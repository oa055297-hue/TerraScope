
import earthaccess
import os

# Earthdata credentials should be set up via earthaccess.login() or .netrc
# For this script, we assume earthaccess.login() has been called previously

short_name = 'MCD19A2'
version = '061'
temporal_range = ('2025-09-29', '2025-09-30')
# Bounding box for tile h20v05 (approximate, based on previous search results)
# This bounding box covers the area where Cairo (30.0444, 31.2357) is located.
# (min_lon, min_lat, max_lon, max_lat)
bounding_box = (22.9899, 29.8804, 39.1769, 40.0199)

print(f"Searching for {short_name} data for tile h20v05...")
results = earthaccess.search_data(
    short_name=short_name,
    version=version,
    temporal=temporal_range,
    bounding_box=bounding_box,
    cloud_hosted=True
)

h20v05_granule = None
for g in results:
    # Check if the granule's data link contains 'h20v05'
    # data_links() returns a list of URLs
    if g.data_links() and 'h20v05' in g.data_links()[0]:
        h20v05_granule = g
        break

if h20v05_granule:
    print(f"Found granule for h20v05: {h20v05_granule.data_links()[0]}")
    print("Downloading granule...")
    downloaded_files = earthaccess.download([h20v05_granule])
    if downloaded_files:
        print(f"Downloaded file: {downloaded_files[0]}")
        # Rename the file to a generic name for easier use in aod_to_aqi.py
        # This assumes only one file is downloaded.
        original_filepath = downloaded_files[0]
        new_filename = "MCD19A2.h20v05.hdf"
        # Move the file to the current directory and rename it
        os.rename(original_filepath, new_filename)
        print(f"Renamed {original_filepath} to {new_filename}")
    else:
        print("Download failed.")
else:
    print("No h20v05 granule found for the specified criteria.")

