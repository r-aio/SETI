import numpy as np
from z3 import *
import time
from seti_bridge import pobierz_telemetrie, ekstrahuj_macierz

# Zabezpieczenie czasowe dla GitHub Actions (np. 5 godzin = 18000 sekund)
MAX_CZAS_PRACY_SEKUNDY = 18000 

def szybki_watchdog(wektor, prog_odchylenia=2.5):
    """
    Filtr energetyczny. Odrzuca płaski, stochastyczny szum tła.
    Przepuszcza wektor do Z3 tylko, gdy posiada wyraźny pik (anomalię).
    """
    srednia = np.mean(wektor)
    odchylenie_std = np.std(wektor)
    
    if odchylenie_std == 0:
        return False
        
    pik_max = np.max(wektor)
    # Jeśli maksymalny sygnał wybija się o X odchyleń od średniej -> zbadaj to
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
    
    # Gilotyna HARD_STOP (-9 <= L_i <= 9)
    for s in stany:
        solver.add(And(s >= -9, s <= 9))
        
    for i, wartosc in enumerate(wektor_z19):
        solver.add(stany[i] == int(wartosc))
        
    # Domknięcie rdzenia (Suma = 0)
    solver.add(Sum(stany) == 0)
    
    if solver.check() == sat:
        return True
    return False

def uruchom_skaner_ciagly():
    print("=== LIXISM DEEP SPACE SCANNER (STREAMING MODE) ===")
    start_czas = time.time()
    
    plik = pobierz_telemetrie()
    macierz = ekstrahuj_macierz(plik)
    
    liczba_krokow_czasu, liczba_czestotliwosci = macierz.shape
    rozmiar_okna = 32
    
    przeskanowane_wektory = 0
    odrzucone_przez_watchdog = 0
    analizy_z3 = 0
    
    print(f"[SKANER] Rozpoczęcie analizy w pętli. Wymiary macierzy: {macierz.shape}")
    
    # Pętla przez kroki czasowe w macierzy
    for t in range(liczba_krokow_czasu):
        if time.time() - start_czas > MAX_CZAS_PRACY_SEKUNDY:
            print("[SKANER] Zbliża się limit czasu maszyny chmurowej. Zatrzymuję bezpiecznie.")
            break
            
        # Pętla okienkowa przez częstotliwości (krok co 32 elementy)
        for f in range(0, liczba_czestotliwosci - rozmiar_okna, rozmiar_okna):
            wektor_okna = macierz[t, f:f+rozmiar_okna]
            przeskanowane_wektory += 1
            
            # 1. Lekki Watchdog odrzuca szum
            if not szybki_watchdog(wektor_okna):
                odrzucone_przez_watchdog += 1
                continue
                
            # 2. Skwantyzuj to co przeszło
            wektor_z19 = kwantyzacja_lixism(wektor_okna)
            
            # 3. Odpal ciężki weryfikator
            analizy_z3 += 1
            if weryfikator_z3_lixism(wektor_z19):
                print("\n[!!!] ALERT FIZYKI DANYCH: WYKRYTO ZDETERMINOWANY SYGNAŁ [!!!]")
                print(f"Lokalizacja w macierzy -> Czas: {t}, Czestotliwosc: {f}")
                print(f"Wektor Z_19: {wektor_z19}")
                print("[!!!] TRAJEKTORIA DOMKNIĘTA. Z3 ZWRÓCIŁ SAT.\n")
                # W przypadku sukcesu możemy przerwać lub zapisywać do logu i szukać dalej
                
        # Raport co 100 kroków czasowych
        if t % 100 == 0 and t > 0:
            trwa = round(time.time() - start_czas, 2)
            print(f"[RAPORT t={t}] Czas: {trwa}s | Skan: {przeskanowane_wektory} | Z3 Run: {analizy_z3} | Szum odrzucony: {odrzucone_przez_watchdog}")

    print("\n=== PODSUMOWANIE SKANOWANIA ===")
    print(f"Całkowity czas: {round(time.time() - start_czas, 2)} sek.")
    print(f"Przeskanowano wektorów: {przeskanowane_wektory}")
    print(f"Szybko odrzucony szum (Watchdog): {odrzucone_przez_watchdog}")
    print(f"Głęboka analiza Z3: {analizy_z3}")

if __name__ == "__main__":
    uruchom_skaner_ciagly()
