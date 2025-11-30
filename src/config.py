"""
Physical constants and configuration settings for Dark IV Analysis.
"""

# Physical Constants
k_B = 1.380649e-23  # Boltzmann constant (J/K)
q = 1.60217663e-19  # Elementary charge (C)
T_STC = 298.15      # Standard Test Conditions Temperature (K)

# Default Settings
DEFAULT_AREA = 1.0  # Default cell area in cm^2 if not specified
VOLTAGE_COLUMN_NAMES = ['V', 'Voltage', 'Voltage (V)', 'U']
CURRENT_COLUMN_NAMES = ['I', 'Current', 'Current (A)', 'J', 'Current Density']

# Analysis Thresholds
R_SH_VOLTAGE_RANGE = (-0.2, 0.2)  # Voltage range for Rsh extraction (V)
LINEAR_REGION_THRESHOLD = 0.5     # Minimum R-squared for linear region detection
