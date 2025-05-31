#!/usr/bin/env python3

import tltdata
import datetime
import interpolate as intr
import math
import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
from pyproj import Transformer

departure_tolerance = 50
deadline_hour = 9
deadline_minute = 5
deadline_second = 0
seconds_home2bus = 300
seconds_stop2work = 240
start_stop = "Zoo"
end_stop = "Toompark"
linenumber = "8"
first_sample_after = datetime.datetime(2025, 5, 3, 8, 0, 0)
last_sample_before = datetime.datetime(2025, 5, 30, 10, 0, 0)

def find_stop(stops, name):
    matches = []
    for stop in stops:
        if len(stop) < 6:
            continue
        if stop[5] == name:
            matches.append(stop)
    return matches

def find_approaches(target, trajectory, adirection):
    # transformer to Estonian linear coordinates, meters
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3301", always_xy=True)
    target3301 = transformer.transform(target[1], target[0])
    transformed = []

    approaches = {}
    ret = []
    for frame, frametime in trajectory:
        newcoords = []
        for v, coord, direction in frame:
            # discard other direction
            if direction != adirection:
                continue
            # already logged this approach
            if v in approaches and frametime - max(approaches[v]) < datetime.timedelta(minutes=2):
                continue
            coord = coord.coords[0]
            transcoord = transformer.transform(coord[1], coord[0])
            newcoords.append(transcoord)
            dist = math.sqrt((transcoord[0]-target3301[0])**2 + (transcoord[1]-target3301[1])**2)
            if dist < departure_tolerance:
                #print(f"Approach {v} {frametime} {direction}")
                ret.append((v, frametime))
                if v not in approaches:
                    approaches[v] = [frametime]
                else:
                    approaches[v].append(frametime)

        transformed.append(newcoords)

    #print(target3301)
    #print(transformed)
    return ret

def find_soonest_arrival(trips, time_point):
    for trip in trips:
        if trip[0] >= time_point:
            return trip[1]
    return None

def check_late(trips, left_home_time, deadline):
    left_dt = trips[0][0].replace(hour=left_home_time.hour, minute=left_home_time.minute, second=left_home_time.second)
    bus_stop_time = left_dt + datetime.timedelta(seconds=seconds_home2bus)
    arrival = find_soonest_arrival(trips, bus_stop_time)
    if arrival is None:
        return True
    else:
        return arrival > (deadline - datetime.timedelta(seconds=seconds_stop2work))
    
def probability_late(samples, left_home_time):
    count_late = 0
    count = 0
    for sample in samples:
        deadline = sample[0][0].replace(hour = deadline_hour, minute=deadline_minute, second=deadline_second)
        waslate = check_late(sample, left_home_time, deadline)
        count_late += 1 if waslate else 0
        count += 1
    return float(count_late)/count


def solve():
    # Find departure and arrival stops
    stops = tltdata.get_stops()
    start = find_stop(stops, start_stop)[0]
    end = find_stop(stops, end_stop)[0]
    print(f"Departure stop: {start_stop}")
    print(f"Arrival stop: {end_stop}")

    startcoord = (float(start[2]) / 1e5, float(start[3]) / 1e5) # lat lon
    endcoord = (float(end[2]) / 1e5, float(end[3]) / 1e5)
    print(startcoord, endcoord)

    cur = first_sample_after
    samples = []
    while cur < last_sample_before:
        if cur.weekday() < 5: # not weekend
            curend = cur + datetime.timedelta(hours=2)
            locs = intr.interpolate_bus_trajectory(cur, curend, linenumber, 1)
            #print(cur, locs)
            departures = find_approaches(startcoord, locs, True)
            arrivals = find_approaches(endcoord, locs, True)
            #print(f"Approaches: {approaches}")
            #print(f"Arrivals: {arrivals}")

            trips = []

            for departure in departures:
                marrivals = list(filter(lambda x: x[0] == departure[0] and x[1] > departure[1], arrivals))
                marrivals = sorted(marrivals, key=lambda x: x[1])
                print(f"{departure[1]} {marrivals[0][1] if len(marrivals) > 0 else 'None'}")
                if len(marrivals) > 0:
                    trips.append((departure[1], marrivals[0][1]))

            samples.append(trips)

        cur = cur + datetime.timedelta(days=1)


    start = datetime.datetime(2025, 5, 31, 8, 0, 0)
    end = datetime.datetime(2025, 5, 31, 9, 5, 0)
    cur = start

    print(f"Sample count: {len(samples)}")

    times = []
    probs = []
    while cur < end:
        prob = probability_late(samples, cur.time())
        print(f"{cur.time()} prob {prob}")
        times.append(cur)
        probs.append(prob)

        cur = cur + datetime.timedelta(seconds=5)

    plt.plot(times, probs)
    plt.savefig("solution.png")
    plt.show()

solve()