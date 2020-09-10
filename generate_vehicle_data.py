import pandas as pd
import pickle
import numpy as np
import random
import humanize
import datetime as dt

# Globals
BASE_ROUTES_DICT = dict()
DISTANCE_DICT = dict()

# Consts
NUM_ROUTES = 10
SECOND_IN_A_DAY = 24 * 60 * 60


NUM_VEHICLES = 20                       # Number of vehicles
DAY_START_RANGE = [0, 3 * 60 * 60]      # Start delay
SPEED_RANGE = [15, 25]                  # Vehicle Speed Range
IDLE_RANGE = [30 * 60, 5 * 60 * 60]     # Vehicle Idle range
FRAC_START_T0 = 0.25                    # Fraction of vehicles start at T0


def get_idle_data(start, end):
    d = {'timestamp': range(start, end)}
    d['latitude'] = [None] * (end - start)
    d['longitude'] = [None] * (end - start)
    return pd.DataFrame.from_dict(d)


def start_at_tzero():
    return random.choices([True, False], weights=(
        FRAC_START_T0, 1 - FRAC_START_T0), k=1)[0]


def get_idle_timedelta():
    return random.randint(IDLE_RANGE[0], IDLE_RANGE[1])


def get_speed():
    return random.randint(SPEED_RANGE[0], SPEED_RANGE[1])


def get_start_time():
    return random.randint(DAY_START_RANGE[0], DAY_START_RANGE[1])


def get_random_stop(exclude=None):
    stop = random.randint(0, NUM_ROUTES - 1)
    if exclude is None:
        return stop
    elif stop != exclude:
        return stop
    else:
        return get_random_stop(exclude)


def num_to_char(num):
    return chr(num + 97)


def load_base_routes():
    global BASE_ROUTES_DICT
    BASE_ROUTES_DICT = {'{}_{}'.format(num_to_char(stop1), num_to_char(stop2)): pd.read_csv('routes_cleaned/{}_{}.txt'.format(num_to_char(
        stop1), num_to_char(stop2))) for stop1 in range(0, NUM_ROUTES) for stop2 in range(0, NUM_ROUTES) if stop1 != stop2}
    print('Routes loaded...')
    # print(BASE_ROUTES_DICT.keys())


def load_distances():
    global DISTANCE_DICT
    with open('distances.pickle', 'rb') as f:
        DISTANCE_DICT = pickle.load(f)
    print('Distances loaded...')
    # print(DISTANCE_DICT.keys())


def get_route_data(stop1, stop2, start, speed=15):
    route_key = '{}_{}'.format(num_to_char(stop1), num_to_char(stop2))

    print('Route Key: {}'.format(route_key))

    # if start is None:
    #     start = int(datetime.now().timestamp())
    # start = int(start.timestamp())

    route_distance = DISTANCE_DICT[route_key]
    print('Route Distance: {} kms'.format(route_distance))

    datapoints = int((route_distance / speed) * 60 * 60)

    print('Datapoints: {}'.format(datapoints))

    df = BASE_ROUTES_DICT[route_key]
    x = df['latitude']
    y = df['longitude']
    xd = np.diff(x)
    yd = np.diff(y)
    dist = np.sqrt(xd**2 + yd**2)
    u = np.cumsum(dist)
    u = np.hstack([[0], u])
    t = np.linspace(0, u.max(), datapoints)
    xn = np.interp(t, u, x)
    yn = np.interp(t, u, y)
    timestamps = [epoch for epoch in range(start, start + len(xn))]

    start_ts = timestamps[0]
    end_ts = timestamps[-1]
    # print('Start: {}'.format(start_ts))
    # print('End: {}'.format(end_ts))

    data = dict()
    data['timestamp'] = timestamps
    data['latitude'] = xn
    data['longitude'] = yn

    return pd.DataFrame.from_dict(data), start_ts, end_ts


def printd(msg):
    print('')
    print(msg * 50)
    print('')


if __name__ == '__main__':
    load_base_routes()
    load_distances()

    printd('-')

    for vehicle_id in range(0, NUM_VEHICLES):
        print('Routing for vehicle: {}'.format(vehicle_id))
        vehicle_data = None
        current_time = 0 if start_at_tzero() else get_start_time()
        if current_time != 0:
            vehicle_data = get_idle_data(0, current_time)
        start_stop = None
        while current_time < SECOND_IN_A_DAY:
            start_stop = get_random_stop() if start_stop is None else start_stop
            end_stop = get_random_stop(start_stop)
            v_speed = get_speed()
            print('Starting from {} and going to {} with speed {}. Vehicle running time {}'.format(start_stop, end_stop,
                                                                                                   v_speed, humanize.naturaldelta(dt.timedelta(seconds=current_time)) if current_time != 0 else '0 seconds'))
            df, start_ts, end_ts = get_route_data(
                start_stop, end_stop, current_time)
            vehicle_data = df if vehicle_data is None else vehicle_data.append(
                df)

            idle_time = get_idle_timedelta()
            current_time = end_ts + idle_time
            vehicle_data = vehicle_data.append(
                get_idle_data(end_ts + 1, current_time))
            start_stop = end_stop
            print('Waiting at stop {} for {}'.format(start_stop,
                                                     humanize.naturaldelta(dt.timedelta(seconds=idle_time))))
            print('')

        vehicle_data.to_csv(
            'vehicle_data/{}.csv'.format(vehicle_id), index=False)
        printd('-')
