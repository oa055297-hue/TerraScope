import pytest
from src.main import create_app
from src.aod_to_aqi import modis_coords_from_latlon, get_aod_from_hdf, aod_to_pm25, pm25_to_aqi
import os
import numpy as np

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# Mock the HDF file for testing purposes
@pytest.fixture(autouse=True)
def mock_hdf_file(monkeypatch):
    # Mock get_aod_from_hdf to return a controlled value
    def mock_get_aod_from_hdf_func(file_path, pixel_x, pixel_y):
        # Simulate a valid AOD value for testing
        return 0.2

    monkeypatch.setattr("src.routes.aqi.get_aod_from_hdf", mock_get_aod_from_hdf_func)
    monkeypatch.setattr("src.aod_to_aqi.get_aod_from_hdf", mock_get_aod_from_hdf_func)


def test_aqi_endpoint_success(client):
    # Test with valid coordinates (e.g., Cairo)
    response = client.get("/aqi/current?lat=30.0444&lon=31.2357")
    assert response.status_code == 200
    data = response.get_json()
    assert data["latitude"] == 30.0444
    assert data["longitude"] == 31.2357
    assert data["aqi"] == 0  # Based on mock AOD of 0.2 and new conversion model (PM2.5 = 0, AQI = 0)
    assert data["aqi_category"] == "Good"
    assert data["pollutant"] == "PM2.5"

def test_aqi_endpoint_missing_params(client):
    response = client.get("/aqi/current?lat=30.0444")
    assert response.status_code == 400
    assert response.get_json() == {"error": "Latitude and longitude are required."}

    response = client.get("/aqi/current?lon=31.2357")
    assert response.status_code == 400
    assert response.get_json() == {"error": "Latitude and longitude are required."}

    response = client.get("/aqi/current")
    assert response.status_code == 400
    assert response.get_json() == {"error": "Latitude and longitude are required."}

def test_aod_to_pm25_conversion():
    # Test with a known AOD value
    aod = 0.2
    pm25 = aod_to_pm25(aod)
    assert np.isclose(pm25, 0.0) # 1.64 * 0.2 - 5.14 = -4.812, capped at 0

    aod = 0.5
    pm25 = aod_to_pm25(aod)
    assert np.isclose(pm25, 0.0) # 1.64 * 0.5 - 5.14 = -4.32, capped at 0

def test_pm25_to_aqi_conversion():
    # Test different PM2.5 values against EPA breakpoints
    # Good
    aqi_result = pm25_to_aqi(5.0)
    assert aqi_result["aqi"] == 21
    assert aqi_result["category"] == "Good"

    # Moderate
    aqi_result = pm25_to_aqi(20.0)
    assert aqi_result["aqi"] == 68
    assert aqi_result["category"] == "Moderate"

    # Unhealthy for Sensitive Groups
    aqi_result = pm25_to_aqi(40.0)
    assert aqi_result["aqi"] == 112
    assert aqi_result["category"] == "Unhealthy for Sensitive Groups"

    # Hazardous (capped at 500)
    aqi_result = pm25_to_aqi(600.0)
    assert aqi_result["aqi"] == 500
    assert aqi_result["category"] == "Hazardous"

def test_modis_coords_from_latlon():
    # Test with Cairo coordinates
    lat, lon = 30.0444, 31.2357
    h, v, pixel_x, pixel_y = modis_coords_from_latlon(lat, lon)
    assert h == 20
    assert v == 5
    assert pixel_x == 844
    assert pixel_y == 1194

