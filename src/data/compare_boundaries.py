
from pathlib import Path
import geopandas as gpd

PROJECT = Path(__file__).resolve().parents[2]
BOUNDARY_DIR = PROJECT / "data" / "raw" / "boundaries"

file_2017 = BOUNDARY_DIR / "Pune Electoral Wards Map - 2017.kml"
file_2025 = BOUNDARY_DIR / "PMC Electoral Wards 2025.kml"

# Read both datasets
wards_2017 = gpd.read_file(file_2017)
wards_2025 = gpd.read_file(file_2025)

# Reproject to UTM Zone 43N for area calculations
wards_2017 = wards_2017.to_crs("EPSG:32643")
wards_2025 = wards_2025.to_crs("EPSG:32643")

# Combine ward polygons into overall study boundaries
boundary_2017 = wards_2017.geometry.union_all()
boundary_2025 = wards_2025.geometry.union_all()

# Calculate areas in square kilometres
area_2017 = boundary_2017.area / 1_000_000
area_2025 = boundary_2025.area / 1_000_000

intersection = boundary_2017.intersection(boundary_2025)
shared_area = intersection.area / 1_000_000

outside_2017 = boundary_2017.difference(boundary_2025).area / 1_000_000
outside_2025 = boundary_2025.difference(boundary_2017).area / 1_000_000

union_area = boundary_2017.union(boundary_2025).area / 1_000_000
iou = shared_area / union_area

print("\n========== PMC BOUNDARY COMPARISON ==========")

print(f"2017 wards: {len(wards_2017)}")
print(f"2025 wards: {len(wards_2025)}")

print(f"\n2017 total area: {area_2017:.3f} sq. km")
print(f"2025 total area: {area_2025:.3f} sq. km")

print(f"Shared area: {shared_area:.3f} sq. km")
print(f"2017 area outside 2025: {outside_2017:.3f} sq. km")
print(f"2025 area outside 2017: {outside_2025:.3f} sq. km")

print(f"\nIntersection over Union (IoU): {iou:.4f}")

print("\n2017 ward fields:", wards_2017.columns.tolist())
print("2025 ward fields:", wards_2025.columns.tolist())
