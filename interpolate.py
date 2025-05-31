import polyline
import requests
from glob import glob
import os
import datetime
from shapely.geometry import LineString, Point

import tltdata

data_directory = "data"

def list_data_files(dir):
    files = glob(f"{dir}/*.txt")
    rep1 = os.path.join(f"{dir}", "file_")
    ret = []
    for file in files:
        date_str = file.replace(f"{rep1}", "").replace(".txt", "")
        date = datetime.datetime.strptime(date_str, "%Y%m%d_%H%M%S")
        # The files use UTC time, need to add 3 hours
        date = date + datetime.timedelta(hours=3)
        ret.append((file, date))
    return ret

def get_files_timespan(dir, starttime, endtime):
    all_files = list_data_files(dir)
    filtered_files = filter(lambda x: x[1] > starttime and x[1] < endtime, all_files)
    return list(filtered_files)

def get_bus_locations(bus, time_point, datafiles):
    # Find closest file before.
    before_dates = list(filter(lambda x: x[1] <= time_point, datafiles))
    after_dates = list(filter(lambda x: x[1] > time_point, datafiles))
    if len(before_dates) == 0 or len(after_dates) == 0:
        return None, None
    before = max(before_dates)
    after = min(after_dates)
    #print(f"before {before} after {after}")
    before_locations = (before[1], tltdata.get_bus_locations(before[0], bus))
    after_locations = (after[1], tltdata.get_bus_locations(after[0], bus))
    return before_locations, after_locations

def interpolate_bus_trajectory(starttime, endtime, bus, resolution):
    traj_ab, traj_ba = tltdata.get_bus_trajectory(bus)
    result = []

    curtime = starttime
    datafiles = get_files_timespan(data_directory, starttime, endtime)
    lineAB = LineString(traj_ab)
    lineBA = LineString(traj_ba)
    while curtime < endtime:
        curtime = curtime + datetime.timedelta(seconds=resolution)

        #print(curtime)

        blocs, alocs = get_bus_locations(bus, curtime, datafiles)
        if blocs is None or alocs is None:
            continue

        startTime = blocs[0]
        #print(startTime)
        startLocations = blocs[1]
        endTime = alocs[0]
        endLocations = alocs[1]

        progress = (curtime - startTime) / (endTime - startTime)

        vehicles = set(startLocations.keys()) & set(endLocations.keys())

        #print(f"progress {progress}")
        locations = []
        for vehicleId in vehicles:
            beforePoint = Point(startLocations[vehicleId][:2])
            afterPoint = Point(endLocations[vehicleId][:2])
            bb = lineAB.project(beforePoint)
            aa = lineAB.project(afterPoint)
            activeLine = lineAB
            # flip direction if moving backwards in trajectory
            if aa - bb < 0:
                bb = lineBA.project(beforePoint)
                aa = lineBA.project(afterPoint)
                activeLine = lineBA
            #print(f"{bb} -> {aa}")

            curT = bb + progress*(aa-bb)
            #print(f"{vehicleId} {activeLine.interpolate(curT)}")
            locations.append((vehicleId, activeLine.interpolate(curT)))
        result.append(locations)
    return result
            

def xx():
    #interpolate_bus_trajectory(None, None, "83", 5)

    start = datetime.datetime(2025, 5, 29, 10, 0, 0)
    end = datetime.datetime(2025, 5, 29, 12, 59, 59)
    relevant_files = get_files_timespan("data", start, end)

    curtime = datetime.datetime.now() - datetime.timedelta(days=2)
    #get_bus_locations("83", curtime, relevant_files)

    locs = interpolate_bus_trajectory(start, end, "83", 5)
    print(locs)

    import visualize
    visualize.animate_locations(locs)

#xx()