import requests
import json
import board
import neopixel
import time

station_cfg = {
    'KBVO': [None, 'KIDP', 'KCFV', False],
    'KIDP': [None, 'KCFV', 'KPPF', False],
    'KCFV': [None, 'KIDP', 'KPPF', False],
    'KPPF': [None, 'KCFV', 'KCNU', False],
    'KCNU': [None, 'KPPF', 'KCFV', False],
    'KUKL': [None, 'KEMP', 'KOWI', False],
    'K13K': [None, 'KEQA', 'KEMP', False],
    'KEQA': [None, 'K13K', 'KEMP', False],
    'KEMP': [None, 'KUKL', 'K13K', False],
    'KFRI': [None, 'KMHK', 'KFOE', False],
    'KMHK': [None, 'KFRI', 'KTOP', False],
    'KFOE': [None, 'KTOP', 'KLWC', False],
    'KTOP': [None, 'KFOE', 'KLWC', False],
    'KLWC': [None, 'KTOP', 'KIXD', False],
    'KMCI': [None, 'KMKC', 'KGPH', False],
    'KGPH': [None, 'KMCI', 'KMKC', False],
    'KMKC': [None, 'KMCI', 'KLXT', False],
    'KLXT': [None, 'KMKC', 'KOJC', False],
    'KOJC': [None, 'KIXD', 'KLXT', False],
    'KIXD': [None, 'KOJC', 'KLWC', False],
    'KOWI': [None, 'KIXD', 'KUKL', False],
    'KLRY': [None, 'KOJC', 'KLXT', False],
    'KFSK': [None, 'KPTS', 'KCNU', False],
    'KPTS': [None, 'KFSK', 'KJLN', False],
    'KJLN': [None, 'KPTS', 'KHFJ', False],
    'KGMJ': [None, 'KJLN', 'KHFJ', False],
    'KHFJ': [None, 'KJLN', 'KSGF', False],
    'KBBG': [None, 'KFWB', 'KSGF', False],
    'KFWB': [None, 'KBBG', 'KSGF', False],
    'KSGF': [None, 'KFWB', 'KHFJ', False],
    'KLBO': [None, 'KOZS', 'KTBN', False],
    'KTBN': [None, 'KLBO', 'KOZS', False],
    'KOZS': [None, 'KLBO', 'KTBN', False],
    'KAIZ': [None, 'KOZS', 'KTBN', False],
    'KRAW': [None, 'KGLY', 'KDMO', False],
    'KGLY': [None, 'KRAW', 'KSZL', False],
    'KSZL': [None, 'KDMO', 'KGLY', False],
    'KDMO': [None, 'KSZL', 'KMHL', False],
    'KMHL': [None, 'KDMO', 'KSZL', False],
    'KMBY': [None, 'KVER', 'KCOU', False],
    'KVER': [None, 'KCOU', 'KMHL', False],
    'KCOU': [None, 'KJEF', 'KVER', False],
    'KJEF': [None, 'KCOU', 'KVER', False],
}

# Create comma-separated list of station IDs for web api
id_str = ','.join(station_cfg.keys())
uri='https://aviationweather.gov/api/data/metar'

color_magenta = (8, 0, 8)
color_red = (16, 0, 0)
color_blue = (0, 0, 16)
color_yellow = (14, 10, 0)
color_green = (0, 16, 0)
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
leds = neopixel.NeoPixel(board.D18, led_len, auto_write=False, pixel_order = neopixel.GRB)
# Update time delay for LED strip in seconds
fc_arr = [0] * len(station_cfg)
z_arr = [[0 for _ in range(2)] for _ in range(len(station_cfg))]
z_qty = 0

# Set up the legend LEDs
for i in range(led_skip):
    leds[i] = (0,0,0)
for i in range(5):
    leds[i+led_skip] = colors[i+1]

first_loop = True
while True:
    print(time.strftime('%m.%d-%H:%M:%S'), ' === Start processing loop ===')
    z_qty = 0
    for i in range(len(fc_arr)):
        fc_arr[i] = 0
    for k in station_cfg.keys():
        station_cfg[k][0] = None
        station_cfg[k][3] = False

    r = requests.get('https://aviationweather.gov/api/data/metar', params={'ids' : id_str, 'format' : 'json'})
    wjson=json.loads(r.text)

    # Save the fltCat value..

    for w in wjson:
        flt_cat = w.get('fltCat', None)
        if (flt_cat == 'VFR' or flt_cat == None) and (w.get('wspd', 0) >= 25 or w.get('wgst', 0) >= 25):
            flt_cat = 'WVFR'
        if flt_cat == None:
            continue
        if 'TS' in w.get('wxString', ''):
            print('Lightning: ', w['icaoId'])
            station_cfg[w['icaoId']][3] = True
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
        if v[3] == True:
            z_arr[z_qty][0:2] = [fc_n, fc_arr[fc_n]]
            z_qty += 1
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

    for t in range(900, -1, -5):
        time.sleep(1)
        if z_qty > 0:
            for n in range(3):
                for i in range(z_qty):
                    leds[led_n0 + z_arr[i][0]] = [16,16,16]
                leds.show()
                time.sleep(0.05)
                for i in range(z_qty):
                    leds[led_n0 + z_arr[i][0]] = [0, 0, 0]
                leds.show()
                time.sleep(0.05)
            for i in range(z_qty):
                leds[led_n0 + z_arr[i][0]] = colors[z_arr[i][1]]
            leds.show()
            time.sleep(3.7)
        else:
            leds.show()
            time.sleep(4)
