"""Compact scenarios_built.json into the JSON blob embedded in the game page (build/game.html)."""
import json, sys, pathlib
here = pathlib.Path(__file__).parent
built = json.load(open(here / 'scenarios_built.json'))
# Six options per round: five storyline assets + the fixed deposit. The Nifty is no longer always present,
# and one asset per scenario is dropped so stocks, metals and currency stay balanced.
DROP = {'y2k': 'USD', 'supercycle': 'ALUMINIUM', 'openroad': 'USD', 'boombust': 'BRENT', 'ipo': 'USD', 'telecom': 'USD', 'scams': 'GOLD',
        'credit': 'BRENT', 'banks': 'EUR', 'premium': 'BRENT', 'taper': 'GOLD', 'goldrush': 'PLATINUM', 'pharma': 'EUR', 'power': 'NATGAS',
        'jio': 'USD', 'smallcap': 'GOLD', 'pandemic': 'BRENT', 'defence': 'BRENT'}
out = {'generated': '2026-11-11', 'scenarios': []}
for sc in built:
    out['scenarios'].append({
        'id': sc['id'], 'title': sc['title'], 'story': sc['story'], 'headlines': sc['headlines'],
        'dates': sc['dates'], 'labels': sc['labels'],
        'options': [{'id': o['id'], 'name': o['name'], 'type': o['type'], 'desc': o['desc'], 'unit': o['unit'],
                     'prices': [float(f'{v:.6g}') for v in o['prices']], 'src': o['priceDates']}
                    for o in sc['options'] if o['type'] != 'index' and o['id'] != DROP[sc['id']]]})
for s in out['scenarios']:
    assert len(s['options']) == 6 and s['options'][-1]['id'] == 'FD', s['id']
blob = json.dumps(out, separators=(',', ':'), ensure_ascii=False)
tpl = (here.parent / 'src' / 'template.html').read_text()
assert '/*__DATA__*/null' in tpl
(here.parent / 'build').mkdir(exist_ok=True)
(here.parent / 'build' / 'game.html').write_text(tpl.replace('/*__DATA__*/null', blob))
print('build/game.html written,', len(blob), 'bytes of data')
