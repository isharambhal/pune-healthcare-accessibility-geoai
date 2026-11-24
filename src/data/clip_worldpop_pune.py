"""Clip the WorldPop India raster to the PMC 2025 boundary extent.

Input : data/raw/population/ind_pop_2025_CN_100m_R2025A_v1.tif (not modified)
Output: data/processed/population/worldpop_2025_pmc_clip.tif
"""
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.windows import Window, from_bounds

BOUNDARY = Path("data/raw/boundaries/PMC Electoral Wards 2025.kml")
RASTER = Path("data/raw/population/ind_pop_2025_CN_100m_R2025A_v1.tif")
OUT = Path("data/processed/population/worldpop_2025_pmc_clip.tif")
BUFFER_DEG = 0.01  # about 1 km margin around the boundary extent


def main():
    wards = gpd.read_file(BOUNDARY)
    minx, miny, maxx, maxy = wards.total_bounds
    minx, miny = minx - BUFFER_DEG, miny - BUFFER_DEG
    maxx, maxy = maxx + BUFFER_DEG, maxy + BUFFER_DEG
    print(f"Clip extent: {minx:.4f}, {miny:.4f}, {maxx:.4f}, {maxy:.4f}")

    with rasterio.open(RASTER) as src:
        nodata = src.nodata
        win = from_bounds(minx, miny, maxx, maxy, transform=src.transform)
        # round outwards to whole pixels so no edge pixels are lost
        col_off = int(np.floor(win.col_off))
        row_off = int(np.floor(win.row_off))
        width = int(np.ceil(win.width)) + 1
        height = int(np.ceil(win.height)) + 1
        win = Window(col_off, row_off, width, height)
        data = src.read(1, window=win)
        transform = src.window_transform(win)
        crs = src.crs

    valid = data != nodata
    print(f"Clipped size: {data.shape[1]} columns x {data.shape[0]} rows")
    print(f"Valid pixels: {int(valid.sum())}  Nodata pixels: {int((~valid).sum())}")
    print(f"Sum of valid pixels in this rectangle: {float(data[valid].sum()):,.0f}")
    print("(This rectangle is larger than PMC, so it is NOT the PMC population.)")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        OUT, "w", driver="GTiff", height=data.shape[0], width=data.shape[1],
        count=1, dtype="float32", crs=crs, transform=transform,
        nodata=nodata, compress="lzw",
    ) as dst:
        dst.write(data, 1)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()