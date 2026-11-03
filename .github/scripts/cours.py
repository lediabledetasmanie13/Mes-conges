"""Récupère les cours (Yahoo Finance, différés) des valeurs de bourse/valeurs.json -> bourse/cours.json"""
import json, urllib.request, urllib.parse, datetime, time

valeurs = json.load(open('bourse/valeurs.json', encoding='utf-8'))
try:
    ancien = {c['symbole']: c for c in json.load(open('bourse/cours.json', encoding='utf-8'))['cours']}
except Exception:
    ancien = {}

def lire(symbole):
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + urllib.parse.quote(symbole) + '?range=1mo&interval=1d'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) BoursiScroller/2026'})
    with urllib.request.urlopen(req, timeout=15) as r:
        res = json.load(r)['chart']['result'][0]
    m = res['meta']
    closes = [c for c in res['indicators']['quote'][0]['close'] if c is not None]
    return {
        'prix': m['regularMarketPrice'],
        'veille': m.get('previousClose') or (closes[-2] if len(closes) > 1 else m.get('chartPreviousClose')),
        'devise': m.get('currency', ''),
        'heure': m.get('regularMarketTime'),
        'historique': [round(c, 2) for c in closes[-22:]],
    }

sortie = []
for v in valeurs:
    c = dict(v)
    try:
        c.update(lire(v['symbole']))
        c['ok'] = True
    except Exception as e:
        print('erreur', v['symbole'], e)
        c.update({k: ancien.get(v['symbole'], {}).get(k) for k in ('prix', 'veille', 'devise', 'heure', 'historique')})
        c['ok'] = False
    sortie.append(c)
    time.sleep(1)

json.dump({'maj': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'), 'cours': sortie},
          open('bourse/cours.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok', [(c['nom'], c.get('prix')) for c in sortie])
