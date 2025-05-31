from glob import glob
import datetime
from shapely.geometry import LineString, Point
from util import get_files_timespan

import tltdata

data_directory = "data"

def get_bus_locations(bus, time_point, datafiles):
    # Find closest file before time_point.
    before_dates = list(filter(lambda x: x[1] <= time_point, datafiles))
    # Find closest file after time_point.
    after_dates = list(filter(lambda x: x[1] > time_point, datafiles))
    # If one of the samples is missing don't try to interpolate.
    if len(before_dates) == 0 or len(after_dates) == 0:
        return None, None
    before = max(before_dates)
    after = min(after_dates)
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

        blocs, alocs = get_bus_locations(bus, curtime, datafiles)
        if blocs is None or alocs is None:
            continue

        startTime = blocs[0]
        startLocations = blocs[1]
        endTime = alocs[0]
        endLocations = alocs[1]

        progress = (curtime - startTime) / (endTime - startTime)

        vehicles = set(startLocations.keys()) & set(endLocations.keys())

        locations = []
        for vehicleId in vehicles:
            beforePoint = Point(startLocations[vehicleId][:2])
            afterPoint = Point(endLocations[vehicleId][:2])
            bb = lineAB.project(beforePoint)
            aa = lineAB.project(afterPoint)
            activeLine = lineAB
            direction = True
            # flip direction if moving backwards in trajectory
            if aa - bb < 0:
                bb = lineBA.project(beforePoint)
                aa = lineBA.project(afterPoint)
                activeLine = lineBA
                direction = False

            curT = bb + progress*(aa-bb)
            locations.append((vehicleId, activeLine.interpolate(curT), direction))
        result.append((locations, curtime))
    return result
            
'''
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
'''