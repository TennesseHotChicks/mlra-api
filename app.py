from fastapi import FastAPI
import geopandas as gpd
from shapely.geometry import Point

app = FastAPI()

# Load MLRA polygons
gdf = gpd.read_file("mlra.geojson")

# Ensure GPS coordinate system
gdf = gdf.to_crs(epsg=4326)

@app.get("/lookup")
def lookup(lat: float, lon: float):

    point = Point(lon, lat)

    matches = gdf[gdf.contains(point)]

    if matches.empty:
        return {
            "found": False
        }

    row = matches.iloc[0]

    def clean(v):
        if v is None:
            return None
        try:
            return v.item()  # converts numpy types → python types
        except:
            return str(v)

    return {
        "found": True,
        "mlra": clean(row.get("MLRARSYM")),
        "lrr": clean(row.get("LRRSYM"))
    }
