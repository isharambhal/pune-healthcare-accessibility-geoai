"""Checks that the core GIS libraries import and work together."""
import geopandas as gpd
from shapely.geometry import Point


def test_geopandas_basic_operation():
    gdf = gpd.GeoDataFrame(
        {"name": ["test"]},
        geometry=[Point(73.85, 18.52)],  # near central Pune
        crs="EPSG:4326",
    )
    projected = gdf.to_crs("EPSG:32643")  # WGS 84 / UTM zone 43N
    assert projected.crs.to_epsg() == 32643
    assert projected.geometry.iloc[0].x > 0
