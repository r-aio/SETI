import sys # Dodaj to na górze pliku

# ... [poprzedni kod kwantyzacji i Z3] ...

            # 3. Odpal ciężki weryfikator
            analizy_z3 += 1
            if weryfikator_z3_lixism(wektor_z19):
                raport = (
                    "!!! ALERT FIZYKI DANYCH: WYKRYTO ZDETERMINOWANY SYGNAŁ !!!\n"
                    f"Lokalizacja w macierzy -> Czas: {t}, Czestotliwosc: {f}\n"
                    f"Wektor Z_19: {wektor_z19}\n"
                    "TRAJEKTORIA DOMKNIĘTA. Z3 ZWRÓCIŁ SAT."
                )
                print(raport)
                
                # Zapisz dowód do pliku zanim maszyna zniknie
                with open("WYKRYTY_SYGNAL_LIXISM.txt", "w") as plik_dowodowy:
                    plik_dowodowy.write(raport)
                
                # WYMUSZENIE BŁĘDU (Zatrzymuje serwer i wysyła Ci e-mail z GitHuba)
                print("[!] Przerywam działanie chmury. Sprawdź plik i logi.")
                sys.exit(1) 
