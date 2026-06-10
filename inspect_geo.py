import geopandas as gpd

gdf = gpd.read_file("mlra.geojson")

print(gdf.columns)