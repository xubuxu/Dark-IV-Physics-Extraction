import os
import pandas as pd
import numpy as np
from src.config import VOLTAGE_COLUMN_NAMES, CURRENT_COLUMN_NAMES, DEFAULT_AREA

class DataLoader:
    @staticmethod
    def load_data(filepath):
        """
        Loads IV data from various file formats (.csv, .txt, .xlsx, .iv).
        """
        ext = os.path.splitext(filepath)[1].lower()
        
        try:
            if ext == '.csv':
                df = pd.read_csv(filepath)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath)
            elif ext in ['.txt', '.iv']:
                # Try tab-delimited first, then whitespace
                try:
                    df = pd.read_csv(filepath, sep='\t')
                    if df.shape[1] < 2:
                         df = pd.read_csv(filepath, sep=r'\s+')
                except:
                     df = pd.read_csv(filepath, sep=r'\s+')
            else:
                raise ValueError(f"Unsupported file extension: {ext}")
            
            return df
        except Exception as e:
            raise IOError(f"Error loading file {filepath}: {str(e)}")

    @staticmethod
    def preprocess(df, area=DEFAULT_AREA):
        """
        Preprocesses IV data: column recognition, unit conversion, 
        zero-offset correction, and polarity check.
        
        Returns:
            pd.DataFrame: Processed DataFrame with 'V', 'I', 'J' columns.
        """
        # 1. Column Recognition
        # Normalize column names to lower case for matching
        df.columns = [str(c).strip() for c in df.columns]
        
        v_col = None
        i_col = None
        
        # Simple fuzzy matching
        for col in df.columns:
            if any(n.lower() == col.lower() for n in VOLTAGE_COLUMN_NAMES):
                v_col = col
            elif any(n.lower() in col.lower() for n in VOLTAGE_COLUMN_NAMES) and not v_col: # Partial match if exact not found
                v_col = col
                
            if any(n.lower() == col.lower() for n in CURRENT_COLUMN_NAMES):
                i_col = col
            elif any(n.lower() in col.lower() for n in CURRENT_COLUMN_NAMES) and not i_col:
                i_col = col

        if not v_col or not i_col:
            # Fallback: Assume 1st col is V, 2nd is I if only 2 columns
            if df.shape[1] == 2:
                v_col = df.columns[0]
                i_col = df.columns[1]
            else:
                raise ValueError(f"Could not identify Voltage or Current columns. Found: {df.columns.tolist()}")

        # Standardize names
        df = df.rename(columns={v_col: 'V', i_col: 'I'})
        
        # Ensure numeric
        df['V'] = pd.to_numeric(df['V'], errors='coerce')
        df['I'] = pd.to_numeric(df['I'], errors='coerce')
        df = df.dropna(subset=['V', 'I'])

        # Sort by Voltage
        df = df.sort_values('V').reset_index(drop=True)

        # 2. Zero-offset Correction (I = I - I(V=0))
        # Find point closest to V=0 within a small window
        idx_zero = (df['V'].abs()).idxmin()
        if abs(df.loc[idx_zero, 'V']) < 0.5: # Only correct if we have data near zero
            i_offset = df.loc[idx_zero, 'I']
            df['I'] = df['I'] - i_offset

        # 3. Polarity Correction
        # Heuristic: The "forward bias" region (exponential growth) should be in the first quadrant (V>0, I>0).
        # Find the point with the maximum absolute current.
        max_idx = df['I'].abs().idxmax()
        max_v = df.loc[max_idx, 'V']
        max_i = df.loc[max_idx, 'I']

        # If max power point is in 3rd quadrant (V<0, I<0), flip both.
        if max_v < 0 and max_i < 0:
            df['V'] = -df['V']
            df['I'] = -df['I']
        # If max power point is in 2nd or 4th, flip I or V to get to 1st.
        # Assuming standard diode curve, we want the high current part to be V>0, I>0.
        elif max_v < 0 and max_i > 0:
             df['V'] = -df['V'] # Flip V
        elif max_v > 0 and max_i < 0:
             df['I'] = -df['I'] # Flip I
             
        # Re-sort after potential V flip
        df = df.sort_values('V').reset_index(drop=True)

        # 4. Area Normalization (I -> J)
        # Assuming I is in Amps, Area in cm^2 -> J in A/cm^2
        if area and area > 0:
            df['J'] = df['I'] / area 
        else:
            df['J'] = df['I']

        return df
