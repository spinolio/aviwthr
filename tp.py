import requests
import json

# TODO: Read config data from file
station_cfg = {
    'KBVO': [None, 'KCFV', 'KPPF'],
    'KCFV': [None, 'KIDP', 'KPPF'],
    'KPPF': [None, 'KCFV', 'KCNU'],
    'KCNU': [None, 'KPPF', 'KCFV'],
    'KUKL': [None, 'KEMP', 'KOWI'],
    'K13K': [None, 'KEQA', 'KEMP'],
    'KEQA': [None, 'K13K', 'KEMP'],
    'KEMP': [None, 'KUKL', 'K13K'],
    'KFRI': [None, 'KMHK', 'KFOE'],
    'KMHK': [None, 'KFRI', 'KTOP'],
    'KFOE': [None, 'KTOP', 'KLWC'],
    'KTOP': [None, 'KFOE', 'KLWC'],
    'KLWC': [None, 'KTOP', 'KIXD'],
    'KMCI': [None, 'KMKC', 'KGPH'],
    'KGPH': [None, 'KMCI', 'KMKC'],
    'KMKC': [None, 'KMCI', 'KLXT'],
    'KLXT': [None, 'KMKC', 'KOJC'],
    'KOJC': [None, 'KIXD', 'KLXT'],
    'KIXD': [None, 'KOJC', 'KLWC'],
    'KOWI': [None, 'KIXD', 'KUKL'],
    'KLRY': [None, 'KOJC', 'KLXT'],
    'KFSK': [None, 'KPTS', 'KCNU'],
    'KPTS': [None, 'KFSK', 'KJLN'],
    'KJLN': [None, 'KPTS', 'KHFJ'],
    'KGMJ': [None, 'KJLN', 'KHFJ'],
    'KHFJ': [None, 'KJLN', 'KSGF'],
    'KBBG': [None, 'KFWB', 'KSGF'],
    'KFWB': [None, 'KBBG', 'KSGF'],
    'KSGF': [None, 'KFWB', 'KHFJ'],
    'KLBO': [None, 'KOZS', 'KTBN'],
    'KTBN': [None, 'KLBO', 'KOZS'],
    'KOZS': [None, 'KLBO', 'KTBN'],
    'KAIZ': [None, 'KOZS', 'KTBN'],
    'KRAW': [None, 'KGLY', 'KDMO'],
    'KGLY': [None, 'KRAW', 'KSZL'],
    'KSZL': [None, 'KDMO', 'KGLY'],
    'KDMO': [None, 'KSZL', 'KMHL'],
    'KMHL': [None, 'KDMO', 'KSZL'],
    'KMBY': [None, 'KVER', 'KCOU'],
    'KVER': [None, 'KCOU', 'KMHL'],
    'KCOU': [None, 'KJEF', 'KVER'],
    'KJEF': [None, 'KCOU', 'KVER'],
}

# Create comma-separated list of station IDs for web api
id_str = ','.join(station_cfg.keys())

uri='https://aviationweather.gov/api/data/metar'
colors={'LIFR':'magenta', 'IFR':'red', 'MVFR':'blue', 'VFR':'green'}

r = requests.get('https://aviationweather.gov/api/data/metar', params={'ids' : id_str, 'format' : 'json'})

wjson=json.loads(r.text)

# Set the colors of all station IDs returned based on the fltCat value..

for w in wjson:
    flt_cat = w.get('fltCat', None)
    if flt_cat == None:
        continue
    station_cfg[w['icaoId']][0] = flt_cat
    
# Check the status colors determined above to see if any were not processed. Use the
# primary and then secondary backup stations to fill in the missing data.

for k, v in station_cfg.items():
    if v[0] == None:
        # Try using first backup
        flt_cat = station_cfg[v[1]][0]
        print(k, '<=', v[1])
        if flt_cat == None:
            # Egad, try using second backup
            flt_cat = station_cfg[v[2]][0]
            print(k, '<==', v[2])
    else:
        flt_cat = v[0]
        led_color = colors[flt_cat]
    print(f'{k}: {flt_cat} ({led_color})')

