# gps.txt file format
# type, lineid, lat, lon, speed, heading, vehicleid, vehicletype
# type - 1 trolley, 2 bus, 3 tram, 7 nightbus
# vehicletype - Z low
def get_bus_locations(file, bus):
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