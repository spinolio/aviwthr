import requests
import json
import board
import neopixel
import time

def rgb2grb(c):
    return (c[1], c[0], c[2])

def no_map(c):
    return c

station_cfg = {
    'KBVO': [None, 'KCFV', 'KPPF'],
    'KIDP': [None, 'KCFV', 'KPPF'],
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

# Must choose an RGB color_map from no_map, rgb2grb
color_map = no_map
color_magenta = color_map((16, 0, 16))
color_red = color_map((32, 0, 0))
color_blue = color_map((0, 0, 32))
color_yellow = color_map((18, 14, 0))
color_green = color_map((0, 32, 0))
num_black = 0
num_magenta = 1
num_red = 2
num_blue = 3
num_yellow = 4
num_green = 5
colors = [(0,0,0), color_magenta, color_red, color_blue, color_yellow, color_green]
color_map={'LIFR':num_magenta, 'IFR':num_red, 'MVFR':num_blue, 'WVFR': num_yellow, 'VFR':num_green}

# The LED strip starts with 0 or more skipped LEDs followed by 5 legend LEDs
led_skip = 2
led_n0 = 5 + led_skip
led_len = led_n0 + len(station_cfg)
leds = neopixel.NeoPixel(board.D18, led_len, auto_write=False)
# Update time delay for LED strip in seconds
led_td = 5
fc_arr = [0] * len(station_cfg)

# Set up the legend LEDs
for i in range(led_skip):
    leds[i] = (0,0,0)
leds[led_skip] = color_magenta
leds[led_skip+1] = color_red
leds[led_skip+2] = color_blue
leds[led_skip+3] = color_yellow
leds[led_skip+4] = color_green
first_loop = True

while True:
    print(time.strftime('%m.%d-%H:%M:%S'), ' === Start processing loop ===')
    for i in range(len(fc_arr)):
        fc_arr[i] = 0
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

    fc_n = 0
    for k, v in station_cfg.items():
        if v[0] == None:
            # Try using first backup
            flt_cat = station_cfg[v[1]][0]
            if flt_cat == None:
                print(k, '<!', v[1])
                # Egad, try using second backup
                flt_cat = station_cfg[v[2]][0]
                if flt_cat == None:
                    print(k, '<!!', v[2])
                else:
                    print(k, '<==', v[2])
            else:
                print(k, '<=', v[1])
        else:
            flt_cat = v[0]
        if flt_cat != None:
            print(f'{k}: {flt_cat}')
            fc_arr[fc_n] = color_map[flt_cat]
        fc_n += 1
    # Update the LED strip
    time.sleep(1)
    if first_loop == True:
        first_loop = False
    else:
        for i in range(len(station_cfg)):
            leds[i + led_n0] = (0,0,0)
            leds.show()
            time.sleep(0.05)
    for i in range(len(station_cfg)):
        leds[i + led_n0] = colors[fc_arr[i]]
        leds.show()
        time.sleep(0.05)

    for t in range(900, -1, -led_td):
        time.sleep(led_td)
        leds.show()
