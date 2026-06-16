#!/usr/bin/env python3
from docx import Document
from pathlib import Path
import sys

infile = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('docs/Диплом - правки_исправлено_final6_lists.docx')
outfile = Path(sys.argv[2]) if len(sys.argv) > 2 else infile.with_name(infile.stem + '_dashes.docx')

print('Loading', infile)
doc = Document(str(infile))
changed = 0
for p in doc.paragraphs:
    style = getattr(p.style, 'name', '') if p.style else ''
    # check if it's a list style
    if any(x in style.lower() for x in ('list', 'марки', 'нумер')):
        text = p.text.strip()
        if text and not text.startswith('—'):
            # prepend em-dash
            p.text = '— ' + text
            changed += 1

print('Converted', changed, 'list paragraphs to em-dashes')
doc.save(str(outfile))
print('Saved to', outfile)
