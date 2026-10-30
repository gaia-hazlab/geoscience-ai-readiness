"""Build local release archives from tracked files; never publish or access APIs."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    version = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']['version']
    out = ROOT / 'dist' / version
    subprocess.run([sys.executable, str(ROOT / 'scripts/verify_release.py')], check=True)
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    tracked = [p for p in tracked if p]
    figures = sorted(p for folder in ('archive_readiness', 'das_semantic')
                     for p in (ROOT / 'build' / folder).glob('*')
                     if p.suffix in ('.png', '.svg', '.pdf'))
    if len(figures) != 33 or len({p.stem for p in figures}) != 11:
        raise SystemExit('Rebuild the report first: expected eleven PNG/SVG/PDF figure sets.')
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f'Release output already exists: {out}. Move it aside before rebuilding.')
    out.mkdir(parents=True, exist_ok=True)
    prefix = f'geoscience_ai_readiness-{version}'
    with tempfile.TemporaryDirectory(prefix='readiness-release-') as temp:
        stage = Path(temp) / prefix
        stage.mkdir()
        for name in tracked:
            source = ROOT / name
            if not source.is_file() or source.is_symlink():
                raise SystemExit(f'Expected a regular tracked file: {name}')
            dest = stage / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        with zipfile.ZipFile(out / f'{prefix}-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for name in tracked:
                archive.write(stage / name, f'{prefix}/{name}')
        # Include the full tracked research toolkit in the sdist, while the wheel
        # retains the package-data rules declared in pyproject.toml.
        (stage / 'MANIFEST.in').write_text('\n'.join(f'include {p}' for p in tracked) + '\n')
        subprocess.run([sys.executable, '-c',
                        'import setuptools.build_meta as b; import sys; '
                        'out = sys.argv[1]; b.build_sdist(out); b.build_wheel(out)', str(out)],
                       cwd=stage, check=True)
    with zipfile.ZipFile(out / f'{prefix}-report-figures.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in figures:
            archive.write(path, str(path.relative_to(ROOT / 'build')))
    if len(list(out.glob('*.whl'))) != 1 or len(list(out.glob('*.tar.gz'))) != 1:
        raise SystemExit('Release build did not produce both a wheel and source distribution.')
    files = sorted(out.iterdir())
    (out / 'SHA256SUMS.txt').write_text(''.join(
        f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in files))
    print(f'Prepared {len(files)} archives and SHA256SUMS.txt in {out}; nothing published.')


if __name__ == '__main__':
    main()
