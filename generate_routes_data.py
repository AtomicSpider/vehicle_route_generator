import pyperclip

BASE_DIR_URL = 'https://www.google.com/maps/dir/{}/{}/'
STOPS_DICT = dict()
ROUTES_URL_DICT = dict()

with open('stops.txt', 'r') as f:
    stops = f.readlines()

for stop in stops:
    stop_id, coord = stop.strip().split(':')
    STOPS_DICT[stop_id] = coord


ROUTES_URL_DICT = {'{}_{}'.format(stop1, stop2): BASE_DIR_URL.format(
    STOPS_DICT[stop1], STOPS_DICT[stop2]) for stop1 in STOPS_DICT for stop2 in STOPS_DICT if stop1 != stop2}

route_iterater = iter(ROUTES_URL_DICT)

while True:
    input()
    key = next(route_iterater)

    pyperclip.copy(ROUTES_URL_DICT[key])
    print(ROUTES_URL_DICT[key])

    input()
    pyperclip.copy(key)
    print(key)
