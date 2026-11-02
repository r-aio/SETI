import os
import requests
import pandas as pd
import numpy as np

# Oficjalny link do surowych danych CSV sygnału Wow! z repozytorium projektu Ohio-SETI
WOW_CSV_URL = "https://raw.githubusercontent.com/planetaryhablab/Ohio-SETI/main/oseti_19770815_220410.csv"
LOCAL_FILE = "oseti_19770815_220410.csv"

def verify_local_archive(url=WOW_CSV_URL, filepath=LOCAL_FILE):
    """
    Pobiera plik CSV z danymi sygnału Wow!, jeśli nie znajduje się on lokalnie.
    """
    if os.path.exists(filepath):
        print(f"[BRIDGE] Plik archiwum sygnału Wow! jest dostępny lokalnie: {filepath}")
        return filepath
        
    print(f"[BRIDGE] Pobieranie historycznych danych sygnału Wow! z repozytorium: {url}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    with requests.get(url, headers=headers) as r:
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(r.content)
                    
    print("[BRIDGE] Pobieranie pliku danych Wow! zakończone pomyślnie.")
    return filepath

def extract_h5py_matrix(filepath):
    """
    Wczytuje plik CSV z danymi sygnału Wow! i konwertuje go do macierzy 2D 
    kompatybilnej z rdzeniem lixism_core.py.
    """
    print("[BRIDGE] Przetwarzanie tabeli danych Wow! do macierzy stochastycznej...")
    
    # Wczytanie pliku CSV za pomocą pandasa
    df = pd.read_csv(filepath)
    
    # Wyciągnięcie numerycznych kolumn sygnału / natężenia jako macierzy
    # (system automatycznie konwertuje kolumny numeryczne na tablicę numpy)
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        # Awaryjnie, jeśli struktura wymaga konkretnej kolumny (np. natężenia/flux)
        matrix_2d = df.values.astype(float)
    else:
        matrix_2d = numeric_df.values.astype(float)
    
    # Zapewnienie wymiaru 2D dla silnika analitycznego
    if matrix_2d.ndim == 1:
        matrix_2d = np.expand_dims(matrix_2d, axis=0)
        
    print(f"[BRIDGE] Ekstrakcja udana. Fizyczny kształt macierzy sygnału Wow!: {matrix_2d.shape}")
    return matrix_2d

if __name__ == "__main__":
    target_file = verify_local_archive()
    extract_h5py_matrix(target_file)
