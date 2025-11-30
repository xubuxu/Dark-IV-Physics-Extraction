# Dark IV Analysis (DIVA)

**Dark IV Physics Extraction Tool for Photovoltaic Device Research**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📋 Overview

**DIVA (Dark IV Analysis)** is an automated data analysis tool specifically designed for photovoltaic device R&D. It extracts key physical parameters from dark current-voltage (IV) measurements and generates publication-quality Word reports and presentation-ready PowerPoint slides.

### Key Features

- 🔬 **Automated Parameter Extraction**: Extracts $R_{sh}$, $R_s$, $J_0$, and $n$ from dark IV curves
- 📊 **Multi-Format Data Support**: Handles `.csv`, `.txt`, `.xlsx`, and `.iv` files
- 📈 **Comprehensive Visualization**: Generates three types of diagnostic plots
  - Semi-log J-V curves (leakage & rectification analysis)
  - Ideality factor n(V) plots (recombination mechanism diagnosis)
  - Differential resistance Rdiff(V) plots (resistance analysis)
- 📄 **Professional Reports**: Auto-generates Word and PowerPoint reports with customizable styles
- 🎨 **Dual Style System**: "Nature" style for publications, "Business" style for presentations

---

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/xubuxu/Dark-IV-Physics-Extraction.git
cd Dark-IV-Physics-Extraction
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the analysis**
```bash
python main.py
```

### First Run

The tool includes a sample data generator for testing:

```bash
python generate_sample_data.py  # Generate synthetic test data
python main.py                  # Run analysis
```

Reports will be saved in the `output/` directory.

---

## 📂 Project Structure

```
Dark-IV-Analysis/
├── data/                   # Input data directory
│   ├── sample_1.csv
│   └── sample_2.csv
├── output/                 # Generated reports
│   ├── Dark_IV_Report.docx
│   ├── Dark_IV_Presentation.pptx
│   └── summary.xlsx
├── src/                    # Source code
│   ├── config.py           # Physical constants & settings
│   ├── io_handler.py       # Data loading & preprocessing
│   ├── physics.py          # Physics engine (parameter extraction)
│   ├── visualization.py    # Plotting engine
│   └── reporting/          # Report generation modules
│       ├── excel_gen.py
│       ├── word_gen.py
│       └── ppt_gen.py
├── templates/              # Report templates
│   ├── report_template.docx
│   └── slide_template.pptx
├── styles/                 # Matplotlib style sheets
│   ├── nature.mplstyle     # Publication style
│   └── business.mplstyle   # Presentation style
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 📊 Output Examples

### Generated Plots

For each sample, DIVA generates three diagnostic plots:

1. **Semi-log J-V Plot**
   - Visualizes dark current characteristics
   - Shows raw data + smoothed curve
   - Identifies leakage and rectification behavior

2. **Ideality Factor n(V) Plot**
   - Tracks local ideality factor vs. voltage
   - Includes n=1 and n=2 reference lines
   - Diagnoses recombination mechanisms

3. **Differential Resistance Rdiff(V) Plot**
   - Shows dV/dJ variation with voltage
   - Semi-log scale for better visualization
   - Highlights shunt and series resistance effects

### Report Formats

- **Excel**: Summary table with all extracted parameters
- **Word**: Detailed analysis report with:
  - Parameter summary table
  - Individual sample sections with all three plots
  - Nature journal formatting
- **PowerPoint**: Presentation slides with:
  - Title slide
  - Summary table slide
  - Individual analysis slides (3 per sample)
  - Business-friendly styling

---

## ⚙️ Configuration

### Physical Constants (`src/config.py`)

```python
k_B = 1.380649e-23  # Boltzmann constant (J/K)
q = 1.60217663e-19  # Elementary charge (C)
T_STC = 298.15      # Standard temperature (K)
```

### Default Settings

- **Cell Area**: 1.0 cm² (modify in `config.py` or pass to `DataLoader.preprocess()`)
- **Smoothing**: Savitzky-Golay filter (window=11, polyorder=3)
- **Rsh Voltage Range**: -0.2V to 0.2V

---

## 🔬 Physics Background

### Extracted Parameters

| Parameter | Symbol | Description | Unit |
|-----------|--------|-------------|------|
| Shunt Resistance | $R_{sh}$ | Parallel resistance (leakage) | Ω·cm² |
| Series Resistance | $R_s$ | Contact + bulk resistance | Ω·cm² |
| Saturation Current Density | $J_0$ | Reverse saturation current | A/cm² |
| Ideality Factor | $n$ | Diode quality (1=ideal, 2=SRH) | - |

### Analysis Methods

- **Rsh**: Inverse slope of J-V near V=0
- **n & J0**: Linear regression on ln(J) vs V in exponential region
- **Rs**: Deviation from ideal diode at high voltage
- **Rdiff**: Numerical gradient dV/dJ from smoothed data

---

## 🛠️ Customization

### Adding Custom Templates

1. Place your `.docx` or `.pptx` template in `templates/`
2. Update the file paths in `main.py`:

```python
word_builder = WordReportBuilder('templates/your_template.docx')
ppt_builder = PPTReportBuilder('templates/your_template.pptx')
```

### Modifying Plot Styles

Edit the matplotlib style files in `styles/`:
- `nature.mplstyle`: For academic publications
- `business.mplstyle`: For presentations

---

## 📝 Requirements

- Python 3.8+
- numpy >= 1.21.0
- pandas >= 1.3.0
- scipy >= 1.7.0
- matplotlib >= 3.4.0
- python-docx >= 0.8.11
- python-pptx >= 0.6.21
- openpyxl >= 3.0.0

See `requirements.txt` for complete list.

---

## 📖 Usage Examples

### Basic Usage

```python
from src.io_handler import DataLoader
from src.physics import DarkIVAnalyzer

# Load data
df = DataLoader.load_data('data/sample_1.csv')
df = DataLoader.preprocess(df, area=0.25)  # 0.25 cm²

# Analyze
analyzer = DarkIVAnalyzer(df)
analyzer.smooth_data()
analyzer.calculate_differential_resistance()
params = analyzer.extract_parameters()

print(f"J0 = {params['J0']:.2e} A/cm²")
print(f"n = {params['n']:.2f}")
```

### Custom Visualization

```python
from src.visualization import Visualizer
import matplotlib.pyplot as plt

viz = Visualizer(style_dir='styles')
viz.set_style('nature')

fig, ax = plt.subplots()
viz.plot_semilog_jv(analyzer.df, ax, title="My Device")
plt.show()
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by best practices in solar cell characterization
- Built for researchers by researchers
- Special thanks to the photovoltaic research community

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Happy Analyzing! 🔬📊**
