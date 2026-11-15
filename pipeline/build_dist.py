"""Package the game for static hosting.

    python3 pipeline/export_game_data.py          # builds build/game.html (the game page; also what the claude.ai artifact shows)
    python3 pipeline/build_dist.py                # SITE_URL defaults to https://playhindsight.vercel.app

Writes dist/: a complete index.html (doctype, charset, language, description, social preview tags)
plus everything in public/ (favicon, touch icon, og.png, robots.txt, _headers).
dist/ is committed: Vercel serves it as-is (see vercel.json), with no build step on Vercel.
"""
import os
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
SITE = os.environ.get('SITE_URL', 'https://playhindsight.vercel.app').rstrip('/')

page = (ROOT / 'build' / 'game.html').read_text()
cut = page.index('<div class="aura"')            # everything before the first body element is head material
head, body = page[:cut], page[cut:]
assert head.lstrip().startswith('<title>') and '</style>' in head

TITLE = 'Hindsight · Everyone’s a genius in hindsight'
DESC = 'Go back in time with ₹1 lakh and bet on real Indian markets from 2000 to 2026. Would you make it big, or will the classic FD beat you?'
img = f'{SITE}/og.png' if SITE else 'og.png'
meta = f'''<meta charset="utf-8">
<meta name="description" content="{DESC}">
<meta name="theme-color" content="#09090b">
<meta name="color-scheme" content="dark light">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Hindsight">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
{f'<meta property="og:url" content="{SITE}/">' if SITE else ''}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{img}">
'''
head = head.replace('<title>Hindsight</title>', f'<title>{TITLE}</title>', 1)
doc = f'<!doctype html>\n<html lang="en-IN">\n<head>\n{meta}{head}</head>\n<body>\n{body}\n</body>\n</html>\n'

if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir()
(DIST / 'index.html').write_text(doc)
for f in (ROOT / 'public').iterdir():
    shutil.copy(f, DIST / f.name)
print('dist/ ready:', ', '.join(sorted(p.name for p in DIST.iterdir())), f'({len(doc) // 1024} KB page)')
if not SITE:
    print('note: set SITE_URL to your domain so link previews get an absolute og:image URL')
