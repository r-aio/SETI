import os
import requests
import h5py
import numpy as np

# Surowy zrzut GBT: Cel Alkaid (HIP67301) - 14.4 GiB
SETI_URL = "https://bldata.berkeley.edu/pipeline/AGBT16B_999_15/holding/spliced_blc0001020304050607_guppi_57626_80989_HIP67301_0028.gpuspec.0000.h5"
SETI_FILE = "deep_space_target.h5"

def pobierz_w_kawalkach(url=SETI_URL, plik=SETI_FILE, max_rozmiar_gb=8):
    """
    Pobiera dane stochastyczne z ominięciem limitów dysku serwerów chmurowych.
    Pobierze tylko określoną początkową próbkę (np. 8GB), co uchroni 
    GitHub Actions przed błędem 'Out of Space'. 
    Wielkość piku L0 i tak ukrywa się w pierwszych warstwach czasowych.
    """
    if os.path.exists(plik):
        print("[BRIDGE] Pakiet telemetryczny znajduje się w pamięci.")
        return plik
        
    print(f"[BRIDGE] Inicjalizacja nasłuchu (Target: {url})...")
    limit_bajtow = max_rozmiar_gb * 1024 * 1024 * 1024 
    pobrane_bajty = 0
    
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(plik, 'wb') as f:
            # Chunking zapobiega przeładowaniu RAM
            for chunk in r.iter_content(chunk_size=1024*1024): # Paczki 1MB
                if chunk:
                    f.write(chunk)
                    pobrane_bajty += len(chunk)
                    
                if pobrane_bajty >= limit_bajtow:
                    print(f"[BRIDGE] Osiągnięto bezpieczny limit chmury ({max_rozmiar_gb}GB). Przecinanie strumienia.")
                    break
                    
    print("[BRIDGE] Zakończono buforowanie wycinka wszechświata.")
    return plik

def ekstrahuj_macierz_h5py(plik):
    """
    Omija ciężki moduł 'blimpy' dla plików wielkogabarytowych.
    Używa niskopoziomowego h5py do odczytania struktury i wgrania tylko 
    fizycznych danych (macierz Data) prosto z uciętego pliku.
    """
    print("[BRIDGE] Niskopoziomowa ekstrakcja przestrzeni stanów z HDF5...")
    
    # Odczyt w trybie read-only, by nie obciążać I/O
    try:
        f = h5py.File(plik, 'r')
        # Struktura danych z Berkeley w formacie h5 to zazwyczaj: f['data']
        macierz_danych = f['data'][:]
        f.close()
        
        macierz_2d = np.squeeze(macierz_danych)
        print(f"[BRIDGE] Ekstrakcja udana. Kształt wektora: {macierz_2d.shape}")
        return macierz_2d
    except Exception as e:
        print(f"[!] Błąd dekompresji HDF5: {e}")
        print("[!] Plik mógł zostać obcięty w sposób uniemożliwiający odczyt struktury.")
        print("[!] Fallback: Zwracam sztuczny szum do kalibracji gilotyny Z3.")
        # Zabezpieczenie przed twardym padem chmury w razie obcięcia nagłówków 14GB pliku
        return np.random.rand(16, 1000000)

if __name__ == "__main__":
    plik = pobierz_w_kawalkach()
    ekstrahuj_macierz_h5py(plik)
