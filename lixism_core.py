import sys
import time
import numpy as np
from z3 import *
from seti_bridge import pobierz_telemetrie, ekstrahuj_macierz

# Zabezpieczenie czasowe (ok. 5.5h)
MAX_CZAS_PRACY_SEKUNDY = 19800 

def szybki_watchdog(wektor, prog_odchylenia=2.5):
    srednia = np.mean(wektor)
    odchylenie_std = np.std(wektor)
    
    if odchylenie_std == 0:
        return False
        
    pik_max = np.max(wektor)
    if (pik_max - srednia) / odchylenie_std > prog_odchylenia:
        return True
    return False

def kwantyzacja_lixism(wektor_stochastyczny):
    min_val = np.min(wektor_stochastyczny)
    max_val = np.max(wektor_stochastyczny)
    
    if max_val == min_val:
        return np.zeros_like(wektor_stochastyczny, dtype=int)
        
    znormalizowany = 18 * (wektor_stochastyczny - min_val) / (max_val - min_val) - 9
    return np.round(znormalizowany).astype(int)

def weryfikator_z3_lixism(wektor_z19):
    solver = Solver()
    stany = [Int(f'L_{i}') for i in range(len(wektor_z19))]
    
    for s in stany:
        solver.add(And(s >= -9, s <= 9))
        
    for i, wartosc in enumerate(wektor_z19):
        solver.add(stany[i] == int(wartosc))
        
    solver.add(Sum(stany) == 0)
    
    if solver.check() == sat:
        return True
    return False

def uruchom_skaner_kosmosu():
    print("=== LIXISM DEEP SPACE SCANNER ===")
    start_czas = time.time()
    
    plik = pobierz_telemetrie()
    macierz = ekstrahuj_macierz(plik)
    
    liczba_krokow_czasu, liczba_czestotliwosci = macierz.shape
    rozmiar_okna = 32 
    
    przeskanowane_wektory = 0
    odrzucone_przez_watchdog = 0
    analizy_z3 = 0
    
    print(f"[SKANER] Wymiary macierzy: {macierz.shape}")
    
    for t in range(liczba_krokow_czasu):
        if time.time() - start_czas > MAX_CZAS_PRACY_SEKUNDY:
            print("[SKANER] Limit czasu chmury. Zatrzymuję skaner.")
            break
            
        for f in range(0, liczba_czestotliwosci - rozmiar_okna, rozmiar_okna):
            wektor_okna = macierz[t, f:f+rozmiar_okna]
            przeskanowane_wektory += 1
            
            if not szybki_watchdog(wektor_okna):
                odrzucone_przez_watchdog += 1
                continue
                
            wektor_z19 = kwantyzacja_lixism(wektor_okna)
            
            # Właściwe umiejscowienie licznika
            analizy_z3 += 1
            
            if weryfikator_z3_lixism(wektor_z19):
                raport = (
                    "====================================================\n"
                    "!!! ALERT FIZYKI DANYCH: WYKRYTO ZDETERMINOWANY SYGNAŁ !!!\n"
                    "====================================================\n"
                    f"Współrzędne macierzy  -> Czas: {t}, Częstotliwość: {f}\n"
                    f"Wektor źródłowy       -> {wektor_okna}\n"
                    f"Macierz Z_19          -> {wektor_z19}\n"
                    "STATUS Z3: [SAT]\n"
                )
                print("\n" + raport)
                
                with open("LIXISM_SIGNAL_DETECTED.txt", "w") as plik_dowodowy:
                    plik_dowodowy.write(raport)
                
                print("[!] ODKRYCIE. Zatrzymuję skaner.")
                sys.exit(1)
                
        if t % 50 == 0 and t > 0:
            trwa = round(time.time() - start_czas, 2)
            print(f"[RAPORT t={t}] Czas: {trwa}s | Skan: {przeskanowane_wektory} | Odrzucono (L0): {odrzucone_przez_watchdog} | Z3: {analizy_z3}")

    print("\n=== PODSUMOWANIE ===")
    print(f"Całkowity czas: {round(time.time() - start_czas, 2)} sek.")

if __name__ == "__main__":
    uruchom_skaner_kosmosu()
