# Greater Bay Area Networks: Logistics, Manufacturing, AI, Technology and Finance

[Dataset on Hugging Face](https://huggingface.co/datasets/Kukai-7/greater-bay-area-networks) · code in this repository

**How do eleven cities around the Pearl River estuary work as one economy?** This dataset maps the Guangdong–Hong Kong–Macao Greater Bay Area (粤港澳大湾区) through its networks: the ports and airports that move its goods, the bridges, railways and joint zones that tie its cities together, the research and the companies behind its manufacturing and AI, and the financial links between Hong Kong, Macao and the mainland.

*粤港澳大湾区的物流、制造、人工智能、科技与金融网络：十一座城市的公开数据。*

![One bay, eleven cities](https://huggingface.co/datasets/Kukai-7/greater-bay-area-networks/resolve/main/assets/map_gba_network.png)

*Reading the map: grey circles are the nine mainland cities and red ones Hong Kong and Macao, with area proportional to GDP in 2024; black lines are road links, blue lines rail links; blue squares are the three container ports and grey triangles the airports, sized by 2024 throughput.*

## Dataset description

| | |
|---|---|
| Area | Guangzhou, Shenzhen, Zhuhai, Foshan, Huizhou, Dongguan, Zhongshan, Jiangmen and Zhaoqing in Guangdong province; the Hong Kong and Macao Special Administrative Regions |
| Period | City GDP 2000 to 2024; container ports 2004 to 2024; airports 2000 to 2025; links 1911 to 2024 |
| Size | 7 configurations, 11 cities, 19 links, 32 companies and institutions, about 400 rows in all |
| Format | Parquet, with the pipeline in this repository |
| Owner | Kukai-7, independent compilation |
| Created | October 2026, version 1.0 |
| License | CC BY 4.0 for the compilation; sources keep their own terms (see credits) |
| Intended use | Teaching, exploratory analysis, maps and charts of the bay economy; a starting point for city-level research. Not for investment decisions. |

## At a glance

- **An economy of 14.8 trillion yuan and 87.5 million people.** In 2024 the eleven cities produced about 14.8 trillion yuan (2.1 trillion dollars). Shenzhen (3.68), Guangzhou (3.10) and Hong Kong (2.91 trillion yuan) account for 65% of it.
- **A seven-fold gap in income.** Output per head ranges from 71,000 yuan in Zhaoqing to 386,000 in Hong Kong and 512,000 in Macao; Shenzhen stands at 206,000.
- **The ports changed places.** Hong Kong handled 22.0 million containers (TEU) in 2004 and 13.7 million in 2024; Shenzhen went from 13.6 to 33.4 million and Guangzhou from 3.3 to 26.1 million. The three ports together moved 73 million TEU in 2024.
- **The world's busiest cargo airport.** Hong Kong handled 4.94 million tonnes of air cargo in 2024, first in the world; Guangzhou (2.38) and Shenzhen (1.88) rank 9th and 19th.
- **Research is concentrated in Shenzhen.** Shenzhen spent 245 billion yuan on R&D in 2024, 6.67% of its GDP and 48% of Guangdong's total. WIPO ranked the Shenzhen–Hong Kong–Guangzhou cluster first among the world's science and technology clusters in 2025.
- **Most of the wiring is recent.** Seventeen of the nineteen links in the dataset (bridges, railways, financial connections, joint zones) opened in 2007 or later, eleven of them since 2018.
- **Finance across the border.** Hong Kong is third in the Global Financial Centres Index (GFCI 38, September 2025) and Shenzhen in the top ten. By January 2026 the Wealth Management Connect counted 175,000 individual investors and 129.2 billion yuan transferred across the border.

## What it shows

![The logistics backbone](https://huggingface.co/datasets/Kukai-7/greater-bay-area-networks/resolve/main/assets/logistics.png)

*Reading the chart: left, containers handled each year by the three bay ports (coloured) against Shanghai and Singapore (grey), in million TEU; right, air cargo in million tonnes. Hong Kong's port has been shrinking since 2011 while Shenzhen and Guangzhou grew; in the air, Hong Kong remains far ahead.*

![Where the output is](https://huggingface.co/datasets/Kukai-7/greater-bay-area-networks/resolve/main/assets/economy.png)

*Reading the chart: left, GDP in 2024 with output per head in brackets (red: Hong Kong and Macao); right, nominal GDP of the nine mainland cities with 2000 set to 1, on a log scale so that equal slopes mean equal growth rates. Shenzhen multiplied its output by 16.8, Jiangmen by 8.3.*

![Research and the companies behind it](https://huggingface.co/datasets/Kukai-7/greater-bay-area-networks/resolve/main/assets/innovation.png)

*Reading the chart: left, R&D spending as a share of GDP for the seven mainland cities that publish it, against the national (2.69%) and Guangdong (3.6%) averages; right, a selection of companies and institutions by headquarters city and segment, larger circles for more entries. Shenzhen leads on both; Hong Kong adds finance and research, the outer cities manufacturing.*

![How the bay was wired](https://huggingface.co/datasets/Kukai-7/greater-bay-area-networks/resolve/main/assets/links_timeline.png)

*Reading the chart: each row is a link, placed at the year it opened (links before 1995 sit at the left edge with their real year); colour gives the kind. Bridges and railways come first, then from 2016 the financial connections and joint zones.*

![Small numbers, wide intervals](https://huggingface.co/datasets/Kukai-7/greater-bay-area-networks/resolve/main/assets/scatter_matrix_cities.png)

*Reading the chart: see "Reading the correlations" below. With seven to eleven cities, no correlation here is distinguishable from chance.*

## Reading the correlations

**How to read r.** Pearson's r measures how closely two variables move along a straight line: +1 is a perfect positive line, 0 no linear link, -1 a perfect negative line. r² is the share of the variance of one variable that a straight line on the other accounts for. The labels used here: under 0.1 negligible, 0.1 to 0.3 weak, 0.3 to 0.5 moderate, 0.5 to 0.7 strong, 0.7 and above very strong.

**How sure is it?** The 95% confidence interval gives the range of r compatible with the data; when it excludes zero, p is below 0.05 and the link is distinguishable from chance. With eleven points or fewer the intervals are very wide: an r of +0.67 on seven cities is compatible with anything from -0.16 to +0.95.

**What stands out**

- **Richer cities spend more on research (r = +0.67, n = 7) and grew faster from 2015 to 2024 (+0.62, n = 9)**, but both intervals include zero. The pattern matches what the 31 provinces show in the companion dataset, where it is clear; here it is only suggestive.
- **Size does not predict income or growth.** Population correlates weakly with everything else (-0.31 to +0.22).

| Pair | r | 95% CI | p | n | Spearman ρ | Reading |
|---|---|---|---|---|---|---|
| GDP per head × R&D intensity | **+0.67** | -0.16 to +0.95 | 0.10 | 7 | +0.71 | strong, positive; not distinguishable from zero |
| Growth 2015 to 2024 × R&D intensity | **+0.65** | -0.21 to +0.94 | 0.12 | 7 | +0.89 | strong, positive; not distinguishable from zero |
| GDP per head × growth 2015 to 2024 | **+0.62** | -0.08 to +0.91 | 0.08 | 9 | +0.65 | strong, positive; not distinguishable from zero |
| GDP per head × population | **-0.31** | -0.77 to +0.36 | 0.36 | 11 | +0.09 | moderate, negative; not distinguishable from zero |
| Population × R&D intensity | **+0.22** | -0.64 to +0.83 | 0.64 | 7 | +0.21 | weak, positive; not distinguishable from zero |
| Population × growth 2015 to 2024 | **+0.10** | -0.60 to +0.72 | 0.80 | 9 | +0.13 | weak, positive; not distinguishable from zero |

GDP per head and population are taken in logarithms. The same figures are in the `correlations` configuration.

## Load it

```python
from datasets import load_dataset

cities = load_dataset("Kukai-7/greater-bay-area-networks", "cities", split="train").to_pandas()
ports = load_dataset("Kukai-7/greater-bay-area-networks", "ports", split="train").to_pandas()

# Container throughput of the three bay ports, 2004 to 2024
ports[ports.in_gba].pivot(index="year", columns="port", values="teu_thousand")
```

## Configurations

### `cities` (default), 11 rows

| column | description |
|---|---|
| `city`, `city_zh`, `status`, `latitude`, `longitude` | Name, Chinese name, administrative status, position of the city centre |
| `population_2024_10k` | Resident population at the end of 2024, in units of 10,000 (city statistical bulletins) |
| `gdp_2024_cny_100m`, `gdp_2024_usd_bn`, `gdp_per_capita_2024_cny`, `gdp_source` | GDP in 100 million yuan and billion dollars, GDP per head; mainland cities from the Guangdong Statistical Yearbook 2025, Hong Kong and Macao from the World Bank converted at 7.1217 yuan per dollar |
| `gdp_nominal_cagr_2015_2024_pct` | Nominal growth a year, mainland cities |
| `rd_2024_cny_100m`, `rd_intensity_2024_pct`, `rd_intensity_note` | R&D spending and its share of GDP in 2024 (Guangdong statistical bulletin); Foshan's share computed here |
| `container_teu_2024_thousand`, `airport_passengers_2024`, `airport_cargo_2024_tonnes` | Port and airport throughput in 2024 |
| `companies_listed` | Entries in the `companies` table |

### `city_gdp_by_year`, 126 rows

GDP and GDP per head of the nine mainland cities in 2000, 2005, 2008, 2010 to 2012, 2015 and 2018 to 2024, as published in the Guangdong Statistical Yearbook and the city bulletins.

### `ports`, 128 rows

Container throughput in thousand TEU, 2004 to 2024, for Shenzhen, Guangzhou and Hong Kong, with Shanghai, Singapore and Ningbo-Zhoushan for comparison; `in_gba` flags the bay ports and `note` the two corrected values (see limitations).

### `airports`, 97 rows

Passengers and cargo for Guangzhou Baiyun, Shenzhen Bao'an, Zhuhai Jinwan, Huizhou Pingtan and Foshan Shadi from 2000 (CAAC, 2025 preliminary), and Hong Kong and Macao for 2024 (cargo also for 2025 at Hong Kong), with positions.

### `links`, 19 rows

Name in English and Chinese, kind (road, rail, finance, policy zone), the two cities it connects, year of first opening or launch, and a note.

### `companies`, 32 rows

Headquarters city, English and Chinese name, founding year and segment (software and AI; ICT and chips; devices and robots; vehicles and batteries; finance; logistics) of selected companies and institutions.

### `correlations`, 6 rows

One row per pair of variables in the scatter-plot matrix: `n`, `pearson_r`, `r_squared`, `ci95_low`, `ci95_high` (Fisher z interval), `p_value` (two-sided t test), `spearman_rho`, `strength`, `direction`. Made by `correlations.py`.

## Dataset characterization

**Data collection method:** automated download of public tables (Wikipedia at pinned revisions, World Bank API, Natural Earth), plus hand curation of figures from official statistical bulletins and press releases. Every automated source is fixed to a revision so that the build can be repeated.

**Labeling method:** none in the machine-learning sense. Links, segments and companies were classified by hand for this dataset.

| Source | What it gives | Access |
|---|---|---|
| Guangdong Statistical Yearbook (2001 to 2025) and city bulletins, as tabulated on Chinese Wikipedia, *广东各地级市地区生产总值列表*, revision 91319080 | GDP and GDP per head of the nine mainland cities | Wikipedia API |
| City statistical bulletins 2024, Hong Kong and Macao statistics, via Chinese Wikipedia, *粤港澳大湾区*, revision 94965331 | Population at the end of 2024 | Wikipedia API |
| Lloyd's List One Hundred Ports, via English Wikipedia, *List of busiest container ports*, revision 1381656045 | Container throughput 2004 to 2024 | Wikipedia API |
| CAAC airport statistics, via English Wikipedia, *List of the busiest airports in China*, revision 1356827047 | Mainland airports 2000 to 2025 | Wikipedia API |
| Airports Council International; Airport Authority Hong Kong; CAM (Macao) | Hong Kong and Macao airports | Press releases, curated |
| World Bank, World Development Indicators | GDP of Hong Kong and Macao in dollars | API |
| Guangdong Provincial Bureau of Statistics and partners, *2024 statistical bulletin on R&D spending* (24 November 2025) | R&D by city | Curated |
| WIPO, Global Innovation Index 2025; Z/Yen and China Development Institute, GFCI 38; Xinhua (27 January 2026) | Cluster rank, financial centres, cross-border figures | Curated |
| Natural Earth | Coastline and borders | Download |

## How it was built

1. `collect.py` downloads the tables and the base map into `raw/`.
2. `build.py` parses the tables, adds the curated R&D figures, links and companies, and writes the Parquet files.
3. `viz.py` draws the charts and `correlations.py` the scatter-plot matrix and the `correlations` table.

## Limitations

- **Two statistical systems.** Hong Kong and Macao compile their accounts under their own rules and in their own currencies. Their GDP comes from the World Bank in dollars, converted at the 2024 central parity; their population is end-of-year, like the mainland's, but sources differ. Comparisons across the border are approximate.
- **Revisions and breaks.** City GDP for 2019 and earlier was revised after the economic census, and the 2020 census raised population estimates, which lowers GDP per head from 2020. Zhongshan's GDP was revised down in 2019. The yearly series are as published, not harmonised.
- **Nominal values.** GDP growth includes price changes.
- **Two port values corrected.** The 2023 column of the Wikipedia table gives operator figures for Shenzhen and Guangzhou (26.9 and 20.8 million TEU). They are replaced by the whole-port totals published by the cities (29.88 and 25.41 million), and flagged in `note`.
- **R&D at city level is incomplete.** The bulletin gives R&D spending for the seven cities above 10 billion yuan and the share of GDP for six; Foshan's share is computed here, Jiangmen and Zhaoqing are missing, and Hong Kong and Macao use other surveys.
- **Airports.** Hong Kong is included only for 2024 and 2025 in this version, Macao for 2024.
- **Curated tables are selections.** The links table keeps the main fixed links, financial connections and joint zones, not every road or ferry; the company list illustrates each city and is not a ranking or a complete census. Dates are the first opening to traffic or the launch.
- **No direct measure of AI.** R&D, companies and patents are proxies; there is no comparable public series on AI use by city.
- **Correlation only.** The scatter-plot matrix has seven to eleven points; it describes, it does not test causes.

## Ethical considerations

The data are aggregate public statistics about cities and companies; there is no personal data. Political status matters in this region: Hong Kong and Macao are Special Administrative Regions of China with their own statistical systems, and the dataset labels them as such without taking a position on policy. Nothing here is investment advice.

## Credits and licences

- Guangdong Provincial Bureau of Statistics; city statistics bureaus; Census and Statistics Department (Hong Kong); Statistics and Census Service (Macao).
- Wikipedia (CC BY-SA 4.0), World Bank (CC BY 4.0), Natural Earth (public domain), Lloyd's List, CAAC, ACI, WIPO, Z/Yen and CDI (figures cited).
- This compilation, curated tables and charts: CC BY 4.0.

## Citation

```bibtex
@misc{kukai7_gba_networks_2026,
  title  = {Greater Bay Area Networks: Logistics, Manufacturing, AI, Technology and Finance},
  author = {Kukai-7},
  year   = {2026},
  url    = {https://huggingface.co/datasets/Kukai-7/greater-bay-area-networks}
}
```

## Related

- [China, AI and Manufacturing](https://huggingface.co/datasets/Kukai-7/china-ai-manufacturing), R&D by province and the Hangzhou, Shenzhen and Beijing clusters.
- [China under Deng](https://huggingface.co/datasets/Kukai-7/deng-era-china), where the Special Economic Zones began.
- [GitHub: Kukai-7](https://github.com/Kukai-7)
