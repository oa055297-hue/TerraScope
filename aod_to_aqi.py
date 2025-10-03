
import numpy as np
from pyhdf.SD import SD, SDC
from modis_sinusoidal_tile_converter.sinusoidal import Sinusoidal

def modis_coords_from_latlon(lat, lon, image_pixels=1200):
    """Converts latitude/longitude to MODIS tile (h, v) and pixel coordinates using the library."""
    # The library's GCS2ICSTile returns (vertical_tile, horizontal_tile, line, sample)
    # where line and sample are pixel coordinates. It also takes 'grid' as a parameter.
    # For 1200x1200 pixel tiles, the grid resolution is 1km.
    v, h, pixel_y, pixel_x = Sinusoidal.GCS2ICSTile(lat, lon, grid="1km")
    return h, v, int(round(pixel_x)), int(round(pixel_y))

def get_aod_from_hdf(file_path, pixel_x, pixel_y):
    """Extracts AOD value from an HDF file at specified pixel coordinates."""
    try:
        hdf = SD(file_path, SDC.READ)
        sds_info = hdf.datasets()

        aod_sds_name = None
        possible_aod_sds_names = [
            'Optical_Depth_055',
            'Optical_Depth_047',
            'AOD_550_Dark_Target_Deep_Blue_Combined',
            'Optical_Depth_Land_And_Ocean',
            'AOD_550_Dark_Target_Deep_Blue_Combined_Mean',
            'AOD_550_Dark_Target_Deep_Blue_Combined_StdDev',
            'AOD_550'
        ]

        for name in possible_aod_sds_names:
            if name in sds_info:
                aod_sds_name = name
                break

        if not aod_sds_name:
            print("Error: Could not find a suitable AOD SDS dataset.")
            return None

        sds = hdf.select(aod_sds_name)
        aod_data = sds.get()

        attrs = sds.attributes()
        scale_factor = attrs.get("scale_factor", 1.0)
        add_offset = attrs.get("add_offset", 0.0)
        _FillValue = attrs.get("_FillValue", -9999)

        # Apply scale and offset, handle fill value
        aod_data = aod_data.astype(np.float32)
        aod_data[aod_data == _FillValue] = np.nan
        aod_data = aod_data * scale_factor + add_offset

        # AOD data might have multiple layers (e.g., orbits). Take the first one for simplicity.
        # The shape is (num_orbits, height, width). We need to select a specific orbit or average.
        # For now, let's assume we take the first orbit's data.
        if aod_data.ndim == 3:
            aod_value = aod_data[0, pixel_y, pixel_x] # Accessing [orbit_index, row, col]
        elif aod_data.ndim == 2:
            aod_value = aod_data[pixel_y, pixel_x] # Accessing [row, col]
        else:
            print(f"Unexpected AOD data dimension: {aod_data.ndim}")
            return None

        hdf.end()
        return aod_value

    except Exception as e:
        print(f"An error occurred while extracting AOD: {e}")
        return None

def aod_to_pm25(aod_value, conversion_factor=0.2):
    """Converts AOD to PM2.5 concentration (ug/m^3) using a simple conversion factor.
    This is a placeholder and needs to be refined with more accurate models.
    """
    if np.isnan(aod_value):
        return np.nan
    # This is a highly simplified conversion. Real-world conversion is complex.
    # A common range for AOD to PM2.5 conversion factor is 0.2 to 0.6
    # For a placeholder, we use 0.2
    return aod_value * conversion_factor * 100 # Multiply by 100 to get a more realistic PM2.5 range

def pm25_to_aqi(pm25_value):
    """Converts PM2.5 concentration (ug/m^3) to AQI using EPA standards.
    Source: https://www.airnow.gov/aqi/aqi-calculator/
    """
    if np.isnan(pm25_value):
        return {"aqi": None, "category": "N/A", "pollutant": "PM2.5"}

    # EPA AQI breakpoints for PM2.5 (24-hour)
    # Concentrations are in ug/m^3
    # AQI = [(I_high - I_low) / (C_high - C_low)] * (C - C_low) + I_low

    breakpoints = [
        (0.0, 12.0, 0, 50, "Good"),
        (12.1, 35.4, 51, 100, "Moderate"),
        (35.5, 55.4, 101, 150, "Unhealthy for Sensitive Groups"),
        (55.5, 150.4, 151, 200, "Unhealthy"),
        (150.5, 250.4, 201, 300, "Very Unhealthy"),
        (250.5, 500.4, 301, 500, "Hazardous")
    ]

    for C_low, C_high, I_low, I_high, category in breakpoints:
        if C_low <= pm25_value <= C_high:
            aqi = ((I_high - I_low) / (C_high - C_low)) * (pm25_value - C_low) + I_low
            return {"aqi": int(round(aqi)), "category": category, "pollutant": "PM2.5"}
    
    if pm25_value > 500.4:
        return {"aqi": 500, "category": "Hazardous", "pollutant": "PM2.5"} # Capped at 500

    return {"aqi": None, "category": "N/A", "pollutant": "PM2.5"}


if __name__ == "__main__":
    # Example usage:
    lat, lon = 30.0444, 31.2357  # Cairo coordinates
    print(f"Converting Lat: {lat}, Lon: {lon} to MODIS Sinusoidal...")
    h, v, pixel_x, pixel_y = modis_coords_from_latlon(lat, lon)
    print(f"MODIS Tile (h,v): ({h},{v}), Pixel (x,y): ({pixel_x},{pixel_y})")

    # This part assumes you have the correct HDF file for the calculated tile (h,v)
    # For demonstration, we'll use the previously downloaded file.
    hdf_file = "MCD19A2.h20v05.hdf"
    if h is not None and v is not None and pixel_x is not None and pixel_y is not None:
        # Note: The downloaded HDF file might not correspond to the exact tile (h,v) for Cairo.
        # This is a placeholder for actual data retrieval based on tile.
        print(f"Attempting to extract AOD from {hdf_file} at pixel ({pixel_x}, {pixel_y})...")
        aod_value = get_aod_from_hdf(hdf_file, pixel_x, pixel_y)

        if aod_value is not None and not np.isnan(aod_value):
            print(f"Extracted AOD value: {aod_value}")
            pm25 = aod_to_pm25(aod_value)
            print(f"Converted PM2.5: {pm25} ug/m^3")
            aqi_result = pm25_to_aqi(pm25)
            print(f"AQI Result: {aqi_result}")
        else:
            print("Could not retrieve a valid AOD value.")
    else:
        print("Coordinates are outside valid MODIS tile/pixel range or could not be determined.")

