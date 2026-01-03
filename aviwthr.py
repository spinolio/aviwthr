import requests
import json
import board
import neopixel
import time

# I only have 10 leds; The legend uses 5.
station_cfg = {
    'KLWC': [None, 'KTOP', 'KIXD'],
    'KMCI': [None, 'KMKC', 'KGPH'],
    'KGPH': [None, 'KMCI', 'KMKC'],
    'KMKC': [None, 'KMCI', 'KLXT'],
    'KLXT': [None, 'KMKC', 'KOJC'],
}

leds = neopixel.NeoPixel(board.D18, 10, auto_write=False)

# Create comma-separated list of station IDs for web api
id_str = ','.join(station_cfg.keys())

uri='https://aviationweather.gov/api/data/metar'

color_magenta = (16, 0, 16)
color_red = (32, 0, 0)
color_blue = (0, 0, 32)
color_yellow = (18, 14, 0)
color_green = (0, 32, 0)
colors={'LIFR':color_magenta, 'IFR':color_red, 'MVFR':color_blue, 'WVFR': color_yellow, 'VFR':color_green}

# The first five LEDs will stay the same.
led_n0 = 5

# For now just run a set number of loops
for x in range(5):
    leds.fill([0,0,0])
    for k in station_cfg.keys():
        station_cfg[k][0] = None
    r = requests.get('https://aviationweather.gov/api/data/metar', params={'ids' : id_str, 'format' : 'json'})

    wjson=json.loads(r.text)

    # Save the fltCat value..

    for w in wjson:
        flt_cat = w.get('fltCat', None)
        if flt_cat == None:
            continue
        station_cfg[w['icaoId']][0] = flt_cat

    # Check the status determined above to see if any were not processed. Use the
    # primary and then secondary backup stations to fill in the missing data.

    leds[0] = color_magenta
    leds[1] = color_red
    leds[2] = color_blue
    leds[3] = color_yellow
    leds[4] = color_green
    led_n = led_n0
    for k, v in station_cfg.items():
        if v[0] == None:
            # Try using first backup
            flt_cat = station_cfg[v[1]][0]
            # print(k, '<=', v[1])
            if flt_cat == None:
                # Egad, try using second backup
                flt_cat = station_cfg[v[2]][0]
                # print(k, '<==', v[2])
        else:
            flt_cat = v[0]
        if flt_cat != None:
            leds[led_n] = colors[flt_cat]
        led_n += 1

    time.sleep(1)
    leds.show()
    time.sleep(120)
