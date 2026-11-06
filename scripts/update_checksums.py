"""Rewrite SHA256SUMS.txt from tracked and new unignored files. Offline; run only after reviewing the changes."""
from pathlib import Path
import hashlib
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    listed = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT).decode().split('\0')
    files = sorted({p for p in listed if p and p != 'SHA256SUMS.txt' and (ROOT / p).is_file()})
    lines = [f"{hashlib.sha256((ROOT / p).read_bytes()).hexdigest()}  {p}\n" for p in files]
    (ROOT / 'SHA256SUMS.txt').write_text(''.join(lines))
    print(f'Wrote {len(lines)} checksums.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
