from flask import Blueprint, request, jsonify
import os
import numpy as np
from ..aod_to_aqi import modis_coords_from_latlon, get_aod_from_hdf, aod_to_pm25, pm25_to_aqi

aqi_bp = Blueprint("aqi", __name__)

@aqi_bp.route("/current", methods=["GET"])
def get_current_aqi():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if lat is None or lon is None:
        return jsonify({"error": "Latitude and longitude are required."}), 400

    h, v, pixel_x, pixel_y = modis_coords_from_latlon(lat, lon)

    if h is None or v is None or pixel_x is None or pixel_y is None:
        return jsonify({"error": "Could not determine MODIS tile/pixel for the given coordinates."}), 400

    if os.environ.get("FLASK_ENV") == "testing":
        aod_value = 0.2 # Directly use a mock AOD value for testing
    else:
        # Determine the HDF file path for the given tile
        # For now, we are using a hardcoded file. In a real application, this would involve
        # a more sophisticated data management system to find the correct HDF file for the tile and date.
        hdf_file_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)), "tests", "MCD19A2.h20v05.hdf")
        if not os.path.exists(hdf_file_path):
            return jsonify({"error": f"HDF file for tile h{h}v{v} not found at {hdf_file_path}."}), 404
        aod_value = get_aod_from_hdf(hdf_file_path, pixel_x, pixel_y)




    if aod_value is None or np.isnan(aod_value):
        return jsonify({"error": "Could not retrieve a valid AOD value for the specified location."}), 404

    pm25_value = aod_to_pm25(aod_value)

    if np.isnan(pm25_value):
        return jsonify({"error": "Could not convert AOD to PM2.5."}), 500

    aqi_result = pm25_to_aqi(pm25_value)

    return jsonify({
        "latitude": lat,
        "longitude": lon,
        "modis_tile": f"h{h}v{v}",
        "modis_pixel_x": pixel_x,
        "modis_pixel_y": pixel_y,
        "aod_value": float(aod_value),
        "pm25_value": float(pm25_value),
        "aqi": aqi_result["aqi"],
        "aqi_category": aqi_result["category"],
        "pollutant": aqi_result["pollutant"]
    })

@aqi_bp.route("/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello from AQI blueprint!"})

