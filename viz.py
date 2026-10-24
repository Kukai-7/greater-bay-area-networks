import json, os, glob, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly, FancyArrowPatch
from matplotlib.lines import Line2D
from shapely.geometry import shape

for f in glob.glob('fonts/*.otf') + ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']:
    if os.path.exists(f): fm.fontManager.addfont(f)
_n = {f.name for f in fm.fontManager.ttflist}
FONT = next((n for n in ('Noto Sans CJK SC', 'Noto Sans CJK JP') if n in _n), 'DejaVu Sans')
plt.rcParams.update({'font.family': FONT, 'font.size': 10, 'axes.edgecolor': '#BBBBBB', 'axes.linewidth': .6,
                     'xtick.color': '#666666', 'ytick.color': '#666666', 'axes.labelcolor': '#444444', 'text.color': '#1F1F1F',
                     'savefig.dpi': 200})
INK, MID, LIGHT, LAND, PAPER = '#1F1F1F', '#8A8A8A', '#C9C6BF', '#ECE9E3', '#FFFFFF'
RED, RED_SOFT, BLUE, BLUE_SOFT = '#B33A2B', '#E3B5AE', '#2F4B7C', '#B9C4D6'
SEA = '#F6F7F9'
os.makedirs('out/assets', exist_ok=True)

ci = pd.read_parquet('out/data/cities.parquet').set_index('city')
gy = pd.read_parquet('out/data/city_gdp_by_year.parquet')
po = pd.read_parquet('out/data/ports.parquet')
ai = pd.read_parquet('out/data/airports.parquet')
li = pd.read_parquet('out/data/links.parquet')
co = pd.read_parquet('out/data/companies.parquet')
KIND = {'Road': (INK, '-', 1.6), 'Rail': (BLUE, '-', 1.6), 'Finance': (RED, (0, (4, 2)), 1.4), 'Policy zone': (RED_SOFT, (0, (1, 1.5)), 2.2)}

def title(fig, t, s, y=.95):
    fig.text(.05, y, t, fontsize=15, weight='bold')
    fig.text(.05, y - .045, s, fontsize=9, color='#555555')
def clean(ax, left=True):
    for s_ in ('top', 'right'): ax.spines[s_].set_visible(False)
    if not left: ax.spines['left'].set_visible(False)
    ax.tick_params(length=0)

# ------------------------------------------------------------------ 1. map: cities, links, ports and airports
EXT = (112.15, 114.75, 21.85, 23.55)
fig, ax = plt.subplots(figsize=(12, 9.2))
ax.set_facecolor(SEA)
for f in json.load(open('raw/gba_admin1.geojson'))['features']:
    g = shape(f['geometry']); p = f['properties']
    gba = p['name'] == 'Guangdong' or p['adm0'] in ('HKG', 'MAC')
    for q in getattr(g, 'geoms', [g]):
        if q.geom_type == 'Polygon':
            ax.add_patch(MPoly(np.array(q.exterior.coords), closed=True, fc=LAND if gba else '#F2F0EC', ec='#D8D4CC' if p['adm0'] == 'CHN' else '#E4E0D8', lw=.5, zorder=1))
# links, curved slightly so that parallel links stay visible
seen = {}
for _, l in li[li.kind.isin(['Road', 'Rail'])].iterrows():
    a, b = ci.loc[l.from_city], ci.loc[l.to_city]
    key = tuple(sorted((l.from_city, l.to_city))); k = seen.get(key, 0); seen[key] = k + 1
    col, ls, lw = KIND[l.kind]
    rad = [.0, .18, -.18, .32, -.32][k % 5]
    ax.add_patch(FancyArrowPatch((a.longitude, a.latitude), (b.longitude, b.latitude), connectionstyle=f'arc3,rad={rad}', arrowstyle='-',
                                 color=col, lw=lw, ls=ls, alpha=.85, zorder=3))
# cities: circle area proportional to GDP 2024
mx = ci.gdp_2024_cny_100m.max()
for c, r in ci.iterrows():
    s = 2600 * r.gdp_2024_cny_100m / mx
    ax.scatter(r.longitude, r.latitude, s=s, c=RED if r.status == 'Special Administrative Region' else INK, alpha=.18, lw=0, zorder=4)
    ax.scatter(r.longitude, r.latitude, s=18, c=RED if r.status == 'Special Administrative Region' else INK, zorder=6)
OFF = {'Guangzhou': (-10, 10, 'right'), 'Shenzhen': (10, 8, 'left'), 'Hong Kong': (12, -16, 'left'), 'Foshan': (-12, -4, 'right'), 'Dongguan': (10, 10, 'left'),
       'Huizhou': (10, 6, 'left'), 'Zhuhai': (-14, -12, 'right'), 'Zhongshan': (-12, 2, 'right'), 'Jiangmen': (-10, -14, 'right'), 'Zhaoqing': (-8, 10, 'right'), 'Macao': (10, -14, 'left')}
for c, r in ci.iterrows():
    dx, dy, ha = OFF[c]
    ax.annotate(f'{c} {r.city_zh}\n{r.gdp_2024_cny_100m / 1e4:.2f} tn yuan', (r.longitude, r.latitude), xytext=(dx, dy), textcoords='offset points', ha=ha,
                fontsize=8.3, weight='bold', color=RED if r.status == 'Special Administrative Region' else INK, zorder=8, linespacing=1.15,
                bbox=dict(fc=PAPER, ec='none', alpha=.7, pad=1))
# ports and airports in 2024
P = {'Shenzhen': (22.56, 114.27), 'Guangzhou': (22.70, 113.66), 'Hong Kong': (22.345, 114.115)}
for p, (la, lo) in P.items():
    v = po[(po.port == p) & (po.year == 2024)].teu_thousand.iloc[0]
    ax.scatter(lo, la, marker='s', s=v / 220, fc='none', ec=BLUE, lw=1.4, zorder=7)
    ax.annotate(f'port {v / 1e3:.1f} m TEU', (lo, la), xytext=(8, -2), textcoords='offset points', fontsize=7, color=BLUE, zorder=8)
for _, a in ai[(ai.year == 2024) & ai.cargo_tonnes.notna()].iterrows():
    ax.scatter(a.longitude, a.latitude, marker='^', s=max(a.cargo_tonnes / 25000, 12), fc='none', ec=MID, lw=1.1, zorder=7)
    if a.cargo_tonnes > 5e5:
        ax.annotate(f'{a.iata} {a.cargo_tonnes / 1e6:.1f} m t', (a.longitude, a.latitude), xytext=(7, -10), textcoords='offset points', fontsize=7, color=MID, zorder=8)
ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3]); ax.set_aspect(1 / np.cos(np.radians(22.7)))
ax.set_xticks([]); ax.set_yticks([])
for s_ in ax.spines.values(): s_.set_visible(False)
H = [Line2D([], [], color=c, ls=s, lw=w, label=k + ' link') for k, (c, s, w) in KIND.items() if k in ('Road', 'Rail')] + [
    Line2D([], [], marker='o', ls='', color=INK, alpha=.35, ms=12, label='City, area = GDP 2024'),
    Line2D([], [], marker='s', ls='', mfc='none', mec=BLUE, ms=9, label='Container port, area = TEU 2024'),
    Line2D([], [], marker='^', ls='', mfc='none', mec=MID, ms=9, label='Airport, area = cargo 2024')]
ax.legend(handles=H, loc='lower left', frameon=True, facecolor=PAPER, edgecolor='none', fontsize=8, framealpha=.9, ncol=2)
ax.text(114.55, 21.95, 'South China Sea', fontsize=9, color='#9AA3B0', style='italic', ha='right')
title(fig, 'One bay, eleven cities', 'The Greater Bay Area in 2024: output by city, the road and rail links that tie it together, and its ports and airports.', y=.955)
fig.text(.05, .025, 'Data: Guangdong Statistical Yearbook 2025; World Bank (Hong Kong, Macao, converted at 7.1217 yuan per dollar); Lloyd\'s List and CAAC via Wikipedia; '
         'Airports Council International.\nRoad and rail links curated for this dataset (financial links and joint zones: see the timeline). Borders: Natural Earth. Positions are city centres.', fontsize=7, color=MID, linespacing=1.5)
plt.subplots_adjust(left=.02, right=.98, top=.88, bottom=.05)
fig.savefig('out/assets/map_gba_network.png', facecolor=PAPER); plt.close(fig)

# ------------------------------------------------------------------ 2. logistics: ports since 2004, airports since 2000
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.4), gridspec_kw=dict(wspace=.25))
PS = {'Shenzhen': (RED, 2.2), 'Guangzhou': (BLUE, 2), 'Hong Kong': (INK, 2), 'Shanghai': (LIGHT, 1.4), 'Singapore': (LIGHT, 1.4)}
for p, (c, w) in PS.items():
    s = po[po.port == p].set_index('year').teu_thousand / 1e3
    a1.plot(s.index, s, color=c, lw=w)
    a1.annotate(f'{p} {s.iloc[-1]:.1f}', (s.index[-1], s.iloc[-1]), xytext=(4, 0), textcoords='offset points', fontsize=8, color=c if c != LIGHT else MID, va='center')
a1.set_xlim(2004, 2028.5); a1.set_ylabel('Million TEU a year'); clean(a1); a1.yaxis.grid(color='#EEEEEE', lw=.6)
a1.set_title('Container ports: Hong Kong falls back as Shenzhen and Guangzhou rise', fontsize=10, loc='left')
AS = {'HKG': (INK, 'Hong Kong'), 'CAN': (BLUE, 'Guangzhou'), 'SZX': (RED, 'Shenzhen')}
for code, (c, nm) in AS.items():
    s = ai[ai.iata == code].set_index('year').cargo_tonnes.dropna() / 1e6
    if code == 'HKG':
        a2.scatter(s.index, s, color=c, s=28, zorder=3)
        for y, v in s.items(): a2.annotate(f'{v:.2f}', (y, v), xytext=(-4, 6), textcoords='offset points', fontsize=7.5, ha='right', color=c)
    else: a2.plot(s.index, s, color=c, lw=2)
    a2.annotate(nm, (s.index[-1], s.iloc[-1]), xytext=(5, 0), textcoords='offset points', fontsize=8, color=c, va='center')
a2.set_xlim(2000, 2028.5); a2.set_ylim(0, 5.6); a2.set_ylabel('Million tonnes of air cargo a year'); clean(a2); a2.yaxis.grid(color='#EEEEEE', lw=.6)
a2.set_title('Air cargo: Hong Kong is the world\'s busiest; the mainland pair keeps growing', fontsize=10, loc='left')
title(fig, 'The logistics backbone', 'Container throughput of the three bay ports against Shanghai and Singapore, and air cargo at the three main airports.', y=.955)
fig.text(.05, .02, 'Data: Lloyd\'s List One Hundred Ports via Wikipedia (TEU); CAAC airport statistics via Wikipedia (mainland airports); ACI and Airport Authority Hong Kong '
         '(Hong Kong, 2024 and 2025 only in this dataset).', fontsize=7, color=MID)
plt.subplots_adjust(left=.06, right=.97, top=.78, bottom=.1)
fig.savefig('out/assets/logistics.png', facecolor=PAPER); plt.close(fig)

# ------------------------------------------------------------------ 3. economy: output and income by city, and growth since 2000
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.8), gridspec_kw=dict(width_ratios=[1, 1.1], wspace=.32))
d = ci.sort_values('gdp_2024_cny_100m')
cols = [RED if s == 'Special Administrative Region' else INK for s in d.status]
a1.barh(range(len(d)), d.gdp_2024_cny_100m / 1e4, color=cols, height=.62)
for i, (c, r) in enumerate(d.iterrows()):
    a1.text(r.gdp_2024_cny_100m / 1e4 + .05, i, f'{r.gdp_2024_cny_100m / 1e4:.2f}   ({r.gdp_per_capita_2024_cny / 1e3:.0f}k per head)', va='center', fontsize=8)
a1.set_yticks(range(len(d))); a1.set_yticklabels([f'{c} {r.city_zh}' for c, r in d.iterrows()], fontsize=8.5)
a1.set_xlim(0, 5.4); a1.set_xlabel('GDP 2024, trillion yuan'); clean(a1, left=False); a1.xaxis.grid(color='#EEEEEE', lw=.6); a1.set_axisbelow(True)
a1.set_title('Output in 2024, and output per head', fontsize=10, loc='left')
g = gy.pivot(index='year', columns='city', values='gdp_cny_100m'); idx = g / g.loc[2000]
for c in idx.columns:
    hl = c in ('Shenzhen', 'Guangzhou', 'Huizhou', 'Zhuhai')
    a2.plot(idx.index, idx[c], color={'Shenzhen': RED, 'Guangzhou': BLUE, 'Huizhou': INK, 'Zhuhai': MID}.get(c, LIGHT), lw=2 if hl else 1.1, marker='o', ms=2.5)

a2.set_yscale('log'); a2.set_ylim(.9, 22)
last = idx.iloc[-1].sort_values(); ly = np.log10(last.values); pos = []
for v_ in ly: pos.append(max(v_, pos[-1] + .045) if pos else v_)
for (c, v_), p_ in zip(last.items(), pos):
    a2.annotate(f'{c} ×{v_:.1f}', (2024, v_), xytext=(2026, 10 ** p_), textcoords='data', fontsize=7.5, va='center',
                color={'Shenzhen': RED, 'Guangzhou': BLUE, 'Huizhou': INK, 'Zhuhai': MID}.get(c, MID), arrowprops=dict(arrowstyle='-', color=LIGHT, lw=.5))
a2.set_yticks([1, 2, 5, 10, 20]); a2.set_yticklabels(['1', '2', '5', '10', '20']); a2.set_xlim(2000, 2030)
a2.set_ylabel('Nominal GDP, 2000 = 1 (log scale)'); clean(a2); a2.yaxis.grid(color='#EEEEEE', lw=.6)
a2.set_title('Growth since 2000, the nine mainland cities', fontsize=10, loc='left')
title(fig, 'Where the output is', 'Shenzhen, Guangzhou and Hong Kong produce two thirds of the bay\'s GDP. Since 2000 Shenzhen has grown fastest, Jiangmen slowest.', y=.955)
fig.text(.05, .02, 'Data: Guangdong Statistical Yearbook, via Chinese Wikipedia (mainland, current yuan); World Bank (Hong Kong and Macao, US dollars converted at 7.1217). '
         'Nominal values: price changes are not removed.', fontsize=7, color=MID)
plt.subplots_adjust(left=.13, right=.95, top=.78, bottom=.13)
fig.savefig('out/assets/economy.png', facecolor=PAPER); plt.close(fig)

# ------------------------------------------------------------------ 4. innovation and companies
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13.5, 8), gridspec_kw=dict(width_ratios=[1, 1.35], wspace=.3))
d = ci[ci.rd_intensity_2024_pct.notna()].sort_values('rd_intensity_2024_pct')
a1.barh(range(len(d)), d.rd_intensity_2024_pct, color=[RED if c == 'Shenzhen' else INK for c in d.index], height=.6)
for i, (c, r) in enumerate(d.iterrows()):
    a1.text(r.rd_intensity_2024_pct + .08, i, f'{r.rd_intensity_2024_pct:.2f}%  ({r.rd_2024_cny_100m:,.0f} 100m yuan){"*" if r.rd_intensity_note.startswith("computed") else ""}', va='center', fontsize=8)
for v, lab in [(2.69, 'China 2.69%'), (3.6, 'Guangdong 3.6%')]:
    a1.axvline(v, color=MID, lw=.8, ls=(0, (3, 2))); a1.text(v, -.75 if v < 3 else -1.05, lab, fontsize=7.5, color=MID, ha='center', va='top')
a1.set_yticks(range(len(d))); a1.set_yticklabels([f'{c} {r.city_zh}' for c, r in d.iterrows()], fontsize=8.5)
a1.set_xlim(0, 9.5); a1.set_ylim(-1.3, len(d) - .5); a1.set_xlabel('R&D spending, % of GDP, 2024'); clean(a1, left=False)
a1.set_title('Research intensity, seven mainland cities', fontsize=10, loc='left')
SEG = ['Software and AI', 'ICT and chips', 'Devices and robots', 'Vehicles and batteries', 'Finance', 'Logistics']
SEGL = ['Software\nand AI', 'ICT\nand chips', 'Devices\nand robots', 'Vehicles\nand batteries', 'Finance', 'Logistics']
ORD = ['Shenzhen', 'Guangzhou', 'Hong Kong', 'Huizhou', 'Dongguan', 'Foshan', 'Zhuhai', 'Zhongshan', 'Macao']
for i, c in enumerate(ORD):
    for j, s in enumerate(SEG):
        names = co[(co.city == c) & (co.segment == s)].sort_values('founded').name.tolist()
        if names:
            a2.scatter(j, i, s=90 * len(names), color=RED if c in ('Hong Kong', 'Macao') else INK, alpha=.85, zorder=3)
            a2.annotate('\n'.join(names[:3]) + (f'\n+{len(names) - 3}' if len(names) > 3 else ''), (j, i), xytext=(0, -9), textcoords='offset points',
                        ha='center', va='top', fontsize=6.3, color='#444444', linespacing=1.05)
a2.set_xticks(range(len(SEG))); a2.set_xticklabels(SEGL, fontsize=8, rotation=0); a2.xaxis.tick_top()
a2.set_yticks(range(len(ORD))); a2.set_yticklabels(ORD, fontsize=8.5); a2.set_ylim(len(ORD) - .2, -.6); a2.set_xlim(-.6, len(SEG) - .4)
for s_ in a2.spines.values(): s_.set_visible(False)
a2.tick_params(length=0); a2.grid(color='#F2F2F2', lw=.6); a2.set_axisbelow(True)
a2.set_title('Who is headquartered where (selection)', fontsize=10, loc='left', pad=26)
title(fig, 'Research and the companies behind it', 'Shenzhen spends 6.7% of its GDP on R&D. WIPO ranked Shenzhen-Hong Kong-Guangzhou the world\'s first science and technology cluster in 2025.', y=.96)
fig.text(.05, .02, 'Data: Guangdong statistical bulletin on R&D spending 2024 (published 24 November 2025); * Foshan: intensity computed here from R&D and GDP. Jiangmen and Zhaoqing not published '
         'in the source;\nHong Kong and Macao measure R&D differently. Companies: curated selection, not a ranking; circle size grows with the number listed.', fontsize=7, color=MID, linespacing=1.5)
plt.subplots_adjust(left=.1, right=.98, top=.8, bottom=.1)
fig.savefig('out/assets/innovation.png', facecolor=PAPER); plt.close(fig)

# ------------------------------------------------------------------ 5. how the bay was wired: links by year
fig, ax = plt.subplots(figsize=(12.5, 6.8))
d = li.sort_values(['year_opened', 'link']).reset_index(drop=True)
X0 = 1995                                   # links older than 1995 are drawn at the left edge, with their real year
xpos = lambda y: max(y, X0)
for i, r in d.iterrows():
    col, ls, lw = KIND[r.kind]
    ax.hlines(i, X0 - 1, xpos(r.year_opened), color='#F0F0F0', lw=.8, zorder=1)
    ax.scatter(xpos(r.year_opened), i, color=col, s=55, zorder=3, marker='o' if r.kind in ('Road', 'Rail') else 'D')
    ax.text(xpos(r.year_opened) + .5, i, f'{r.year_opened}  {r.from_city} – {r.to_city}', va='center', fontsize=7.5, color=MID)
ax.set_yticks(range(len(d))); ax.set_yticklabels([f'{a}  {b}' for a, b in zip(d.link, d.link_zh)], fontsize=8)
ax.invert_yaxis(); ax.set_xlim(X0 - 1, 2033); ax.set_xticks([1995, 2000, 2005, 2010, 2015, 2020, 2025]); ax.set_xticklabels(['≤1995', '2000', '2005', '2010', '2015', '2020', '2025'])
clean(ax, left=False); ax.xaxis.grid(color='#F2F2F2', lw=.6); ax.set_axisbelow(True)
fig.legend(handles=[Line2D([], [], marker='o' if k in ('Road', 'Rail') else 'D', ls='', color=c, label=k, ms=7) for k, (c, _, _) in KIND.items()],
           loc='upper left', bbox_to_anchor=(.045, .885), frameon=False, fontsize=8.5, ncol=4)
title(fig, 'How the bay was wired', 'Fixed links, financial connections and joint zones, by year of opening. Seventeen of the nineteen date from 2007 or later.', y=.965)
fig.text(.05, .02, 'Curated for this dataset from the articles on each link and official announcements; year of first opening to traffic or launch.', fontsize=7, color=MID)
plt.subplots_adjust(left=.3, right=.98, top=.82, bottom=.08)
fig.savefig('out/assets/links_timeline.png', facecolor=PAPER); plt.close(fig)

print(sorted(os.listdir('out/assets')))
