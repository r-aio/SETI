import os
import requests
from blimpy import Waterfall
import numpy as np

# Oficjalny link do archiwum Breakthrough Listen: Obiekt 'Oumuamua
SETI_URL = "http://blpd0.ssl.berkeley.edu/oumuamua/spliced_blc0001020304050607_guppi_58100_78802_OUMUAMUA_0011.gpuspec.0002.fil"
SETI_FILE = "oumuamua_target.fil"

def verify_local_archive(url=SETI_URL, filepath=SETI_FILE):
    """
    Pobiera plik .fil z międzygwiazdowego archiwum Berkeley, jeśli nie ma go lokalnie.
    """
    if os.path.exists(filepath):
        print(f"[BRIDGE] Plik telemetrii Oumuamua znajduje się lokalnie: {filepath}")
        return filepath
        
    print(f"[BRIDGE] Pobieranie danych z międzygwiazdowego strumienia: {url}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    with requests.get(url, stream=True, headers=headers) as r:
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024): # Paczki po 1 MB
                if chunk:
                    f.write(chunk)
                    
    print("[BRIDGE] Pobieranie zakończone pomyślnie.")
    return filepath

def extract_h5py_matrix(filepath):
    """
    Ekstrakcja macierzy wodospadowej z pliku Filterbank (.fil) przy użyciu blimpy.
    (Zachowano nazwę funkcji dla pełnej kompatybilności z lixism_core.py).
    """
    print("[BRIDGE] Ładowanie struktury Filterbank (.fil) przez blimpy...")
    
    # Inicjalizacja obiektu Waterfall z biblioteki blimpy
    observer = Waterfall(filepath)
    
    # Wyciągnięcie i spłaszczenie do macierzy 2D (czas x częstotliwość)
    matrix_2d = np.squeeze(observer.data)
    
    print(f"[BRIDGE] Ekstrakcja udana. Fizyczny kształt macierzy Oumuamua: {matrix_2d.shape}")
    return matrix_2d

if __name__ == "__main__":
    target_file = verify_local_archive()
    extract_h5py_matrix(target_file)
