# Empirics: compound climate × world-price shocks in local food markets

Replication pipeline for the proposal in `../research-proposal/`. Run the scripts in order.

| Step | Script | Input | Output |
|---|---|---|---|
| 1 | `code/01_era5_monthly.py 1990 2026` | ARCO-ERA5 (public GCS, anonymous) | `data/raw/era5_monthly/YYYY-MM.npz`: monthly T mean, Tmax, HDD30, soil moisture at 0.25° |
| – | GPCP v2.3 monthly precipitation | `s3://noaa-cdr-precip-gpcp-monthly-pds` (public) | `data/raw/gpcp/` |
| – | World cereal prices (IMF via FRED: PWHEAMTUSDM, PMAIZMTUSDM, PRICENPQUSDM) | FRED | `data/raw/world_cereal_prices_imf_fred.csv` |
| 2 | `code/02_exporter_instrument.py` | ERA5 + GPCP | `data/processed/instrument.csv`: exporter-weather supply-shock index $Z_{ct}$ |
| 3 | `code/03_first_stage.py` | world prices + $Z$ | `output/tables/first_stage_lp.csv`, `output/figures/first_stage_lp.png` |
| 4 | `code/04_build_wfp_panel.py` | **`data/raw/wfp/*.csv`** (HDX "Global – Food Prices" yearly CSVs) | `data/processed/panel.parquet` |
| 5 | `code/05_estimate.py` | panel | `output/tables/main_panel.csv` (RF, OLS, 2SLS-LP, DML-PLIV, placebo) |
| MC | `code/99_simulate_panel.py` | – | simulated panel with known parameters for validating step 5 |

## Getting the WFP price files (manual step)

The cloud environment that built this pipeline could not reach `data.humdata.org`, because the host is blocked by network policy. To get the files:

1. Open <https://data.humdata.org/dataset/global-wfp-food-prices>.
2. Download the yearly CSVs `wfp_food_prices_global_YYYY.csv` (2000–2026; about 500 MB in total).
3. Place them in `empirics/data/raw/wfp/`.
4. Run steps 4–5.

Large data files are git-ignored. Every input can be regenerated from the scripts above.
