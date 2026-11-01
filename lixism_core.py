import sys
import time
import numpy as np
from z3 import *
from seti_bridge import verify_local_archive, extract_h5py_matrix

def fast_entropy_watchdog(vector, deviation_threshold=2.5):
    """
    Pre-cognitive filter (Watchdog) L0-ISM.
    Discards background stochastic noise before triggering the heavy SMT solver.
    """
    mean_val = np.mean(vector)
    std_dev = np.std(vector)
    
    if std_dev == 0:
        return False
        
    peak_max = np.max(vector)
    if (peak_max - mean_val) / std_dev > deviation_threshold:
        return True
    return False

def quantize_lixism_z19(stochastic_vector):
    """
    Quantizes amplitudes into a discrete Z_19 state-space grid (-9 to +9).
    """
    min_val = np.min(stochastic_vector)
    max_val = np.max(stochastic_vector)
    
    if max_val == min_val:
        return np.zeros_like(stochastic_vector, dtype=int)
        
    normalized = 18 * (stochastic_vector - min_val) / (max_val - min_val) - 9
    return np.round(normalized).astype(int)

def z3_closure_verifier(z19_vector):
    """
    SMT Z3 Solver. Verifies O(1) closure at zero point (L0).
    """
    solver = Solver()
    states = [Int(f'L_{i}') for i in range(len(z19_vector))]
    
    for s in states:
        solver.add(And(s >= -9, s <= 9))
        
    for i, val in enumerate(z19_vector):
        solver.add(states[i] == int(val))
        
    solver.add(Sum(states) == 0)
    
    if solver.check() == sat:
        return True
    return False

def run_deep_space_scanner():
    print("=== LIXISM SOVEREIGN DEEP SPACE SCANNER ===")
    start_time = time.time()
    
    target_file = verify_local_archive()
    matrix = extract_h5py_matrix(target_file)
    
    time_steps, freq_bins = matrix.shape
    window_size = 32 
    
    scanned_vectors = 0
    rejected_by_watchdog = 0
    z3_analyses = 0
    
    print(f"[SCANNER] Input matrix shape: {matrix.shape}")
    
    for t in range(time_steps):
        for f in range(0, freq_bins - window_size, window_size):
            window_vector = matrix[t, f:f+window_size]
            scanned_vectors += 1
            
            if not fast_entropy_watchdog(window_vector):
                rejected_by_watchdog += 1
                continue
                
            z19_vector = quantize_lixism_z19(window_vector)
            z3_analyses += 1
            
            if z3_closure_verifier(z19_vector):
                report_payload = (
                    "====================================================\n"
                    "!!! DATA PHYSICS ALERT: DETERMINISTIC SIGNAL DETECTED !!!\n"
                    "====================================================\n"
                    f"Matrix coordinates -> Time: {t}, Frequency: {f}\n"
                    f"Source vector      -> {window_vector}\n"
                    f"Z_19 matrix        -> {z19_vector}\n"
                    "Z3 STATUS: [SAT]\n"
                )
                print("\n" + report_payload)
                
                with open("LIXISM_SIGNAL_DETECTED.txt", "w") as proof_file:
                    proof_file.write(report_payload)
                
                print("[!] DISCOVERY. Stopping scanner and saving proof.")
                sys.exit(0)
                
        if t % 5 == 0:
            elapsed = round(time.time() - start_time, 2)
            print(f"[REPORT t={t}] Time: {elapsed}s | Scanned: {scanned_vectors} | Filtered (L0): {rejected_by_watchdog} | Z3: {z3_analyses}")

    print("\n=== SCAN SUMMARY ===")
    print(f"Total time: {round(time.time() - start_time, 2)} sec.")
    print(f"Total vectors scanned: {scanned_vectors}")
    print(f"Noise rejected by Watchdog: {rejected_by_watchdog}")
    print(f"Deep Z3 analyses: {z3_analyses}")

if __name__ == "__main__":
    run_deep_space_scanner()
