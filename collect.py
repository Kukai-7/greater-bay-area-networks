"""Download the raw inputs used by build.py into raw/ (Wikipedia tables at pinned revisions, World Bank API, Natural Earth). No key needed."""
import json, os, re, requests
import lxml.html
from shapely.geometry import shape, mapping, box

NE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'


def wiki(lang, revision):
    """All wikitables of one pinned revision: the text just before each table, and its cells, footnote markers removed."""
    r = requests.get(f'https://{lang}.wikipedia.org/w/api.php', params=dict(action='parse', oldid=revision, prop='text|revid', format='json', formatversion=2,
                                                                            **({'variant': 'zh-cn'} if lang == 'zh' else {})), timeout=60).json()['parse']
    doc = lxml.html.fromstring(r['text'])
    for sup in doc.xpath('//sup'): sup.drop_tree()
    out = []
    for t in doc.xpath('//table[contains(concat(" ", @class, " "), " wikitable ")]'):
        prev = t.getprevious()
        rows = [[re.sub(r'\s+', ' ', c.text_content()).strip() for c in tr.xpath('./th|./td')] for tr in t.xpath('.//tr')]
        out.append({'title': (prev.text_content().strip()[:60] if prev is not None else ''), 'rows': rows})
    return r['revid'], out


def wb(countries, ind):
    j = requests.get(f'https://api.worldbank.org/v2/country/{countries}/indicator/{ind}?format=json&per_page=4000&date=1990:2026', timeout=60).json()
    return [[r['countryiso3code'], int(r['date']), float(f"{float(r['value']):.6g}")] for r in (j[1] or []) if r['value'] is not None]


if __name__ == '__main__':
    os.makedirs('raw', exist_ok=True)
    B = {}
    rev, t = wiki('zh', 91319080); B['zh_gd_gdp'] = {'rev': rev, 'tables': t}                      # 广东各地级市地区生产总值列表
    rev, t = wiki('zh', 94965331); B['zh_gba_pop'] = {'rev': rev, 'table': t[0]['rows']}           # 粤港澳大湾区, population at end 2024
    keep = lambda r, pat: re.search(pat, ' '.join(r)) is not None
    rev, t = wiki('en', 1381656045)                                                                  # List of busiest container ports
    B['en_ports'] = {'rev': rev, 'table': [r for i, r in enumerate(t[1]['rows']) if i == 0 or keep(r[1:2], 'Shenzhen|Guangzhou|Hong Kong|Dongguan|Zhuhai|Foshan|Shanghai|Singapore|Ningbo')]}
    rev, t = wiki('en', 1356827047)                                                                  # List of the busiest airports in China
    B['en_airports_cn'] = {'rev': rev, 'tables': [{'title': x['title'], 'rows': [r for i, r in enumerate(x['rows']) if i == 0 or keep(r, 'Guangzhou|Shenzhen|Zhuhai|Huizhou|Foshan|Shanghai Pudong')]} for x in t]}
    for ind in ['NY.GDP.MKTP.CD', 'SP.POP.TOTL', 'NY.GDP.PCAP.CD', 'PA.NUS.FCRF']:
        B[f'wb_{ind}'] = wb('HKG;MAC;CHN', ind)
    json.dump(B, open('raw/bundle.json', 'w'), ensure_ascii=False)
    # base map: Guangdong, Hong Kong, Macao and neighbouring provinces, clipped to the bay
    a1 = requests.get(NE + 'ne_10m_admin_1_states_provinces.geojson', timeout=300).json()
    clip = box(110.8, 20.8, 116.6, 25.2); feats = []
    for f in a1['features']:
        p = f['properties']; g = shape(f['geometry'])
        if p['adm0_a3'] in ('CHN', 'HKG', 'MAC') and g.intersects(clip):
            feats.append(dict(type='Feature', properties=dict(name=p['name'], adm0=p['adm0_a3']), geometry=mapping(g.intersection(clip).simplify(.003, preserve_topology=True))))
    json.dump(dict(type='FeatureCollection', features=feats), open('raw/gba_admin1.geojson', 'w'))
