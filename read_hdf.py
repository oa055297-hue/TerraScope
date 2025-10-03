
import h5py

# Open the HDF file
FILE_NAME = 'MCD19A2CMG.A2025273.061.2025274194542.hdf'

try:
    with h5py.File(FILE_NAME, 'r') as f:
        print(f"Successfully opened HDF5 file: {FILE_NAME}")
        print("Keys in the HDF5 file:")
        for key in f.keys():
            print(f"  - {key}")
            if isinstance(f[key], h5py.Group):
                print(f"    Sub-keys in group '{key}':")
                for sub_key in f[key].keys():
                    print(f"      - {sub_key}")
            elif isinstance(f[key], h5py.Dataset):
                print(f"    Dataset shape: {f[key].shape}")
                print(f"    Dataset attributes: {dict(f[key].attrs)}")

except Exception as e:
    print(f"Error opening HDF5 file: {e}")
    print("This might not be an HDF5 file or it is corrupted.")

