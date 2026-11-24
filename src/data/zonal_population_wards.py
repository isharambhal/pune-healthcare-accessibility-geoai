"""Ward-level population from the clipped WorldPop raster (zonal sums).

Two methods are compared:
  centre : a pixel belongs to the ward containing its centre point
  super  : each pixel is split into F x F sub-cells; a ward receives the
           fraction of the pixel that falls inside it (area-weighted)
Nodata cells are treated as "no people estimated" and never summed.

Inputs : data/raw/boundaries/PMC Electoral Wards 2025.kml
         data/processed/population/worldpop_2025_pmc_clip.tif
Output : data/processed/population/ward_population_worldpop2025.csv
"""
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from affine import Affine
from rasterio.features import rasterize

BOUNDARY = Path("data/raw/boundaries/PMC Electoral Wards 2025.kml")
RASTER = Path("data/processed/population/worldpop_2025_pmc_clip.tif")
OUT = Path("data/processed/population/ward_population_worldpop2025.csv")
F = 10  # sub-cells per pixel side


def main():
    wards = gpd.read_file(BOUNDARY)
    wards["qwr"] = wards["qwr"].astype(int)
    wards = wards[["qwr", "geometry"]].sort_values("qwr").reset_index(drop=True)

    # Areas must be computed in a projected CRS (metres), not in degrees.
    proj = wards.to_crs(32643)
    wards["area_km2"] = proj.area / 1e6
    overlap_km2 = wards["area_km2"].sum() - proj.union_all().area / 1e6
    print(f"Wards: {len(wards)}  Total area: {wards['area_km2'].sum():.3f} km2")
    print(f"Overlap check (should be about 0): {overlap_km2:.4f} km2")

    with rasterio.open(RASTER) as src:
        data = src.read(1)
        transform = src.transform
        nodata = src.nodata
    is_nodata = data == nodata
    pop = np.where(is_nodata, 0.0, data).astype("float64")
    h, w = pop.shape

    shapes = [(g, int(i)) for g, i in zip(wards.geometry, wards["qwr"])]
    ids_c = rasterize(shapes, out_shape=(h, w), transform=transform,
                      fill=0, dtype="int32")
    ids_f = rasterize(shapes, out_shape=(h * F, w * F),
                      transform=transform * Affine.scale(1 / F),
                      fill=0, dtype="int32")

    rows = []
    for wid in wards["qwr"]:
        pop_centre = pop[ids_c == wid].sum()
        frac = (ids_f == wid).reshape(h, F, w, F).mean(axis=(1, 3))
        pop_super = (pop * frac).sum()
        nodata_share = (frac * is_nodata).sum() / frac.sum()
        rows.append((wid, pop_centre, pop_super, nodata_share))

    df = pd.DataFrame(rows, columns=["qwr", "pop_centre", "pop_area_weighted",
                                     "nodata_share"])
    df = wards[["qwr", "area_km2"]].merge(df, on="qwr")
    df["diff_pct"] = 100 * (df["pop_centre"] - df["pop_area_weighted"]) \
        / df["pop_area_weighted"]
    df["density_per_km2"] = df["pop_area_weighted"] / df["area_km2"]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.round(3).to_csv(OUT, index=False)

    print(f"Total population, centre rule   : {df['pop_centre'].sum():,.0f}")
    print(f"Total population, area-weighted : {df['pop_area_weighted'].sum():,.0f}")
    print(f"Largest ward difference between methods: "
          f"{df['diff_pct'].abs().max():.2f} %")
    cols = ["qwr", "area_km2", "pop_area_weighted", "density_per_km2",
            "nodata_share"]
    print("\nHighest density wards:")
    print(df.nlargest(5, "density_per_km2")[cols].round(2).to_string(index=False))
    print("\nLowest density wards:")
    print(df.nsmallest(5, "density_per_km2")[cols].round(2).to_string(index=False))
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()