import os
import h5py
import numpy as np

# Enter the exact filename of the downloaded .h5 file from the Berkeley table
SETI_FILE = "your_downloaded_file.h5"

def verify_local_archive(filepath=SETI_FILE):
    """
    Sovereign (Local) version.
    Verifies the existence of the physical file on the working disk.
    """
    if not os.path.exists(filepath):
        print(f"[!] PHYSICAL ERROR: File '{filepath}' not found.")
        print("[!] Place the downloaded HDF5 file in the script directory.")
        exit(1)
        
    print(f"[BRIDGE] Authorizing access to local cosmic archive: {filepath}")
    return filepath

def extract_h5py_matrix(filepath):
    """
    Extracts the stochastic matrix directly from the HDF5 file.
    """
    print("[BRIDGE] Low-level state-space matrix extraction...")
    with h5py.File(filepath, 'r') as f:
        raw_data_matrix = f['data'][:]
    
    matrix_2d = np.squeeze(raw_data_matrix)
    print(f"[BRIDGE] Extraction successful. Physical matrix shape: {matrix_2d.shape}")
    return matrix_2d

if __name__ == "__main__":
    target_file = verify_local_archive()
    extract_h5py_matrix(target_file)
