
import h5py
import numpy as np
import os

def create_dummy_hdf(file_path):
    with h5py.File(file_path, 'w') as f:
        # Create a dummy dataset for AOD
        # Assuming a 2D dataset for simplicity, matching pixel_y, pixel_x access
        aod_data = np.full((1200, 1200), 0.2, dtype=np.float32)
        sds = f.create_dataset('Optical_Depth_055', data=aod_data)
        sds.attrs['scale_factor'] = 1.0
        sds.attrs['add_offset'] = 0.0
        sds.attrs['_FillValue'] = -9999
    print(f"Dummy HDF file created at: {file_path}")

if __name__ == "__main__":
    dummy_hdf_path = os.path.join(os.path.dirname(__file__), "MCD19A2.h20v05.hdf")
    create_dummy_hdf(dummy_hdf_path)

