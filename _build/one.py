"""Render a single demo to demos/<slug>.html for testing: python3 _build/one.py <slug>"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build
slug = sys.argv[1]
d = next(d for d in build.DEMOS if d[0] == slug)
os.makedirs(os.path.join(build.ROOT, 'demos'), exist_ok=True)
with open(os.path.join(build.ROOT, 'demos', slug + '.html'), 'w', encoding='utf-8') as f:
    f.write(build.demo_page(d))
print('ok', slug)
