#!/usr/bin/env python3
from docx import Document
from pathlib import Path
import sys

infile = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('docs/Диплом - правки_исправлено_final6_fixed.docx')
outfile = Path(sys.argv[2]) if len(sys.argv) > 2 else infile.with_name(infile.stem + '_lists.docx')

print('Loading', infile)
doc = Document(str(infile))
changed = 0
for p in doc.paragraphs:
    text = p.text
    if not text or not text.strip():
        continue
    stripped = text.lstrip()
    # detect leading dash or numeric marker
    is_marker = False
    new_text = stripped
    if stripped[0] in '-–—':
        is_marker = True
        new_text = stripped[1:].lstrip()
    else:
        first = stripped.split(None, 1)[0]
        if first.rstrip('.').isdigit():
            is_marker = True
            parts = stripped.split(None, 1)
            new_text = parts[1] if len(parts) > 1 else ''
    if is_marker:
        try:
            p.text = new_text
            # try common list style names (English and Russian)
            for style_name in ('List Bullet', 'List Bullet 2', 'List Number', 'Список с маркерами', 'Маркированный список', 'Нумерованный'):
                try:
                    p.style = style_name
                    break
                except Exception:
                    continue
            changed += 1
        except Exception as e:
            print('Failed to convert paragraph:', e)

print('Converted', changed, 'paragraphs')
doc.save(str(outfile))
print('Saved to', outfile)
