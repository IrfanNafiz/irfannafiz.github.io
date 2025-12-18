import re
from pathlib import Path

from PyPDF2 import PdfReader

PDF = Path('data/CV_IrfanNafizShahan.pdf')
OUT_DIR = Path('outputs')
OUT_DIR.mkdir(exist_ok=True)

reader = PdfReader(str(PDF))
text_pages = []
for i, page in enumerate(reader.pages):
    t = page.extract_text() or ''
    text_pages.append(t)
full_text = '\n'.join(text_pages)

# Save raw extracted text
(OUT_DIR / 'cv_text.txt').write_text(full_text, encoding='utf-8')

# Heuristic: look for lines that look like project titles
lines = [l.strip() for l in full_text.splitlines() if l.strip()]

candidates = []
for i, line in enumerate(lines):
    # candidate title: length between 5 and 120, has two or more words, and contains Title Case or keywords
    words = line.split()
    if 2 <= len(words) <= 12 and 5 <= len(line) <= 120:
        # avoid lines that look like headers (CONTACT, EDUCATION)
        if line.upper() == line and len(line) < 30:
            continue
        # keywords commonly in project titles
        if any(k.lower() in line.lower() for k in ['project','vr','simulation','braille','lidar','sat','satellite','tiny','trash','recycler','sustsat','rfid','ibraille','perseverance','icarus','carla','snow','iqa']):
            snippet = ' '.join(lines[i+1:i+4])
            candidates.append({'title': line, 'snippet': snippet})

# Fallback: also look for bold-like patterns where a line is followed by a descriptive line
for i in range(len(lines)-1):
    a, b = lines[i], lines[i+1]
    if len(a) < 100 and len(b) > 30 and len(a.split()) <= 8:
        # likely a title + description
        if any(ch.isupper() for ch in a[0:1]):
            candidates.append({'title': a, 'snippet': b})

# Deduplicate preserving order
seen = set()
unique = []
for c in candidates:
    t = c['title']
    if t not in seen:
        seen.add(t)
        unique.append(c)

import json
(OUT_DIR / 'cv_projects.json').write_text(json.dumps(unique, indent=2, ensure_ascii=False), encoding='utf-8')
print('Wrote outputs/cv_text.txt and outputs/cv_projects.json with', len(unique), 'candidates')
print('\nTop candidates:')
for c in unique[:30]:
    print('- ', c['title'])
    print('   ', c['snippet'][:200])

