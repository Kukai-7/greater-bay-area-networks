"""Build the Greater Bay Area networks dataset from raw/bundle.json (Wikipedia tables compiled from the Guangdong Statistical
Yearbook and port and airport statistics, World Bank) plus curated tables: R&D by city, links and companies."""
import json, os, re, numpy as np, pandas as pd

RAW, OUT = 'raw', 'out/data'
os.makedirs(OUT, exist_ok=True)
B = json.load(open(f'{RAW}/bundle.json'))
num = lambda s: float(re.sub(r'[^\d.\-]', '', s)) if s and re.sub(r'[^\d.\-]', '', s) not in ('', '-', '.') else np.nan

# ------------------------------------------------------------------ the eleven cities
C = [  # name, Chinese, kind, latitude, longitude (city centre)
    ('Guangzhou', '广州', 'Provincial capital', 23.129, 113.264), ('Shenzhen', '深圳', 'Special Economic Zone', 22.543, 114.058),
    ('Hong Kong', '香港', 'Special Administrative Region', 22.302, 114.177), ('Foshan', '佛山', 'Prefecture-level city', 23.022, 113.122),
    ('Dongguan', '东莞', 'Prefecture-level city', 23.021, 113.752), ('Huizhou', '惠州', 'Prefecture-level city', 23.111, 114.416),
    ('Zhuhai', '珠海', 'Special Economic Zone', 22.271, 113.577), ('Zhongshan', '中山', 'Prefecture-level city', 22.517, 113.392),
    ('Jiangmen', '江门', 'Prefecture-level city', 22.579, 113.082), ('Zhaoqing', '肇庆', 'Prefecture-level city', 23.047, 112.465),
    ('Macao', '澳门', 'Special Administrative Region', 22.199, 113.544)]
cities = pd.DataFrame(C, columns=['city', 'city_zh', 'status', 'latitude', 'longitude'])
ZH2EN = dict(zip(cities.city_zh, cities.city)); ZH2EN['澳门'] = 'Macao'

# GDP by city and year, Guangdong Statistical Yearbook via Chinese Wikipedia
rows = []
for t in B['zh_gd_gdp']['tables']:
    year = int(t['title'][:4]); r = t['rows']
    if r[0][0].startswith('行政区'):        # 2015 onwards: two header rows, GDP in 100 million yuan, per head in yuan
        h = r[1]; ipc = 1 + h.index('本币（元）')
        get = lambda row: (num(row[1]), num(row[ipc]))
    else:                                    # 2000 to 2012: one header row; GDP in million or 100 million yuan
        h = r[0]; total = num(r[1][2]); k = 100 if total > 1e6 else 1
        ipc = next(i for i, x in enumerate(h) if x.startswith('人均') and ('本币' in x or x == '人均(本币)'))
        get = lambda row, k=k, ipc=ipc: (num(row[2]) / k, num(row[ipc]))
    for row in r:
        name = row[0].replace('市', '')
        if name not in ZH2EN or name in ('香港', '澳门'): continue
        gdp, pc = get(row); rows.append((ZH2EN[name], year, gdp, pc))
gy = pd.DataFrame(rows, columns=['city', 'year', 'gdp_cny_100m', 'gdp_per_capita_cny']).drop_duplicates(['city', 'year']).sort_values(['city', 'year']).reset_index(drop=True)
gy['source'] = 'Guangdong Statistical Yearbook and city statistical bulletins, via Chinese Wikipedia'
gy.to_parquet(f'{OUT}/city_gdp_by_year.parquet', index=False)

# population at the end of 2024 (10,000 people), city statistical bulletins via Chinese Wikipedia
pop = {ZH2EN[r[0]]: num(r[1]) for r in B['zh_gba_pop']['table'][1:] if r[0] in ZH2EN}
cities['population_2024_10k'] = cities.city.map(pop)
g24 = gy[gy.year == 2024].set_index('city')
FX24 = 7.1217      # yuan per dollar, 2024 central parity, the rate used by the Guangdong yearbook
wb = {(c, y): v for c, y, v in B['wb_NY.GDP.MKTP.CD']}
gdp_usd = {c: wb[(iso, 2024)] / 1e9 for c, iso in [('Hong Kong', 'HKG'), ('Macao', 'MAC')]}
cities['gdp_2024_cny_100m'] = cities.city.map(lambda c: g24.gdp_cny_100m.get(c, np.nan) if c in g24.index else gdp_usd[c] * 1e9 * FX24 / 1e8).round(1)
cities['gdp_2024_usd_bn'] = (cities.gdp_2024_cny_100m * 1e8 / FX24 / 1e9).round(1)
cities['gdp_per_capita_2024_cny'] = cities.apply(lambda r: g24.gdp_per_capita_cny.get(r.city) if r.city in g24.index else
                                                round(r.gdp_2024_cny_100m * 1e8 / (r.population_2024_10k * 1e4)), axis=1)
cities['gdp_source'] = np.where(cities.city.isin(['Hong Kong', 'Macao']), 'World Bank, US dollars converted at 7.1217 yuan', 'Guangdong Statistical Yearbook 2025')
g15 = gy[gy.year == 2015].set_index('city').gdp_cny_100m
cities['gdp_nominal_cagr_2015_2024_pct'] = cities.city.map(lambda c: round(((g24.gdp_cny_100m[c] / g15[c]) ** (1 / 9) - 1) * 100, 2) if c in g15.index else np.nan)

# R&D, 2024: Guangdong statistical bulletin on science and technology spending (24 November 2025); cities above 10 billion yuan
RD = {'Shenzhen': (2453.07, 6.67), 'Guangzhou': (1022.32, 3.29), 'Dongguan': (492.11, 4.01), 'Foshan': (298.27, None),
      'Zhuhai': (204.55, 4.57), 'Huizhou': (186.98, 3.05), 'Zhongshan': (124.10, 3.00)}
cities['rd_2024_cny_100m'] = cities.city.map(lambda c: RD[c][0] if c in RD else np.nan)
cities['rd_intensity_2024_pct'] = cities.city.map(lambda c: RD[c][1] if c in RD and RD[c][1] else np.nan)
fo = cities.city == 'Foshan'
cities.loc[fo, 'rd_intensity_2024_pct'] = round(298.27 / cities.loc[fo, 'gdp_2024_cny_100m'].iloc[0] * 100, 2)
cities['rd_intensity_note'] = np.where(fo, 'computed here from R&D spending and GDP', np.where(cities.rd_2024_cny_100m.notna(), 'published', 'not published at city level in this source'))

# ------------------------------------------------------------------ ports, container throughput (thousand TEU), Lloyd's List via Wikipedia
pt = B['en_ports']['table']; years = [int(y) for y in pt[0][5:]]
ports = pd.DataFrame([(r[1], y, num(v)) for r in pt[1:] for y, v in zip(years, r[5:])], columns=['port', 'year', 'teu_thousand']).dropna()
ports['note'] = ''
# The 2023 column of the Wikipedia table gives terminal-operator figures for Shenzhen and Guangzhou (26.9 and 20.8 million), not whole-port
# totals; they are replaced by the port totals published by the cities (Guangzhou 25.41 million; Shenzhen 29.88 million, consistent with
# the 33.4 million of 2024 being up 11.8%).
for p, v in [('Shenzhen', 29880), ('Guangzhou', 25410)]:
    m = (ports.port == p) & (ports.year == 2023); ports.loc[m, 'teu_thousand'] = v; ports.loc[m, 'note'] = 'whole-port total from city sources, replaces the Wikipedia value'
ports['in_gba'] = ports.port.isin(['Shenzhen', 'Guangzhou', 'Hong Kong'])
ports = ports.sort_values(['port', 'year']).reset_index(drop=True)
ports.to_parquet(f'{OUT}/ports.parquet', index=False)

# ------------------------------------------------------------------ airports
AIR = {'CAN': ('Guangzhou Baiyun', 'Guangzhou', 23.392, 113.299), 'SZX': ("Shenzhen Bao'an", 'Shenzhen', 22.639, 113.811),
       'ZUH': ('Zhuhai Jinwan', 'Zhuhai', 22.006, 113.376), 'HUZ': ('Huizhou Pingtan', 'Huizhou', 23.050, 114.600),
       'FUO': ('Foshan Shadi', 'Foshan', 23.083, 113.070), 'HKG': ('Hong Kong International', 'Hong Kong', 22.308, 113.918),
       'MFM': ('Macau International', 'Macao', 22.149, 113.592)}
ar = []
for t in B['en_airports_cn']['tables']:
    m = re.search(r'in (\d{4})', t['title']); y = int(m.group(1)) if m else 2025
    for r in t['rows'][1:]:
        code = r[4][:3]
        if code in AIR: ar.append((code, y, num(r[5]), num(r[7])))
ar = pd.DataFrame(ar, columns=['iata', 'year', 'passengers', 'cargo_tonnes'])
# Hong Kong: Airport Authority (53.1 million passengers in 2024) and ACI (cargo); Macao: CAM, airport operator, via Wikipedia
extra = pd.DataFrame([('HKG', 2024, 53.1e6, 4938211), ('HKG', 2025, np.nan, 5070256), ('MFM', 2024, 7641495, 108105.209)], columns=ar.columns)
air = pd.concat([ar, extra]).drop_duplicates(['iata', 'year'], keep='last')
air['airport'] = air.iata.map(lambda c: AIR[c][0]); air['city'] = air.iata.map(lambda c: AIR[c][1])
air['latitude'] = air.iata.map(lambda c: AIR[c][2]); air['longitude'] = air.iata.map(lambda c: AIR[c][3])
air = air[['iata', 'airport', 'city', 'year', 'passengers', 'cargo_tonnes', 'latitude', 'longitude']].sort_values(['iata', 'year']).reset_index(drop=True)
air.to_parquet(f'{OUT}/airports.parquet', index=False)

# city-level logistics in 2024
teu24 = ports[ports.year == 2024].set_index('port').teu_thousand
cities['container_teu_2024_thousand'] = cities.city.map(teu24)
a24 = air[air.year == 2024].groupby('city')[['passengers', 'cargo_tonnes']].sum(min_count=1)
cities['airport_passengers_2024'] = cities.city.map(a24.passengers)
cities['airport_cargo_2024_tonnes'] = cities.city.map(a24.cargo_tonnes)

# ------------------------------------------------------------------ links between the cities (curated; first opening to traffic or launch)
L = [('Kowloon-Canton Railway', '广九铁路', 'Rail', 'Guangzhou', 'Hong Kong', 1911, 'Via Dongguan and Shenzhen'),
     ('Humen Bridge', '虎门大桥', 'Road', 'Guangzhou', 'Dongguan', 1997, 'First fixed crossing of the Pearl River estuary'),
     ('Shenzhen Bay Bridge', '深圳湾大桥', 'Road', 'Shenzhen', 'Hong Kong', 2007, 'With a joint checkpoint'),
     ('Guangfo Metro', '广佛地铁', 'Rail', 'Guangzhou', 'Foshan', 2010, 'First metro line between two Chinese cities'),
     ('Guangzhou-Zhuhai Intercity Railway', '广珠城际', 'Rail', 'Guangzhou', 'Zhuhai', 2011, 'Via Zhongshan'),
     ('Xiamen-Shenzhen Railway', '厦深铁路', 'Rail', 'Shenzhen', 'Huizhou', 2013, 'High-speed line along the east coast'),
     ('Guiyang-Guangzhou High-Speed Railway', '贵广高铁', 'Rail', 'Guangzhou', 'Zhaoqing', 2014, 'Links the bay to the south-west'),
     ('Shenzhen-Hong Kong Stock Connect', '深港通', 'Finance', 'Shenzhen', 'Hong Kong', 2016, 'Cross-border trading of listed shares'),
     ('Express Rail Link, Hong Kong section', '广深港高铁香港段', 'Rail', 'Shenzhen', 'Hong Kong', 2018, 'Hong Kong joins the national high-speed network'),
     ('Hong Kong-Zhuhai-Macao Bridge', '港珠澳大桥', 'Road', 'Hong Kong', 'Zhuhai', 2018, 'About 55 km of bridges and tunnel; also serves Macao'),
     ('Hong Kong-Zhuhai-Macao Bridge, Macao link', '港珠澳大桥', 'Road', 'Zhuhai', 'Macao', 2018, 'Same bridge, Macao landing'),
     ('Nansha Bridge', '南沙大桥', 'Road', 'Guangzhou', 'Dongguan', 2019, 'Second crossing next to Humen'),
     ('Wealth Management Connect', '跨境理财通', 'Finance', 'Hong Kong and Macao', 'nine mainland cities', 2021, 'Cross-border sale of investment products to residents'),
     ('Hengqin Cooperation Zone', '横琴粤澳深度合作区', 'Policy zone', 'Zhuhai', 'Macao', 2021, 'Jointly run by Guangdong and Macao'),
     ('Qianhai Cooperation Zone, enlarged', '前海深港现代服务业合作区', 'Policy zone', 'Shenzhen', 'Hong Kong', 2021, 'First set up in 2010'),
     ('Nansha plan', '南沙方案', 'Policy zone', 'Guangzhou', 'Hong Kong', 2022, 'Opening of Nansha to Hong Kong and Macao'),
     ('Hetao Innovation Cooperation Zone', '河套深港科技创新合作区', 'Policy zone', 'Shenzhen', 'Hong Kong', 2023, 'Science and technology zone on the border'),
     ('Shenzhen-Zhongshan Link', '深中通道', 'Road', 'Shenzhen', 'Zhongshan', 2024, 'About 24 km of bridges and an undersea tunnel'),
     ('Huangmaohai Link', '黄茅海跨海通道', 'Road', 'Zhuhai', 'Jiangmen', 2024, 'About 31 km, 14 km over the sea')]
links = pd.DataFrame(L, columns=['link', 'link_zh', 'kind', 'from_city', 'to_city', 'year_opened', 'note'])
links.to_parquet(f'{OUT}/links.parquet', index=False)

# ------------------------------------------------------------------ companies and institutions (curated; headquarters city)
K = [('Shenzhen', 'Huawei', '华为', 1987, 'ICT and chips'), ('Shenzhen', 'Tencent', '腾讯', 1998, 'Software and AI'), ('Shenzhen', 'BYD', '比亚迪', 1995, 'Vehicles and batteries'),
     ('Shenzhen', 'DJI', '大疆', 2006, 'Devices and robots'), ('Shenzhen', 'ZTE', '中兴', 1985, 'ICT and chips'), ('Shenzhen', 'Mindray', '迈瑞', 1991, 'Devices and robots'),
     ('Shenzhen', 'Inovance', '汇川技术', 2003, 'Devices and robots'), ('Shenzhen', 'UBTech', '优必选', 2012, 'Devices and robots'),
     ('Shenzhen', 'Foxconn Industrial Internet', '工业富联', 2015, 'ICT and chips'), ('Shenzhen', 'Ping An', '中国平安', 1988, 'Finance'),
     ('Shenzhen', 'China Merchants Bank', '招商银行', 1987, 'Finance'), ('Shenzhen', 'Shenzhen Stock Exchange', '深圳证券交易所', 1990, 'Finance'),
     ('Shenzhen', 'SF Express', '顺丰', 1993, 'Logistics'),
     ('Guangzhou', 'XPeng', '小鹏汽车', 2014, 'Vehicles and batteries'), ('Guangzhou', 'Pony.ai', '小马智行', 2016, 'Software and AI'),
     ('Guangzhou', 'WeRide', '文远知行', 2017, 'Software and AI'), ('Guangzhou', 'CloudWalk', '云从科技', 2015, 'Software and AI'),
     ('Guangzhou', 'Guangzhou Futures Exchange', '广州期货交易所', 2021, 'Finance'),
     ('Hong Kong', 'HKEX', '香港交易所', 2000, 'Finance'), ('Hong Kong', 'AIA', '友邦保险', 1919, 'Finance'), ('Hong Kong', 'SenseTime', '商汤科技', 2014, 'Software and AI'),
     ('Hong Kong', 'Cathay Pacific', '国泰航空', 1946, 'Logistics'), ('Hong Kong', 'Hong Kong Science and Technology Parks', '香港科技园', 2001, 'Software and AI'),
     ('Foshan', 'Midea', '美的', 1968, 'Devices and robots'), ('Dongguan', 'OPPO', 'OPPO', 2004, 'ICT and chips'), ('Dongguan', 'vivo', 'vivo', 2009, 'ICT and chips'),
     ('Huizhou', 'TCL', 'TCL', 1981, 'ICT and chips'), ('Huizhou', 'Desay SV', '德赛西威', 1986, 'Vehicles and batteries'), ('Huizhou', 'EVE Energy', '亿纬锂能', 2001, 'Vehicles and batteries'),
     ('Zhuhai', 'Gree', '格力电器', 1991, 'Devices and robots'), ('Zhongshan', 'MingYang Smart Energy', '明阳智能', 2006, 'Devices and robots'),
     ('Macao', 'Air Macau', '澳门航空', 1994, 'Logistics')]
co = pd.DataFrame(K, columns=['city', 'name', 'name_zh', 'founded', 'segment'])
co.to_parquet(f'{OUT}/companies.parquet', index=False)
cities['companies_listed'] = cities.city.map(co.city.value_counts()).fillna(0).astype(int)
cities.to_parquet(f'{OUT}/cities.parquet', index=False)

tot = cities.gdp_2024_cny_100m.sum()
stats = dict(gba_gdp_2024_cny_trn=round(tot / 1e4, 2), gba_pop_2024_m=round(cities.population_2024_10k.sum() / 100, 1),
             top3_gdp_share=round(cities.nlargest(3, 'gdp_2024_cny_100m').gdp_2024_cny_100m.sum() / tot * 100, 1),
             teu_2024_m=round(teu24[['Shenzhen', 'Guangzhou', 'Hong Kong']].sum() / 1e3, 1))
json.dump(stats, open('out/stats.json', 'w'), indent=1); print(stats)
