import numpy as np
import pandas as pd
import os

def generate_sample(filename, J0=1e-9, n=1.5, Rs=0.5, Rsh=1e5, noise_level=1e-10):
    V = np.linspace(-0.5, 1.0, 151)
    q = 1.60217663e-19
    k = 1.380649e-23
    T = 298.15
    
    # Ideal diode equation with Rs and Rsh (implicit solved numerically or approx)
    # Approx: J = J0 * (exp(q(V - J*Rs)/nkT) - 1) + (V - J*Rs)/Rsh
    # Since Rs is small, we can iterate or just use V approx
    
    J = np.zeros_like(V)
    for i, v in enumerate(V):
        # Simple iteration to solve for J
        j_val = 0
        for _ in range(20):
            v_diode = v - j_val * Rs
            j_val = J0 * (np.exp(q * v_diode / (n * k * T)) - 1) + v_diode / Rsh
        J[i] = j_val
        
    # Add noise
    J += np.random.normal(0, noise_level, size=len(J))
    
    df = pd.DataFrame({'Voltage (V)': V, 'Current (A)': J})
    df.to_csv(filename, index=False)
    print(f"Generated {filename}")

if not os.path.exists('data'):
    os.makedirs('data')

generate_sample('data/sample_1.csv', J0=1e-10, n=1.2, Rs=0.2, Rsh=1e6)
generate_sample('data/sample_2.csv', J0=1e-8, n=1.8, Rs=1.0, Rsh=1e4)
