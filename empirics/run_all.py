"""Reproduce every table and figure of the paper from the replication package.

Usage (from the package root, i.e. the folder that contains code/ and data/):
    python run_all.py            # analysis stage: Tables 1-7, A.1-A.2, Figures 1-3 (from shipped data)
    python run_all.py --full     # also rebuild the panel and instrument from raw data (needs ERA5, see README)

Each step is run as a separate process; the run stops at the first failure.
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable

BUILD = [  # raw data -> data/processed (needs data/raw/era5_monthly, downloaded by 01_era5_monthly.py)
    ["code/01_era5_monthly.py", "1990", "2026"],
    ["code/02_exporter_instrument.py"],
    ["code/04_build_wfp_panel.py"],
]
ANALYSIS = [  # data/processed -> output/
    ["code/03_first_stage.py"],                 # Table A.1
    ["code/03b_first_stage_variants.py"],       # first-stage variants (Online Appendix)
    ["code/05_estimate.py"],                    # RF / OLS / 2SLS / AR (Online Appendix)
    ["code/05b_lpiv_cumulative.py"],            # Table A.2
    ["code/06_local_weather.py"],               # Tables 2-3, placebos
    ["code/07_heterogeneity.py"],               # Table 4 (causal forest, terciles, BLP)
    ["code/08_figures.py"],                     # Figures 1-3
    ["code/09_robustness.py"],                  # Table 7 (R1-R6)
    ["code/10_selection_sensitivity.py"],       # Table 7 (S1-S4), Holm correction, entry test
    ["code/11_mechanism_moderators.py"],        # Tables 1, 5, 6 (descriptives, production, moderators, welfare)
    ["code/12_winsorize.py"],                   # Table 7 (winsorized)
]
ERA5_ANALYSIS = [  # also needs data/raw/era5_monthly
    ["code/13_supply_area.py"],                 # Table 7 (supply-area rows)
]

if __name__ == "__main__":
    steps = (BUILD + ANALYSIS + ERA5_ANALYSIS) if "--full" in sys.argv else ANALYSIS
    for step in steps:
        t0 = time.time()
        print(f"\n=== {' '.join(step)}", flush=True)
        rc = subprocess.call([PY, *step], cwd=ROOT)
        if rc != 0:
            sys.exit(f"FAILED: {step[0]} (exit {rc})")
        print(f"--- done in {time.time() - t0:.0f} s", flush=True)
    print("\nAll steps finished. Tables: output/tables/, figures: output/figures/")
