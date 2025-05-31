#!/usr/bin/env python3

import tltdata
import datetime
import interpolate as intr
import math
import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
from pyproj import Transformer

departure_tolerance = 50 # meters
deadline_hour = 9 # hour of meeting
deadline_minute = 5 # minute of meeting
deadline_second = 0 # second of meeting
seconds_home2bus = 300 # seconds from home to bus station
seconds_stop2work = 240 # seconds from arrival stop to meeting
start_stop = "Zoo" # start stop name
end_stop = "Toompark" # end stop name
linenumber = "8" # bus line number for travel
first_sample_after = datetime.datetime(2025, 5, 3, 8, 0, 0) # datetime before which not to include samples
last_sample_before = datetime.datetime(2025, 5, 30, 10, 0, 0) # datetime after which not to include samples
trajectory_hours = 2 # time window after first_sample_after to consider
verbose = True # print additional info
directionAB = True # False - direction BA

def find_stop(stops, name):
    """Given list of stops, find a stop."""
    matches = []
    for stop in stops:
        if len(stop) < 6:
            continue
        if stop[5] == name:
            matches.append(stop)
    return matches

def find_approaches(target, trajectory, adirection):
    """Find when bus gets within tolerance from target in specific direction"""
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
            # Check if within tolerance from target
            dist = math.sqrt((transcoord[0]-target3301[0])**2 + (transcoord[1]-target3301[1])**2)
            if dist < departure_tolerance:
                ret.append((v, frametime))
                if v not in approaches:
                    approaches[v] = [frametime]
                else:
                    approaches[v].append(frametime)

        transformed.append(newcoords)

    return ret

def find_soonest_arrival(trips, time_point):
    """Given day sample, return soonest arrival datetime at destination."""
    for trip in trips:
        if trip[0] >= time_point:
            return trip[1]
    return None

def check_late(trips, left_home_time, deadline):
    """Given day sample, return True if was late for a given deadline and departure from home."""
    left_dt = trips[0][0].replace(hour=left_home_time.hour, minute=left_home_time.minute, second=left_home_time.second)
    bus_stop_time = left_dt + datetime.timedelta(seconds=seconds_home2bus)
    arrival = find_soonest_arrival(trips, bus_stop_time)
    if arrival is None:
        return True
    else:
        return arrival > (deadline - datetime.timedelta(seconds=seconds_stop2work))
    
def probability_late(samples, left_home_time):
    """Given day samples, return probability (0-1) of being late when leaving home at specific time."""
    count_late = 0
    count = 0
    for sample in samples:
        deadline = sample[0][0].replace(hour = deadline_hour, minute=deadline_minute, second=deadline_second)
        waslate = check_late(sample, left_home_time, deadline)
        count_late += 1 if waslate else 0
        count += 1
    return float(count_late)/count


def solve():
    """Solve the task: plot probability graph."""
    # Find departure and arrival stops
    stops = tltdata.get_stops()
    start = find_stop(stops, start_stop)[0]
    end = find_stop(stops, end_stop)[0]

    if verbose:
        print(f"Departure stop: {start_stop}")
        print(f"Arrival stop: {end_stop}")

    # LatLon coordinates of the stops
    startcoord = (float(start[2]) / 1e5, float(start[3]) / 1e5) # lat lon
    endcoord = (float(end[2]) / 1e5, float(end[3]) / 1e5)

    # Iterate every weekday in the configured timeframe
    cur = first_sample_after
    samples = []
    while cur < last_sample_before:
        if cur.weekday() < 5: # not weekend
            if verbose:
                print(f"Processing {cur.date()}")
            # Get interpolated trajectory
            curend = cur + datetime.timedelta(hours=trajectory_hours)
            locs = intr.interpolate_bus_trajectory(cur, curend, linenumber, 1)
            # Find when a bus is close to departure station
            departures = find_approaches(startcoord, locs, directionAB)
            # Find when a bus is close to arrival station
            arrivals = find_approaches(endcoord, locs, directionAB)

            trips = []

            # Find matching arrivals at destination for each departure
            for departure in departures:
                marrivals = list(filter(lambda x: x[0] == departure[0] and x[1] > departure[1], arrivals))
                marrivals = sorted(marrivals, key=lambda x: x[1])
                if verbose:
                    print(f"Found departure: {departure[1]} Arrival: {marrivals[0][1] if len(marrivals) > 0 else 'None'}")
                if len(marrivals) > 0:
                    trips.append((departure[1], marrivals[0][1]))

            # save sample
            samples.append(trips)

        cur = cur + datetime.timedelta(days=1)

    # We've now gathered all samples, now calculate probability graph

    start = datetime.datetime(2025, 5, 31, 8, 0, 0)
    end = datetime.datetime(2025, 5, 31, 9, 5, 0)
    cur = start

    print(f"Sample count: {len(samples)}")

    times = []
    probs = []
    while cur < end:
        prob = probability_late(samples, cur.time())
        times.append(cur)
        probs.append(prob * 100.0)

        cur = cur + datetime.timedelta(seconds=1)

    print("Plotting solution to solution.png")
    plt.plot(times, probs)
    plt.title("Probability of being late")
    plt.xlabel("Departure time")
    plt.ylabel("Probability (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("solution.png")
    plt.show()

solve()