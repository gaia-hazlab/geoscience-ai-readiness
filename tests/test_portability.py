"""Test packaged input portability and preservation of the symbolic figures."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from aidatasets_figures import conceptual, das_activity, rendering

ROOT = Path(__file__).resolve().parents[1]


class PortabilityTests(unittest.TestCase):
    def test_distributed_snapshot_copies_are_identical(self):
        source = ROOT / 'data/openalex/2026-10-21'
        packaged = Path(das_activity.__file__).parent / 'snapshots/2026-10-21'
        for name in ('manifest.json', das_activity.NUMERATOR_FILE, das_activity.DENOMINATOR_FILE):
            self.assertEqual((source / name).read_bytes(), (packaged / name).read_bytes())
        self.assertEqual(das_activity.load_snapshot(packaged)['rows'][-1]['das_articles_reviews'], 424)

    def test_conceptual_import_does_not_create_files_or_run_processes(self):
        with mock.patch.object(Path, 'write_text', side_effect=AssertionError('write')), \
             mock.patch.object(Path, 'write_bytes', side_effect=AssertionError('write')), \
             mock.patch('subprocess.run', side_effect=AssertionError('process')):
            importlib.reload(conceptual)

    def test_symbolic_content_and_vector_exports(self):
        with tempfile.TemporaryDirectory() as td:
            # Raster production is checked by the real CLI test below.
            with mock.patch('aidatasets_figures.vector_drawing.render_png'):
                manifest = conceptual.build(td)
            self.assertEqual(len(manifest), 2)
            for figure in manifest:
                self.assertEqual(figure['png_pixels'], [1950, 990])
                stem = Path(td) / figure['basename']
                self.assertTrue(stem.with_suffix('.pdf').read_bytes().startswith(b'%PDF-'))
                svg = stem.with_suffix('.svg').read_text()
                caption = Path(str(stem) + '_caption.txt').read_text()
                self.assertIn('CONCEPTUAL DRAFT', svg)
                self.assertTrue('not a measured result' in caption.lower()
                                or 'no empirical outcomes' in caption.lower())

    def test_renderer_reports_missing_poppler_before_command(self):
        with mock.patch('shutil.which', return_value=None):
            with self.assertRaisesRegex(RuntimeError, 'PNG export needs Poppler'):
                rendering.find_pdftoppm()

    def test_cli_from_unrelated_directory(self):
        try:
            rendering.find_pdftoppm()
        except RuntimeError:
            self.skipTest('Poppler not installed; install it to run the rendering check')
        from PIL import Image
        with tempfile.TemporaryDirectory() as td:
            env = dict(os.environ)
            env['PYTHONPATH'] = str(ROOT / 'src')
            env['PYTHONDONTWRITEBYTECODE'] = '1'
            subprocess.run([sys.executable, '-m', 'aidatasets_figures', '--out', 'figures'],
                           cwd=td, env=env, check=True, capture_output=True, text=True)
            out = Path(td) / 'figures'
            receipt = json.loads((out / 'reproduction_receipt.json').read_text())
            self.assertFalse(receipt['network_used'])
            self.assertEqual(len(list(out.glob('*.png'))), 3)
            for figure in receipt['figures']['conceptual']:
                with Image.open(out / (figure['basename'] + '.png')) as image:
                    self.assertEqual(image.size, (1950, 990))


if __name__ == '__main__':
    unittest.main()
