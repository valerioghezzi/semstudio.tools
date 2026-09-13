from pathlib import Path

files = [Path('dsem.html'), Path('power.html'), Path('multilevel.html')]
old = '(a[i].txt ? "<q>" + esc(a[i].txt) + "</q> &#8212; " : "") + (a[i].say ? a[i].say : esc(a[i].txt || ""))'
new = '(a[i].say && a[i].txt ? "<q>" + esc(a[i].txt) + "</q> &#8212; " : "") + (a[i].say ? a[i].say : esc(a[i].txt || ""))'

for path in files:
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected 1 target expression, found {count}')
    path.write_text(text.replace(old, new), encoding='utf-8')
    print(f'fixed {path}')
