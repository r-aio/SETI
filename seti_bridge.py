import os
import requests
from blimpy import Waterfall
import numpy as np

# Plik kalibracyjny Voyagera 1 z Breakthrough Listen. 
# Aby skanować pusty kosmos w poszukiwaniu obcych struktur, podmień ten URL.
SETI_URL = "http://blpd0.ssl.berkeley.edu/Voyager_data/Voyager1.single_coarse.fine_res.h5"
SETI_FILE = "seti_raw_telemetry.h5"

def pobierz_telemetrie(url=SETI_URL, plik=SETI_FILE):
    if not os.path.exists(plik):
        print(f"[BRIDGE] Pobieranie surowej telemetrii kosmicznej ({url})...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(plik, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("[BRIDGE] Zakończono pobieranie.")
    else:
        print("[BRIDGE] Plik telemetrii już istnieje lokalnie.")
    return plik

def ekstrahuj_macierz(plik):
    print("[BRIDGE] Dekodowanie pliku HDF5 do macierzy wodospadowej...")
    obs = Waterfall(plik)
    macierz_danych = obs.data 
    macierz_2d = np.squeeze(macierz_danych)
    print(f"[BRIDGE] Wyekstrahowano macierz stochastyczną o wymiarach: {macierz_2d.shape}")
    return macierz_2d

if __name__ == "__main__":
    plik = pobierz_telemetrie()
    ekstrahuj_macierz(plik)
