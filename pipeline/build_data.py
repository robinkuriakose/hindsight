"""Build scenario data for the trading game from real sources.

Sources
- NSE stocks: NSE daily bhavcopy archive (github.com/BennyThadikaran/eod2_data, daily/*.csv),
  cross-checked against the NSE Bhavcopy MCP (mcp.nseindia.in) for 2022-2026 and used as-is for
  the final 11-Nov-2026 close. Bonus/split/demerger/rights events from the NSE MCP
  get_corporate_actions tool (2005+) and visible price jumps (pre-2005).
- Nifty 50: three independent NSE-format daily files that agree to 0.0000% on every overlapping day
  (2000-2021, 2005-2025, 2012-2026) + NSE MCP for the final close.
- Gold, silver, copper, Brent crude: World Bank Pink Sheet, monthly averages in USD
  (edition of 3-Nov-2026), converted to INR with FRED monthly USD/INR (EXINUS).
- USD/INR and EUR/INR: FRED monthly averages (github.com/datasets/exchange-rates).
- FD: flat 6% per year, compounded annually.
"""
import csv, json, datetime as dt, os, sys, openpyxl

S = os.environ.get('HINDSIGHT_RAW', 'raw')  # folder holding the raw NSE / World Bank / FRED downloads
RAW = f'{S}/raw'

# --- latest closes from NSE MCP get_bulk_quote (2026-11-11) and get_index_history -----------------
LATEST_DATE = '2026-11-11'
LATEST = {'WIPRO': 197.99, 'RELIANCE': 1335.4, 'BHEL': 432.0, 'SUZLON': 38.88, 'UNITECH': 3.98,
          'TCS': 2472.1, 'RPOWER': 19.32, 'DLF': 742.65, 'RCOM': 0.84, 'BHARTIARTL': 2109.0,
          'BAJFINANCE': 1078.8, 'INFY': 1155.0, 'YESBANK': 17.24, 'HDFCBANK': 806.6,
          'PCJEWELLER': 15.78, 'TITAN': 4970.0, 'GENUSPOWER': 289.8, 'ADANIENT': 2714.5,
          'TANLA': 694.5, 'HCLTECH': 1395.0, 'ITC': 285.0, 'SAIL': 175.48, 'ICICIBANK': 1571.6,
          'IDEA': 12.88, 'EICHERMOT': 7592.0, 'SBIN': 1061.2, 'KOTAKBANK': 487.7, 'PNB': 138.48,
          'MUTHOOTFIN': 2900.0, 'TATAPOWER': 360.0, 'DEEPAKNTR': 1588.9, 'MARUTI': 13185.0,
          'MRF': 127125.0, 'ASHOKLEY': 173.9, 'ONGC': 234.8, 'HCC': 18.96, 'HINDCOPPER': 436.35,
          'SUNPHARMA': 1902.3, 'HINDUNILVR': 2022.4, 'PAGEIND': 36570.0, 'ASIANPAINT': 2550.3,
          'JUBLFOOD': 434.9, 'HAL': 4949.0, 'BEL': 399.0, 'COCHINSHIP': 1202.0, 'COALINDIA': 406.3,
          'GRAPHITE': 773.5, 'VAKRANGEE': 5.87, 'AVANTIFEED': 704.1, 'INDIGO': 5665.0,
          'LUPIN': 2023.4, 'DRREDDY': 1377.0, 'BIOCON': 368.05, 'NIFTY': 25255.05}
# prev_close on 11-Nov-2026 from the same MCP quotes = archive's last close (consistency check)
PREV = {'WIPRO': 199.0, 'RELIANCE': 1324.4, 'BHEL': 422.95, 'SUZLON': 38.91, 'UNITECH': 3.95, 'TCS': 2475.4,
        'RPOWER': 18.8, 'DLF': 755.0, 'RCOM': 0.85, 'BHARTIARTL': 2072.1, 'BAJFINANCE': 1064.85, 'INFY': 1154.1,
        'YESBANK': 17.03, 'HDFCBANK': 798.15, 'PCJEWELLER': 15.2, 'TITAN': 5005.0, 'GENUSPOWER': 286.5,
        'ADANIENT': 2706.3, 'TANLA': 648.6, 'HCLTECH': 1407.0, 'ITC': 278.8, 'SAIL': 169.59, 'ICICIBANK': 1589.0,
        'IDEA': 12.67, 'EICHERMOT': 7629.0, 'SBIN': 1042.0, 'KOTAKBANK': 479.5, 'PNB': 132.17, 'MUTHOOTFIN': 2917.6,
        'TATAPOWER': 360.0, 'DEEPAKNTR': 1540.0, 'MARUTI': 12928.0, 'MRF': 125105.0, 'ASHOKLEY': 174.86,
        'ONGC': 233.5, 'HCC': 18.54, 'HINDCOPPER': 430.0, 'SUNPHARMA': 1904.5, 'HINDUNILVR': 1990.3,
        'PAGEIND': 36380.0, 'ASIANPAINT': 2509.3, 'JUBLFOOD': 428.5, 'HAL': 4999.0, 'BEL': 394.55,
        'COCHINSHIP': 1290.0, 'COALINDIA': 401.5, 'GRAPHITE': 763.1, 'VAKRANGEE': 5.75, 'AVANTIFEED': 722.55,
        'INDIGO': 5430.0, 'LUPIN': 2025.0, 'DRREDDY': 1385.0, 'BIOCON': 368.5}

# --- corporate actions not already adjusted in the archive -----------------------------------------
# ('B', exdate, factor)  bonus/split: multiply all closes before exdate by factor
# ('D', exdate)          demerger: factor = close(ex) / close(prev)  (standard price-ratio method)
# ('R', exdate, held, new, issue_price_in_archive_units)  rights: theoretical ex-rights price
CA = {
    'WIPRO': [('B', '2004-06-25', 1/3), ('B', '2005-08-22', .5), ('B', '2010-06-15', .6)],
    'RELIANCE': [('B', '1997-11-05', .5), ('D', '2006-01-18'), ('B', '2009-11-26', .5),
                 ('R', '2020-05-13', 15, 1, 1257 / 2), ('D', '2023-07-20')],
    'BHEL': [('B', '2007-05-31', .5)],
    'SUZLON': [('B', '2008-01-21', .2), ('R', '2010-06-09', 15, 2, 63), ('R', '2022-10-03', 21, 5, 5)],
    'UNITECH': [('B', '2006-06-23', .2 / 13), ('B', '2007-08-30', .5)],
    'TCS': [('B', '2006-07-28', .5), ('B', '2009-06-16', .5)],
    'RPOWER': [('B', '2008-05-30', .625)],
    'BHARTIARTL': [('B', '2009-07-24', .5), ('R', '2019-04-23', 67, 19, 220), ('R', '2021-09-27', 14, 1, 535)],
    'BAJFINANCE': [('R', '2013-01-23', 19, 3, 1100 / 100)],
    'INFY': [('B', '2015-06-15', .5)],
    'ADANIENT': [('D', '2015-06-03'), ('D', '2018-04-05'), ('D', '2018-09-06'), ('R', '2025-11-17', 25, 3, 1800)],
    'GENUSPOWER': [('B', '2010-10-22', .1)],
    'HCLTECH': [('B', '2000-11-29', .5), ('B', '2007-03-15', .5)],
    'ITC': [('B', '2005-09-21', 1 / 15), ('B', '2010-08-03', .5), ('D', '2025-01-06')],
    'ICICIBANK': [('B', '2017-06-20', 10 / 11)],
    'IDEA': [('R', '2019-03-29', 38, 87, 12.5)],
    'ONGC': [('B', '2006-10-27', 2 / 3), ('B', '2011-02-08', .25)],
    'ASHOKLEY': [('B', '2004-06-29', .1)],
    'HCC': [('B', '2010-08-10', .5), ('R', '2018-11-20', 100, 49, 10), ('R', '2024-03-15', 118, 13, 21),
            ('R', '2025-12-05', 630, 277, 12.5)],
    'HINDUNILVR': [('D', '2025-12-05')],
}


def check_latest(sym, d):
    last = d[-1][1]
    if abs(last / PREV[sym] - 1) > 0.002:
        print(f'WARNING {sym}: archive last {d[-1]} vs MCP prev_close {PREV[sym]}')


def load_stock(sym):
    rows = [r for r in csv.DictReader(open(f'{RAW}/{sym.lower()}.csv')) if r['Close'] not in ('', 'nan')]
    d = [[r['Date'], float(r['Close'])] for r in rows]
    for ev in CA.get(sym, []):
        ex = ev[1]
        i = next(k for k, (dd, _) in enumerate(d) if dd >= ex)
        if ev[0] == 'B':
            f = ev[2]
        elif ev[0] == 'D':
            f = d[i][1] / d[i - 1][1]
        else:
            held, new, issue = ev[2], ev[3], ev[4]
            p = d[i - 1][1]
            f = (held * p + new * issue) / ((held + new) * p)
        for row in d:
            if row[0] < ex:
                row[1] *= f
    return d


def load_nifty():
    out = {}
    for r in csv.DictReader(open(f'{S}/nifty/n14.csv')):           # 2000-2021, D/M/YYYY
        dd, mm, yy = r['Date'].split('/')
        out[f'{yy}-{int(mm):02d}-{int(dd):02d}'] = float(r['Close/Last'])
    for r in csv.DictReader(open(f'{S}/nifty/n4.csv')):            # 2005-2025, NSE format
        k = dt.datetime.strptime(r['HistoricalDate'].strip(), '%d %b %Y').strftime('%Y-%m-%d')
        out[k] = float(r['CLOSE'])
    for r in csv.DictReader(open(f'{RAW}/nifty 50.csv')):          # 2012-2026
        out[r['Date']] = float(r['Close'])
    return sorted(out.items())


def first_on_or_after(series, date):
    for dd, c in series:
        if dd >= date:
            gap = (dt.date.fromisoformat(dd) - dt.date.fromisoformat(date)).days
            if gap > 10:
                raise ValueError(f'gap {gap}d at {date} -> {dd}')
            return dd, c
    raise ValueError(f'no data on/after {date}')


# --- monthly series: World Bank Pink Sheet + FRED FX ------------------------------------------------
wb = openpyxl.load_workbook(f'{S}/wbdl/cmo.xlsx', read_only=True, data_only=True)['Monthly Prices']
wrows = list(wb.iter_rows(values_only=True))
hdr = wrows[4]
col = {'GOLD': hdr.index('Gold'), 'SILVER': hdr.index('Silver'), 'COPPER': hdr.index('Copper'),
       'BRENT': hdr.index('Crude oil, Brent'), 'ALUMINIUM': hdr.index('Aluminum'),
       'PLATINUM': hdr.index('Platinum'), 'NATGAS': hdr.index('Natural gas, US')}
WB = {k: {} for k in col}
for r in wrows[6:]:
    if not r[0] or 'M' not in str(r[0]):
        continue
    y, m = str(r[0]).split('M')
    for k, c in col.items():
        if isinstance(r[c], (int, float)):
            WB[k][f'{y}-{m}'] = float(r[c])

FX = {'India': {}, 'Euro': {}}
for r in csv.DictReader(open(f'{S}/dl/datasets_exchange-rates_main_data_monthly.csv')):
    if r['Country'] in FX and r['Exchange rate']:
        FX[r['Country']][r['Date'][:7]] = float(r['Exchange rate'])
USDINR = FX['India']
EURINR = {k: USDINR[k] / v for k, v in FX['Euro'].items() if k in USDINR}   # dataset: EUR per USD
LAST_MONTH = '2026-10'
for k in WB:
    assert LAST_MONTH in WB[k], k
assert LAST_MONTH in USDINR and LAST_MONTH in EURINR

TROY_OZ_PER_10G = 10 / 31.1034768


def monthly_inr(kind, ym):
    fx = USDINR[ym]
    if kind == 'GOLD':
        return WB['GOLD'][ym] * fx * TROY_OZ_PER_10G           # Rs per 10 g
    if kind == 'SILVER':
        return WB['SILVER'][ym] * fx * 1000 / 31.1034768        # Rs per kg
    if kind == 'COPPER':
        return WB['COPPER'][ym] * fx / 1000                     # Rs per kg
    if kind == 'BRENT':
        return WB['BRENT'][ym] * fx                             # Rs per barrel
    if kind == 'ALUMINIUM':
        return WB['ALUMINIUM'][ym] * fx / 1000                  # Rs per kg
    if kind == 'PLATINUM':
        return WB['PLATINUM'][ym] * fx * TROY_OZ_PER_10G        # Rs per 10 g
    if kind == 'NATGAS':
        return WB['NATGAS'][ym] * fx                            # Rs per mmBtu
    if kind == 'USD':
        return fx
    if kind == 'EUR':
        return EURINR[ym]
    raise KeyError(kind)


ASSETS = {
    # id: (display name, type, short description, unit)
    'WIPRO': ('Wipro', 'stock', 'IT services', 'share'),
    'RELIANCE': ('Reliance Industries', 'stock', 'Oil-to-retail conglomerate', 'share'),
    'BHEL': ('BHEL', 'stock', 'State-owned power equipment maker', 'share'),
    'SUZLON': ('Suzlon Energy', 'stock', 'Wind turbine maker', 'share'),
    'UNITECH': ('Unitech', 'stock', 'Real estate developer', 'share'),
    'TCS': ('TCS', 'stock', 'IT services', 'share'),
    'RPOWER': ('Reliance Power', 'stock', 'Power producer (ADAG)', 'share'),
    'DLF': ('DLF', 'stock', 'Real estate developer', 'share'),
    'RCOM': ('Reliance Communications', 'stock', 'Telecom operator (ADAG)', 'share'),
    'BHARTIARTL': ('Bharti Airtel', 'stock', 'Telecom operator', 'share'),
    'BAJFINANCE': ('Bajaj Finance', 'stock', 'Consumer lender (NBFC)', 'share'),
    'INFY': ('Infosys', 'stock', 'IT services', 'share'),
    'YESBANK': ('Yes Bank', 'stock', 'Private sector bank', 'share'),
    'HDFCBANK': ('HDFC Bank', 'stock', 'Private sector bank', 'share'),
    'PCJEWELLER': ('PC Jeweller', 'stock', 'Jewellery retailer', 'share'),
    'TITAN': ('Titan', 'stock', 'Watches & jewellery (Tanishq)', 'share'),
    'GENUSPOWER': ('Genus Power', 'stock', 'Electricity meter maker', 'share'),
    'ADANIENT': ('Adani Enterprises', 'stock', 'Adani group flagship', 'share'),
    'TANLA': ('Tanla Platforms', 'stock', 'Business messaging (CPaaS)', 'share'),
    'HCLTECH': ('HCL Technologies', 'stock', 'IT services', 'share'),
    'ITC': ('ITC', 'stock', 'Cigarettes, hotels, packaged food', 'share'),
    'SAIL': ('SAIL', 'stock', 'State-owned steelmaker', 'share'),
    'ICICIBANK': ('ICICI Bank', 'stock', 'Private sector bank', 'share'),
    'IDEA': ('Idea Cellular', 'stock', 'Telecom operator', 'share'),
    'EICHERMOT': ('Eicher Motors', 'stock', 'Royal Enfield motorcycles', 'share'),
    'SBIN': ('State Bank of India', 'stock', "India's largest bank", 'share'),
    'KOTAKBANK': ('Kotak Mahindra Bank', 'stock', 'Private sector bank', 'share'),
    'PNB': ('Punjab National Bank', 'stock', 'Public sector bank', 'share'),
    'MUTHOOTFIN': ('Muthoot Finance', 'stock', 'Gold loan company', 'share'),
    'TATAPOWER': ('Tata Power', 'stock', 'Power utility', 'share'),
    'DEEPAKNTR': ('Deepak Nitrite', 'stock', 'Chemicals maker', 'share'),
    'MARUTI': ('Maruti Suzuki', 'stock', "India's largest carmaker", 'share'),
    'MRF': ('MRF', 'stock', 'Tyre maker', 'share'),
    'ASHOKLEY': ('Ashok Leyland', 'stock', 'Trucks and buses', 'share'),
    'ONGC': ('ONGC', 'stock', 'State-owned oil producer', 'share'),
    'HCC': ('HCC', 'stock', 'Construction and infrastructure', 'share'),
    'HINDCOPPER': ('Hindustan Copper', 'stock', 'State-owned copper miner', 'share'),
    'SUNPHARMA': ('Sun Pharma', 'stock', 'Pharmaceuticals', 'share'),
    'HINDUNILVR': ('Hindustan Unilever', 'stock', 'Soaps, detergents, foods', 'share'),
    'PAGEIND': ('Page Industries', 'stock', 'Jockey innerwear licensee', 'share'),
    'ASIANPAINT': ('Asian Paints', 'stock', 'Paint maker', 'share'),
    'JUBLFOOD': ('Jubilant FoodWorks', 'stock', "Runs Domino's Pizza in India", 'share'),
    'HAL': ('Hindustan Aeronautics', 'stock', 'Military aircraft maker', 'share'),
    'BEL': ('Bharat Electronics', 'stock', 'Defence electronics', 'share'),
    'COCHINSHIP': ('Cochin Shipyard', 'stock', 'Shipbuilder', 'share'),
    'COALINDIA': ('Coal India', 'stock', 'State-owned coal miner', 'share'),
    'GRAPHITE': ('Graphite India', 'stock', 'Electrodes for steel furnaces', 'share'),
    'VAKRANGEE': ('Vakrangee', 'stock', 'Rural kiosks and e-commerce', 'share'),
    'AVANTIFEED': ('Avanti Feeds', 'stock', 'Shrimp feed and seafood', 'share'),
    'INDIGO': ('IndiGo', 'stock', 'Low-cost airline', 'share'),
    'LUPIN': ('Lupin', 'stock', 'Generic medicines', 'share'),
    'DRREDDY': ("Dr. Reddy's", 'stock', 'Generic medicines', 'share'),
    'BIOCON': ('Biocon', 'stock', 'Biotech and biosimilars', 'share'),
    'ALUMINIUM': ('Aluminium', 'commodity', 'Industrial metal', 'kg'),
    'PLATINUM': ('Platinum', 'commodity', 'Precious metal', '10 g'),
    'NATGAS': ('Natural Gas', 'commodity', 'US Henry Hub gas', 'mmBtu'),
    'GOLD': ('Gold', 'commodity', 'Precious metal', '10 g'),
    'SILVER': ('Silver', 'commodity', 'Precious metal', 'kg'),
    'COPPER': ('Copper', 'commodity', 'Industrial metal', 'kg'),
    'BRENT': ('Crude Oil', 'commodity', 'Brent crude', 'barrel'),
    'USD': ('US Dollar', 'currency', 'Hold dollars vs rupee', 'USD'),
    'EUR': ('Euro', 'currency', 'Hold euros vs rupee', 'EUR'),
    'NIFTY': ('Nifty 50', 'index', "India's top-50 index", 'index pt'),
    'FD': ('Fixed Deposit', 'fd', 'Guaranteed 6% a year', ''),
}

SCENARIOS = json.load(open(__file__.rsplit('/', 1)[0] + '/scenarios.json'))


def add_months(y, m, k):
    t = (y * 12 + (m - 1)) + k
    return t // 12, t % 12 + 1


stock_cache = {}
nifty = load_nifty()


def build(sc):
    y0, m0 = sc['start']
    pts = []
    k = 0
    while True:
        y, m = add_months(y0, m0, 6 * k)
        if f'{y}-{m:02d}' > LAST_MONTH:
            break
        pts.append((y, m))
        k += 1
    assert len(pts) >= 17, sc['id']
    dates = [f'{y}-{m:02d}' for y, m in pts] + ['latest']
    labels = [dt.date(y, m, 1).strftime('%b %Y') for y, m in pts] + ['Nov 2026']
    opts = []
    for aid in sc['assets'] + ['NIFTY', 'FD']:
        name, typ, desc, unit = ASSETS[aid]
        vals, src_dates = [], []
        for (y, m) in pts:
            ym = f'{y}-{m:02d}'
            if typ == 'stock':
                if aid not in stock_cache:
                    stock_cache[aid] = load_stock(aid); check_latest(aid, stock_cache[aid])
                s = stock_cache[aid]
                dd, c = first_on_or_after(s, f'{ym}-01')
            elif typ == 'index':
                dd, c = first_on_or_after(nifty, f'{ym}-01')
            elif typ == 'fd':
                dd, c = ym, 100 * 1.06 ** ((y * 12 + m - (y0 * 12 + m0)) / 12)
            else:
                dd, c = ym, monthly_inr(aid, ym)
            vals.append(c)
            src_dates.append(dd)
        # final point
        if typ in ('stock', 'index'):
            vals.append(LATEST[aid]); src_dates.append(LATEST_DATE)
        elif typ == 'fd':
            y, m = 2026, 11
            vals.append(100 * 1.06 ** ((y * 12 + m - (y0 * 12 + m0)) / 12)); src_dates.append(LATEST_DATE)
        else:
            vals.append(monthly_inr(aid, LAST_MONTH)); src_dates.append(LAST_MONTH)
        opts.append({'id': aid, 'name': name, 'type': typ, 'desc': desc, 'unit': unit,
                     'prices': [round(v, 4) for v in vals], 'priceDates': src_dates})
    return {**sc, 'dates': dates, 'labels': labels, 'options': opts}


out = [build(sc) for sc in SCENARIOS]

# --- report ---------------------------------------------------------------------------------------
for sc in out:
    print(f"\n== {sc['id']}  {sc['labels'][0]} -> L4 {sc['labels'][12]} -> result {sc['labels'][16]} -> {sc['labels'][-1]}")
    for o in sc['options']:
        p = o['prices']
        r = lambda a, b: p[b] / p[a]
        print(f"  {o['name']:22s} R1 {r(0,4):6.2f}x  R2 {r(4,8):6.2f}x  R3 {r(8,12):6.2f}x  R4 {r(12,16):6.2f}x | to result {r(0,16):7.2f}x | hold {r(16,-1):6.2f}x  total {r(0,-1):8.2f}x")

json.dump(out, open(__file__.rsplit('/', 1)[0] + '/scenarios_built.json', 'w'), indent=1)
print('\nwrote', len(out), 'scenarios')
