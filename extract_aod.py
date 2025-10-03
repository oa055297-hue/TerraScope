from pyhdf.SD import SD, SDC
import numpy as np

def extract_aod_from_hdf(file_path):
    try:
        hdf = SD(file_path, SDC.READ)

        # List available SDS datasets
        sds_info = hdf.datasets()
        print("Available SDS datasets:")
        for sds_name in sds_info:
            print(sds_name)

        # Common SDS names for AOD in MODIS MCD19A2
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

        # Get attributes for scaling and fill value
        attrs = sds.attributes()
        scale_factor = attrs.get("scale_factor", 1.0)
        add_offset = attrs.get("add_offset", 0.0)
        _FillValue = attrs.get("_FillValue", -9999)

        # Apply scale and offset, handle fill value
        aod_data = aod_data.astype(np.float32)
        aod_data[aod_data == _FillValue] = np.nan
        aod_data = aod_data * scale_factor + add_offset

        print(f"Successfully extracted AOD data from {aod_sds_name} with shape: {aod_data.shape}")
        print(f"Min AOD: {np.nanmin(aod_data)}, Max AOD: {np.nanmax(aod_data)}")
        print(f"Mean AOD: {np.nanmean(aod_data)}")

        hdf.end()
        return aod_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    hdf_file = "MCD19A2.A2025243.h13v01.061.2025245213645.hdf"
    aod_data = extract_aod_from_hdf(hdf_file)
    if aod_data is not None:
        # Further processing or visualization can be added here
        pass

