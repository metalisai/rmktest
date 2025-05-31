import requests
import polyline

# gps.txt file format
# type, lineid, lat, lon, speed, heading, vehicleid, vehicletype
# type - 1 trolley, 2 bus, 3 tram, 7 nightbus
# vehicletype - Z low
def get_bus_locations(file, bus):
    """Given gps.txt file location, return locations of all active busses on specific line number."""
    results = {}
    with open(file, "r") as datafile:
        data = datafile.readlines()
        for line in data:
            cols = line.split(",")
            if cols[0] == "2" and cols[1] == bus:
                lon = float(cols[2]) / 1e6
                lat = float(cols[3]) / 1e6
                heading = int(cols[5])
                vehicleid = int(cols[6])
                results[vehicleid] = (lat, lon, heading)
    return results

def get_bus_trajectory(bus):
    """Return WGS84 polyline of a specific bus line."""
    url = f"https://transport.tallinn.ee/data/tallinna-linn_bus_{bus}.txt"
    response = requests.get(url)
    if response.status_code == 200:
        trajectory_data = response.text
    else:
        raise Exception("Failed to fetch trajectory data.")
    traj_datas = trajectory_data.split("\r\n")
    traj_ab = polyline.decode(traj_datas[1])
    traj_ba = polyline.decode(traj_datas[4])
    # NOTE: there might be more subtrajectories
    return traj_ab, traj_ba

# stops.txt file format
# ID;SiriID;Lat;Lng;Stops;Name;Info;Street;Area;City;
def get_stops():
    """Return all bus stops in Tallinn."""
    url = "https://transport.tallinn.ee/data/stops.txt"
    response = requests.get(url)
    if response.status_code == 200:
        stops_data = response.text
    else:
        raise Exception("Failed to fetch stops data.")
    lines = [x.strip().split(';') for x in stops_data.split("\n")]
    return lines