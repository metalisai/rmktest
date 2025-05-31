import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import xyzservices.providers as xyz
from matplotlib.animation import FuncAnimation

# This code was used to confirm that the interpolation was correct.
#   Not part of solution.

def animate_locations(locs):
    fig = plt.figure()

    tiler = cimgt.OSM()

    ax = plt.axes(projection=tiler.crs)
    ax.set_extent([24.60, 24.89, 59.36, 59.51], crs=ccrs.PlateCarree())
    ax.add_image(tiler, 11)

    # Initialize a scatter plot for multiple points
    scat = ax.scatter([], [], color='red', s=5, transform=ccrs.PlateCarree())

    def init():
        scat.set_offsets(np.empty((0, 2)))
        return scat,

    def update(frame):
        lat_lons = [x[1].coords[0] for x in locs[frame]]
        print(f"latlons {lat_lons}")
        if len(lat_lons) > 0:
            lats, lons = zip(*lat_lons)  # Separate into two lists
            scat.set_offsets(list(zip(lons, lats)))  # Note: set_offsets expects (x, y) = (lon, lat)
        else:
            scat.set_offsets(np.empty((0, 2)))
        return scat,

    ani = FuncAnimation(fig, update, frames=len(locs), init_func=init, blit=True, repeat=False, interval=500)

    #plt.show()
    ani.save('animation.mp4', writer='ffmpeg', fps=2)