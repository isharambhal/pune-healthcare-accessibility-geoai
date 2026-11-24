
from pathlib import Path
from itertools import combinations

import geopandas as gpd

PROJECT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT / "data/processed/healthcare/"
    "healthcare_inventory_preliminary.gpkg"
)

gdf = gpd.read_file(INPUT_FILE).to_crs("EPSG:32643")
gdf = gdf.set_index("source_key")

# -----------------------------------------
# 1. Ruby Hall Clinic
# -----------------------------------------

print("\n========== DUP_G001: RUBY HALL CLINIC ==========")

ruby_keys = [
    "node/10172977877",
    "node/7649461743",
    "way/53098668"
]

for key in ruby_keys:
    print(key, "Geometry:", gdf.loc[key].geometry.geom_type)

ruby_points = [
    key for key in ruby_keys
    if gdf.loc[key].geometry.geom_type == "Point"
]

for a, b in combinations(ruby_points, 2):
    distance = gdf.loc[a].geometry.distance(
        gdf.loc[b].geometry
    )
    print(f"Distance {a} to {b}: {distance:.2f} m")

ruby_polygon = gdf.loc["way/53098668"].geometry

for key in ruby_points:
    point = gdf.loc[key].geometry
    print(
        f"{key} inside Ruby Hall polygon:",
        ruby_polygon.covers(point)
    )

# -----------------------------------------
# 2. Shinde Hospitals
# -----------------------------------------

print("\n========== DUP_G002: SHINDE HOSPITALS ==========")

shinde_keys = [
    "node/10219198235",
    "node/10219230632",
    "node/10219230642"
]

distance_sums = {key: 0.0 for key in shinde_keys}

for a, b in combinations(shinde_keys, 2):

    distance = gdf.loc[a].geometry.distance(
        gdf.loc[b].geometry
    )

    distance_sums[a] += distance
    distance_sums[b] += distance

    print(f"Distance {a} to {b}: {distance:.2f} m")

print("\nTotal distance to other points:")

for key, value in distance_sums.items():
    print(key, round(value, 2), "m")

medoid = min(distance_sums, key=distance_sums.get)

print("\nProvisional representative point:", medoid)

# -----------------------------------------
# 3. Jupiter Hospital
# -----------------------------------------

print("\n========== DUP_G034: JUPITER HOSPITAL ==========")

key_a = "way/1410820103"
key_b = "way/652021497"

polygon_a = gdf.loc[key_a].geometry
polygon_b = gdf.loc[key_b].geometry

area_a = polygon_a.area
area_b = polygon_b.area

intersection = polygon_a.intersection(polygon_b).area

print("Polygon A area:", round(area_a, 2), "m²")
print("Polygon B area:", round(area_b, 2), "m²")
print("Intersection area:", round(intersection, 2), "m²")

print(
    "Polygon A covered by B:",
    round(intersection / area_a * 100, 2), "%"
)

print(
    "Polygon B covered by A:",
    round(intersection / area_b * 100, 2), "%"
)

print(
    "A covers B:",
    polygon_a.covers(polygon_b)
)

print(
    "B covers A:",
    polygon_b.covers(polygon_a)
)

print("\nVerification completed.")
