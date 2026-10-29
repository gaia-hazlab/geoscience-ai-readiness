"""Run self-contained suites; never invoke acquisition/semantic clients."""
from pathlib import Path
import os
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
def main():
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PYTHONPATH'] = os.pathsep.join(str(ROOT / p) for p in ('src', 'tools'))
    for suite in ('tests', 'tools/ai_readiness/tests', 'standalone/tests'):
        print('Checking ' + suite, flush=True)
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover',
                                 '-s', str(ROOT / suite), '-v'], cwd=ROOT, env=env)
        if result.returncode:
            return result.returncode
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
