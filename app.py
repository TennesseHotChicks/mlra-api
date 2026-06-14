from fastapi import FastAPI
import geopandas as gpd
from shapely.geometry import Point
import requests

app = FastAPI()

# Load MLRA polygons
gdf = gpd.read_file("mlra.geojson")

# Ensure GPS coordinate system
gdf = gdf.to_crs(epsg=4326)

def get_soil_data(lat, lon):

    query = f"""
    SELECT TOP 1
        mu.musym,
        mu.muname
    FROM mapunit mu
    INNER JOIN legend lg ON mu.lkey = lg.lkey
    INNER JOIN SDA_Get_Mukey_from_intersection_with_WktWgs84(
        'point({lon} {lat})'
    ) mukey
    ON mu.mukey = mukey.mukey
    """

    response = requests.post(
        "https://sdmdataaccess.sc.egov.usda.gov/tabular/post.rest",
        json={
            "query": query,
            "format": "JSON"
        }
    )

    data = response.json()

    if "Table" not in data or len(data["Table"]) == 0:
        return None

    row = data["Table"][0]

    return {
        "soil_symbol": row[0],
        "soil_map_unit": row[1]
    }

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

    soil = get_soil_data(lat, lon)

    return {
        "found": True,
        "mlra": clean(row.get("MLRARSYM")),
        "lrr": clean(row.get("LRRSYM")),

        "soil_symbol": soil["soil_symbol"] if soil else None,
        "soil_map_unit": soil["soil_map_unit"] if soil else None
    }

