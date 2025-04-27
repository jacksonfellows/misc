import rasterio
import rasterio.warp
import matplotlib.pyplot as plt
import numpy as np
import flowpath_wrapper
from matplotlib.animation import FuncAnimation
import click
import math

def load_data(fdr_path, dem_path):
    data = {}
    with rasterio.open(fdr_path) as src:
        data["src"] = src
        fdr_data = src.read(1)
        assert fdr_data.dtype == np.dtype("uint8")
        data["fdr"] = fdr_data
    with rasterio.open(dem_path) as src:
        dem_data = src.read(1)
        data["dem"] = dem_data
    assert data["fdr"].shape == data["dem"].shape
    return data

def lat_lon_to_ij(src, lat, lon):
    x, y = rasterio.warp.transform("EPSG:4326", src.crs, [lon], [lat])
    i, j = src.index(x[0], y[0])
    return i, j

def ij_to_lat_lon(src, i, j):
    x, y = src.xy(i, j)
    if type(x) != np.ndarray:
        x,y = [x], [y]
    lon, lat = rasterio.warp.transform(src.crs, "EPSG:4326", x, y)
    return lat, lon

def flowpath(fdr, i, j):
    # 1 Flow is to the east
    # 2 Flow is to the southeast
    # 4 Flow is to the south
    # 8 Flow is to the southwest
    # 16 Flow is to the west
    # 32 Flow is to the northwest
    # 64 Flow is to the north
    # 128 Flow is to the northeast

    # i is row, j is column
    # assume +i => down (N), -i => up (S)
    #        +j => right (E), -j => left (W)

    di = {
        1: 0,
        2: 1,
        4: 1,
        8: 1,
        16: 0,
        32: -1,
        64: -1,
        128: -1,
    }
    dj= {
        1: 1,
        2: 1,
        4: 0,
        8: -1,
        16: -1,
        32: -1,
        64: 0,
        128: 1,
    }
    path = []
    while 1:
        if (i,j) in path:
            print("I've been here before!")
            break
        if not (0 <= i < fdr.shape[0] and 0 <= j < fdr.shape[1]):
            print("Out-of-bounds")
            break
        path.append((i,j))
        if fdr[i,j] == 0 or fdr[i,j] == 255:
            # Not sure what the difference between 0 and 255 is
            print("Hit sink")
            break
        i, j = i + di[fdr[i,j]], j + dj[fdr[i,j]]
    ii, jj = np.zeros(len(path), dtype="int"), np.zeros(len(path), dtype="int")
    for k,(i,j) in enumerate(path):
        ii[k] = i
        jj[k] = j
    return ii,jj

@click.command()
@click.option('--fdr-path', required=True, help='Path to the FDR file.')
@click.option('--dem-path', required=True, help='Path to the DEM file.')
@click.option('--lat', type=float, required=True, help='Center latitude.')
@click.option('--lon', type=float, required=True, help='Center longitude.')
@click.option('--radius-deg', type=float, required=True, help='Radius in degrees.')
@click.option('--n', default=10, help='Number of paths to generate.')
@click.option('--decimate', default=10, help="Decimation factor.")
@click.option('--seed', default=42, help='Random seed.')
@click.option('--fps', default=600)
def main(fdr_path, dem_path, lat, lon, radius_deg, n, decimate, seed, fps):
    print("Loading data...")
    data = load_data(fdr_path, dem_path)
    rng = np.random.default_rng(seed)
    plt.gca().set_aspect("equal")
    colori = np.arange(n)
    rng.shuffle(colori)
    fig, ax = plt.subplots()
    ax.set_aspect("equal")
    cmap = plt.get_cmap("gist_rainbow", n)  # Use a colormap with n distinct colors
    lines = []
    paths = []

    # Precompute paths and initialize lines
    for idx in range(n):
        valid_point = False
        while not valid_point:
            # Generate random point uniformly in a circle using polar coordinates.
            theta = rng.uniform(0, 2*math.pi)
            r = radius_deg * math.sqrt(rng.uniform(0, 1))
            cand_lat = lat + r * math.sin(theta)
            cand_lon = lon + r * math.cos(theta)
            i, j = lat_lon_to_ij(data["src"], cand_lat, cand_lon)
            if 0 <= i < data["src"].shape[0] and 0 <= j < data["src"].shape[1] and data["dem"][i, j] > 0:
                valid_point = True
        # Get flowpath
        print(f"Computing flowpath {idx}...")
        ii, jj = flowpath_wrapper.call_flowpath(data["fdr"], i, j)
        ii, jj = ii[::decimate], jj[::decimate]  # Decimate!
        # Transform to lat,lon coords
        path_lats, path_lons = ij_to_lat_lon(data["src"], ii, jj)
        paths.append((path_lats, path_lons))
        color = cmap(colori[idx])  # Get the color for the current path
        line, = ax.plot([], [], color=color)
        lines.append(line)

    assert len(lines) == n
    assert len(paths) == n

    # Set bounds
    ax.set_xlim(min(min(path[1]) for path in paths), max(max(path[1]) for path in paths))
    ax.set_ylim(min(min(path[0]) for path in paths), max(max(path[0]) for path in paths))

    def init():
        return lines
    
    i = 0
    j = 0

    def update(_):
        nonlocal i
        nonlocal j
        if j > len(paths[i][0]):
            i += 1
            j = 0
        lines[i].set_data(paths[i][1][:j], paths[i][0][:j])
        j += 1
        return lines[i],

    total_frames = sum(len(path[0]) for path in paths)
    print(f"Creating animation w/ {total_frames=}...")
    ani = FuncAnimation(fig, update, frames=total_frames, init_func=init, blit=True)
    ani.save("rain.mov", fps=fps)

if __name__ == "__main__":
    main()
