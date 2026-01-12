# Fukuzono Slope Failure Prediction

Predictive analysis tool for landslide collapse timing using the Inverse Velocity Method (Fukuzono, 1985) with statistical correction by Qi et al. (2023) and tangent angle detection.

## Overview

This project implements an advanced slope failure prediction algorithm based on:

- **Fukuzono's Inverse Velocity Method (INV)**: During tertiary creep acceleration (pre-collapse phase), the inverse velocity (1/V) tends to zero linearly with time.
- **Qi et al. (2023) Correction**: Applies a statistical correction coefficient (0.30–0.55) to account for the final acceleration phase, which is typically steeper than predicted by linear regression.
- **Tangent Angle (Alpha)**: Normalizes velocity relative to a reference creep rate, defining three alert levels (Safety <80°, Alert 80–85°, Emergency >85°).

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

### Key Dependencies

```python
pandas==2.3.3              # Data manipulation
numpy==2.4.0               # Numerical computations
scipy==1.16.3              # Signal processing (Savitzky-Golay filter)
scikit-learn==1.8.0        # Linear regression
matplotlib==3.10.8         # Plotting
```

## Installation

1. **Clone or download the repository**
   ```bash
   cd fukuzono_improved
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
.
├── data/
│   └── dati_lanzada.csv              # Input dataset
├── output/
│   └── grafico_fukuzono.png          # Generated plot
├── src/
│   ├── config.py                     # Configuration dataclasses
│   ├── fukuzono.py                   # Core INV analysis
│   ├── letturadati.py                # Data loading & preprocessing
│   ├── plot.py                       # Visualization
│   └── report.py                     # Text report generation
├── fukuzono.ipynb                    # Main Jupyter notebook
├── requirements.txt
├── README.md
└── LICENSE
```

## References

- Fukuzono, T. (1985). "A new method for predicting the failure time of a slope." *8th International Conference on Soil Mechanics and Foundation Engineering*.
- Voight, B. (1988). "A method for prediction of volcanic eruptions." *Nature*, 332(6160), 125-130.
- Qi, S., Cao, X., & Peng, M. (2023). "An improvement velocity inverse method for predicting the slope imminent failure time." *Landslides*, 20, 1–12.
- Zhou, W., Liu, Q., & Xu, Q. (2020). "A modified inverse-velocity method for predicting the failure time of landslides." *Bulletin of Engineering Geology and the Environment*, 79(8), 4327-4341.

## License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

You are free to:
- Use, modify, and distribute this software
- Use it for commercial and private purposes

Under the conditions that you:
- Include a copy of the license and copyright notice
- Disclose the source code of any modifications
- Release derivatives under the same license
