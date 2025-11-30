import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from scipy.stats import linregress
from src.config import k_B, q, T_STC, R_SH_VOLTAGE_RANGE, LINEAR_REGION_THRESHOLD

class DarkIVAnalyzer:
    def __init__(self, df):
        """
        Initializes the analyzer with a DataFrame containing 'V' and 'J' columns.
        """
        self.df = df.copy()
        self.results = {
            'Rsh': np.nan,
            'Rs': np.nan,
            'J0': np.nan,
            'n': np.nan,
            'r_squared': np.nan
        }

    def smooth_data(self, window_length=11, polyorder=3):
        """
        Applies Savitzky-Golay filter to the current density J.
        Adds 'J_smooth' and 'logJ' columns to the DataFrame.
        """
        try:
            # Ensure window_length is odd and valid
            n_samples = len(self.df)
            if window_length >= n_samples:
                window_length = n_samples - 1 if n_samples % 2 == 0 else n_samples
            
            if window_length < 3:
                # Too few points to smooth
                self.df['J_smooth'] = self.df['J']
            else:
                self.df['J_smooth'] = savgol_filter(self.df['J'], window_length, polyorder)
            
            # Calculate logJ (using absolute value to avoid log errors)
            # Replace zeros or negative values with NaN for log plot
            self.df['logJ'] = np.log10(self.df['J_smooth'].abs().replace(0, np.nan))
            
        except Exception as e:
            print(f"Smoothing warning: {e}")
            self.df['J_smooth'] = self.df['J']
            self.df['logJ'] = np.log10(self.df['J'].abs().replace(0, np.nan))

    def extract_parameters(self):
        """
        Extracts Rsh, Rs, n, J0 using analytical methods.
        Returns a dictionary of parameters.
        """
        df = self.df
        
        # ---------------------------------------------------------
        # 1. Rsh (Shunt Resistance): Inverse slope at V ~ 0
        # ---------------------------------------------------------
        mask_rsh = (df['V'] >= R_SH_VOLTAGE_RANGE[0]) & (df['V'] <= R_SH_VOLTAGE_RANGE[1])
        df_rsh = df[mask_rsh]
        
        if len(df_rsh) > 2:
            # Slope of J vs V is Gsh (Conductance per unit area) -> Rsh = 1/slope
            # Units: V in Volts, J in A/cm^2 -> Rsh in Ohm*cm^2
            slope, intercept, r_val, _, _ = linregress(df_rsh['V'], df_rsh['J'])
            if slope != 0:
                self.results['Rsh'] = 1.0 / slope
            else:
                self.results['Rsh'] = 1e9 # High resistance
        
        # ---------------------------------------------------------
        # 2. n (Ideality Factor) and J0 (Saturation Current)
        # ---------------------------------------------------------
        # Calculate local ideality factor n(V)
        # n = (q / kT) * (dV / d(lnJ))
        # Use smoothed data and only positive voltage/current
        valid_mask = (df['V'] > 0.1) & (df['J_smooth'] > 0)
        df_pos = df[valid_mask].copy()
        
        if len(df_pos) > 5:
            # Calculate derivative d(lnJ)/dV
            # lnJ (natural log) = ln(10) * log10(J)
            lnJ = np.log(df_pos['J_smooth'])
            
            # Gradient
            dV = np.gradient(df_pos['V'])
            dlnJ = np.gradient(lnJ)
            
            with np.errstate(divide='ignore', invalid='ignore'):
                n_local = (q / (k_B * T_STC)) * (dV / dlnJ)
            
            df_pos['n_local'] = n_local
            # Map back to main df
            self.df.loc[valid_mask, 'n_local'] = n_local
            
            # Find the "plateau" or minimum n in the exponential region
            # Usually between 0.2V and 0.8V depending on material
            # Filter for reasonable n values (e.g., 0.5 < n < 5)
            mask_n = (df_pos['n_local'] > 0.5) & (df_pos['n_local'] < 5)
            
            if mask_n.any():
                # Strategy: Find the minimum n value (often corresponds to the diffusion/recombination balance)
                # or the most stable region. Let's take the minimum n.
                min_n_idx = df_pos.loc[mask_n, 'n_local'].idxmin()
                n_best = df_pos.loc[min_n_idx, 'n_local']
                
                # Use a small window around this point to fit J0
                v_center = df_pos.loc[min_n_idx, 'V']
                mask_fit = (df_pos['V'] > v_center - 0.05) & (df_pos['V'] < v_center + 0.05)
                
                if mask_fit.sum() > 2:
                    slope_ln, intercept_ln, r_sq, _, _ = linregress(df_pos.loc[mask_fit, 'V'], np.log(df_pos.loc[mask_fit, 'J_smooth']))
                    
                    # Recalculate n from slope to be consistent with J0
                    # slope = q / (n kT) -> n = q / (slope kT)
                    n_fit = q / (slope_ln * k_B * T_STC)
                    J0_fit = np.exp(intercept_ln)
                    
                    self.results['n'] = n_fit
                    self.results['J0'] = J0_fit
                    self.results['r_squared'] = r_sq**2
                else:
                    self.results['n'] = n_best
                    # Estimate J0 from single point: J0 = J / exp(qV/nkT)
                    J_point = df_pos.loc[min_n_idx, 'J_smooth']
                    V_point = df_pos.loc[min_n_idx, 'V']
                    self.results['J0'] = J_point / np.exp(q * V_point / (n_best * k_B * T_STC))

        # ---------------------------------------------------------
        # 3. Rs (Series Resistance)
        # ---------------------------------------------------------
        # Rs = (V_meas - V_ideal) / J
        # V_ideal = (n kT / q) * ln(J/J0 + 1)
        if not np.isnan(self.results['n']) and not np.isnan(self.results['J0']):
            # Use the highest voltage point
            idx_max = df['V'].idxmax()
            V_max = df.loc[idx_max, 'V']
            J_max = df.loc[idx_max, 'J_smooth']
            
            if J_max > 0:
                term = J_max / self.results['J0'] + 1
                if term > 0:
                    V_ideal = (self.results['n'] * k_B * T_STC / q) * np.log(term)
                    Rs = (V_max - V_ideal) / J_max
                    self.results['Rs'] = max(0, Rs) # Clamp to 0
        
        return self.results

    def calculate_differential_resistance(self):
        """
        Calculates differential resistance Rdiff = dV/dJ.
        Adds 'R_diff' column to DataFrame.
        """
        df = self.df
        
        if 'J_smooth' in df.columns:
            # Use smoothed data for better derivative calculation
            dV = np.gradient(df['V'])
            dJ = np.gradient(df['J_smooth'])
            
            with np.errstate(divide='ignore', invalid='ignore'):
                R_diff = dV / dJ
            
            # Filter out unreasonable values (infinities, very large values)
            R_diff = np.where(np.isfinite(R_diff), R_diff, np.nan)
            R_diff = np.where(np.abs(R_diff) < 1e10, R_diff, np.nan)
            
            self.df['R_diff'] = R_diff
    
    def fit_sdm(self):
        """
        Wrapper for extract_parameters to satisfy the interface.
        In future versions, this could implement a full non-linear least squares fit.
        """
        self.smooth_data()
        return self.extract_parameters()
