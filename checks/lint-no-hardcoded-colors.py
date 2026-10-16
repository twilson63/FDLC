#!/usr/bin/env python3
"""Fail if component source contains raw color literals.
Usage: lint-no-hardcoded-colors.py <file-or-dir> [...]
Exit 0 = clean, 1 = violations found, 2 = bad input."""
import re, sys, pathlib

HEX = re.compile(r'#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\\b')
FUNC = re.compile(r'\\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\\s*\\(', re.I)
NAMED = re.compile(r'(?<!\\w-)(?:red|blue|green|black|white|gray|grey|orange|purple|yellow)(?!\\w-)', re.I)
EXTS = {'.css', '.scss', '.tsx', '.jsx', '.ts', '.js', '.vue', '.html'}

def scan(path):
    hits = []
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        code = line.split('//')[0] if path.suffix in {'.ts','.tsx','.js','.jsx'} else line
        if HEX.search(code) or FUNC.search(code):
            hits.append((n, line.strip()))
        elif NAMED.search(code) and re.search(r'(color|background|border|fill|stroke)\\s*:', code, re.I):
            hits.append((n, line.strip()))
    return hits

def main(argv):
    if not argv:
        print('usage: lint-no-hardcoded-colors.py <file-or-dir> [...]', file=sys.stderr); return 2
    files = []
    for a in argv:
        p = pathlib.Path(a)
        if not p.exists():
            print(f'bad input: {a} does not exist', file=sys.stderr); return 2
        files += [f for f in p.rglob('*') if f.suffix in EXTS] if p.is_dir() else [p]
    failed = 0
    for f in files:
        for n, text in scan(f):
            failed += 1
            print(f'FAIL {f}:{n}: {text}')
    print(f'{len(files)} file(s) checked, {failed} violation(s)')
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
