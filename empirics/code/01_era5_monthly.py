"""Build monthly ERA5 climate grids (0.25 deg) from the public ARCO-ERA5 Zarr store.

Outputs one compressed .npz per month in data/raw/era5_monthly/YYYY-MM.npz with
  tmean   : monthly mean 2 m temperature (deg C), from 00/06/12/18 UTC samples
  tmax    : monthly mean of daily max over the 4 samples (deg C)
  hdd30   : sum over days of max(Tmax_day - 30, 0)  (extreme-heat degree days)
  swvl1   : monthly mean volumetric soil water, layer 1 (m3/m3), 12 UTC samples
Arrays are float16 on the native 721 x 1440 grid (lat 90..-90, lon 0..359.75).

Resumable: months already written are skipped. Run:  python 01_era5_monthly.py 1990 2026
"""
import concurrent.futures as cf
import os
import sys
import time

import numpy as np
import pandas as pd
import xarray as xr

STORE = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "era5_monthly")
os.makedirs(OUT, exist_ok=True)

ds = xr.open_zarr(STORE, storage_options={"token": "anon"}, chunks=None)
T2M, SWV = ds["2m_temperature"], ds["volumetric_soil_water_layer_1"]
LAST_VALID = pd.Timestamp(ds.attrs.get("valid_time_stop_era5t", "2026-06-30"))


def fetch(var, t):
    for attempt in range(5):
        try:
            return var.sel(time=t).values.astype(np.float32)
        except Exception:  # transient network error
            time.sleep(2 ** attempt)
    raise RuntimeError(f"failed {var.name} {t}")


def month(ym, pool):
    days = pd.date_range(ym, ym + pd.offsets.MonthEnd(0), freq="D")
    days = days[days < LAST_VALID]
    if len(days) < 25:
        return None
    hours = [d + pd.Timedelta(hours=h) for d in days for h in (0, 6, 12, 18)]
    t = np.stack(list(pool.map(lambda x: fetch(T2M, x), hours))) - 273.15
    t = t.reshape(len(days), 4, *t.shape[1:])
    dmax = t.max(axis=1)
    sw = np.stack(list(pool.map(lambda d: fetch(SWV, d + pd.Timedelta(hours=12)), days)))
    return dict(
        tmean=t.mean(axis=(0, 1)).astype(np.float16),
        tmax=dmax.mean(axis=0).astype(np.float16),
        hdd30=np.clip(dmax - 30.0, 0, None).sum(axis=0).astype(np.float16),
        swvl1=sw.mean(axis=0).astype(np.float16),
        ndays=len(days),
    )


if __name__ == "__main__":
    y0, y1 = int(sys.argv[1]), int(sys.argv[2])
    months = pd.date_range(f"{y0}-01-01", f"{y1}-12-01", freq="MS")
    with cf.ThreadPoolExecutor(24) as pool:
        for ym in months:
            f = os.path.join(OUT, f"{ym:%Y-%m}.npz")
            if os.path.exists(f):
                continue
            t0 = time.time()
            res = month(ym, pool)
            if res is None:
                print(f"{ym:%Y-%m} skipped (beyond ERA5T availability)", flush=True)
                break
            np.savez_compressed(f + ".tmp.npz", **res)
            os.replace(f + ".tmp.npz", f)
            print(f"{ym:%Y-%m} done in {time.time() - t0:.0f}s", flush=True)
