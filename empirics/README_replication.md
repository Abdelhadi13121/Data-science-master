# Replication package

**Paper:** "Who pays for local droughts? Weather shocks and staple food prices in 3,200 local markets" (submitted to *Food Policy*).

This package reproduces every table and figure in the paper and its Appendix A. All inputs are public secondary data. The package ships the raw files as downloaded, except the ERA5 reanalysis grids (1.4 GB), which a script re-downloads from a public bucket.

## 1. Contents

| Folder / file | Contents |
|---|---|
| `code/` | Python scripts `00`–`12` and `99` (see Section 4) |
| `run_all.py` | Runs every analysis step in order |
| `requirements.txt` | Exact package versions used |
| `PAP_local_weather.md` | Pre-analysis plan and its dated Addendum A (git commits af071f3 and e5e0ed8 precede the estimates) |
| `data/raw/wfp/` | WFP retail food prices, HDX "Global – Food Prices", yearly CSVs 1990–2026 |
| `data/raw/gpcp/` | GPCP v2.3 monthly precipitation, netCDF |
| `data/raw/faostat/` | FAOSTAT Crops and livestock (QCL) and Food balance sheets (FBS), official zip files |
| `data/raw/ucdp/` | UCDP Georeferenced Event Dataset v26.1, official zip file |
| `data/raw/access/` | Natural Earth populated places, 1:10m |
| `data/raw/world_cereal_prices_imf_fred.csv` | IMF world prices of wheat, maize and rice (FRED series PWHEAMTUSDM, PMAIZMTUSDM, PRICENPQUSDM) |
| `data/processed/panel.parquet` | Analysis panel: market × product × month, with prices, the weather index W and its components, world prices and exchange rates |
| `data/processed/instrument.csv`, `exporter_weather.csv` | Exporter-weather instrument (Appendix A) |
| `data/processed/market_moderators.csv` | Market-level climate moderators used in Table 4 (computed from ERA5 and GPCP by `07_heterogeneity.py`) |
| `output/` | Tables (CSV), figures (PNG) and results notes as reported in the paper |
| `literature/` | Scopus exports and the screening table used for the literature review |

## 2. Requirements

- Python 3.11 or later (tested on Linux; runs on Windows and macOS).
- About 8 GB of RAM for the analysis stage; 16 GB for rebuilding the panel.
- Disk: 3 GB for the package with extracted FAOSTAT/UCDP files; 1.4 GB more for the ERA5 grids if rebuilding.

Set up an environment from the package root:

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate      macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Running

**Analysis stage (all tables and figures, from the shipped panel):**

```bash
python run_all.py
```

This takes about 1 to 2 hours on a laptop; the causal forest (`07`) and the robustness scripts are the slowest. Outputs overwrite `output/tables/` and `output/figures/`. The first run of `11` extracts the FAOSTAT and UCDP zip files in place. Without the ERA5 grids, `10` keeps the shipped index-variant rows (S1) and entry test, and `07` uses `data/processed/market_moderators.csv`.

**Full rebuild (raw data to panel, then analysis):**

```bash
python code/01_era5_monthly.py 1990 2026   # downloads ERA5 from gs://gcp-public-data-arco-era5 (anonymous, about 1.4 GB after aggregation)
python run_all.py --full
```

`--full` re-runs `01`, `02` and `04` before the analysis stage, and `13` (supply-area weather) after it. To also recompute the market moderators from the grids, delete `data/processed/market_moderators.csv` first. To re-download the WFP files, run `code/00_download_wfp.py` (needs access to data.humdata.org).

**Monte Carlo validation of the estimators:**

```bash
python code/99_simulate_panel.py
INSTRUMENT=Z python code/05_estimate.py data/processed/panel_sim.parquet 6
```

## 4. Map from scripts to the paper

| Script | Produces | Paper |
|---|---|---|
| `01_era5_monthly.py` | `data/raw/era5_monthly/*.npz` | Weather inputs (Section 3.2) |
| `02_exporter_instrument.py` | `data/processed/instrument.csv` | Appendix A |
| `03_first_stage.py`, `03b_first_stage_variants.py` | `first_stage_lp.csv`, `first_stage_variants.csv` | Table A.1 |
| `04_build_wfp_panel.py` | `data/processed/panel.parquet` | Sample and W index (Sections 3.1 to 3.3) |
| `05_estimate.py`, `05b_lpiv_cumulative.py` | `rf_ols_iv_ar_panel.csv`, `lpiv_cumulative_panel.csv` | Table A.2 |
| `06_local_weather.py` | `lw_main.csv`, `lw_placebo.csv` | Tables 2 and 3, placebo tests (Section 5.1 to 5.2) |
| `07_heterogeneity.py` | `het_terciles.csv`, `het_quintiles.csv`, `het_blp.csv`, `het_forest_importance.csv` | Table 4; quintiles (PAP grouping) in Section 5.3 |
| `08_figures.py` | `fig1_main_irf.png`, `fig2_tradability.png`, `fig3_components.png` | Figures 1 to 3 |
| `09_robustness.py` | `robustness.csv` | Table 7 |
| `10_selection_sensitivity.py` | `sensitivity.csv`, `selection_entry.csv`, `multiple_testing.csv` | Table 7; Holm correction; entry test (Section 6) |
| `11_mechanism_moderators.py` | `descriptives.csv`, `mech_production.csv`, `moderators.csv`, `welfare_exposure.csv` | Tables 1, 5 and 6; welfare exposure (Section 5.5) |
| `12_winsorize.py` | `winsorized.csv` | Table 7 |
| `13_supply_area.py` | `supply_area.csv` | Table 7 (supply-area rows), Section 6. Needs the ERA5 grids |

## 5. Constructed variables

- **Prices.** Retail prices only; staple groups assigned by regular expression on the WFP commodity name (`GROUP_PATTERNS` in `04_build_wfp_panel.py`). Series = country × market × commodity × unit (monthly median price). Outcome: $y_{h}=\ln p_{t+h}-\ln p_{t-1}$, reported in percent.
- **Weather index W.** At each market's 0.25° cell: 3-month mean heat (ERA5 HDD30), soil moisture (ERA5 swvl1) and rainfall (GPCP), each standardized against the 1991–2020 market × calendar-month climatology (s.d. floored at its 10th percentile, z clipped at ±4). $W=\mathrm{std}\big((z_{heat}-z_{soil}-z_{rain})/3\big)$, so positive values are hotter and drier than normal.
- **World price and exchange rate.** Matched IMF world price by group (wheat, maize, rice; coarse grains and roots matched to maize). Monthly exchange rate = country median of local-currency over US-dollar prices in the WFP files.
- **Moderators.** Cereal import dependence from FBS 2010–2013; conflict exposure = log(1 + UCDP fatalities within 50 km over the previous 12 months); remoteness = log distance to the nearest city ≥ 500,000 (Natural Earth); aridity = log mean annual GPCP precipitation 1991–2020.

## 6. Data sources and licenses

| Source | Access | License / terms |
|---|---|---|
| WFP via HDX | https://data.humdata.org/dataset/global-wfp-food-prices (accessed 7 October 2026) | CC BY-IGO |
| ERA5 (ARCO-ERA5) | gs://gcp-public-data-arco-era5 | Copernicus licence |
| GPCP v2.3 | s3://noaa-cdr-precip-gpcp-monthly-pds | NOAA open data |
| FAOSTAT | https://www.fao.org/faostat | CC BY 4.0 |
| UCDP GED v26.1 | https://ucdp.uu.se/downloads | CC BY 4.0 |
| Natural Earth | https://www.naturalearthdata.com | Public domain |
| IMF primary commodity prices via FRED | https://fred.stlouisfed.org | Public; cite IMF |

Please cite the original sources (see the paper's data references) when reusing these files.
