"""Monte Carlo validation panel with the exact schema of data/processed/panel.parquet.

True DGP (geometric distributed lag, lambda = 0.5):
  dlnp_it = sum_k (1-lam) lam^k [(beta + gamma W_{i,t-k}) dG_{c,t-k} + delta W_{i,t-k}]
            + theta dE_kt + kappa u_t + country-time shock + e_it
  dG_ct   = pi Z_ct + u_t + v_ct              (u_t: global demand shock -> OLS bias)
True cumulative effects at horizon h:  beta_h = beta(1-lam^{h+1}),  gamma_h = gamma(1-lam^{h+1}).
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
TRUE = dict(beta=0.40, gamma=0.20, delta=0.02, theta=0.40, kappa=0.8, pi=0.03, lam=0.5)


def simulate(K=25, M=12, seed=1):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2000-01-01", "2025-12-01", freq="MS")
    T = len(dates)
    groups = ["wheat", "maize", "rice"]
    u = rng.normal(0, 0.03, T)
    Z = {c: rng.normal(0, 1, T) for c in groups}
    dG = {c: TRUE["pi"] * Z[c] + u + rng.normal(0, 0.03, T) for c in groups}
    lG = {c: np.cumsum(dG[c]) + 5 for c in groups}
    rows = []
    lam = TRUE["lam"]
    for k in range(K):
        dE = rng.normal(0, 0.02, T)
        ck = rng.normal(0, 0.02, T)
        for m in range(M):
            lat, lon = rng.uniform(-20, 30), rng.uniform(-20, 60)
            W = rng.normal(0, 1, T)
            for c in groups:
                impulse = (TRUE["beta"] + TRUE["gamma"] * W) * dG[c] + TRUE["delta"] * W
                dist = np.zeros(T)
                acc = 0.0
                for t in range(T):  # geometric distributed lag
                    acc = lam * acc + (1 - lam) * impulse[t]
                    dist[t] = acc
                dlp = dist + TRUE["theta"] * dE + TRUE["kappa"] * u + ck + rng.normal(0, 0.03, T)
                lp = np.cumsum(dlp) + 3
                miss = rng.random(T) < 0.15  # WFP-like gaps
                lp[miss] = np.nan
                rows.append(pd.DataFrame(dict(
                    date=dates, series=f"C{k}|M{m}|{c}", countryiso3=f"C{k:02d}", market_id=m, mkey=f"C{k}|M{m}",
                    group=c, wgroup=c, latitude=lat, longitude=lon, lp=lp, lfx=np.cumsum(dE), W=W, lG=lG[c], Z=Z[c])))
    p = pd.concat(rows, ignore_index=True)
    p["dlp"] = p.groupby("series").lp.diff()
    return p


if __name__ == "__main__":
    os.makedirs(f"{ROOT}/data/processed", exist_ok=True)
    p = simulate()
    p.to_parquet(f"{ROOT}/data/processed/panel_sim.parquet", index=False)
    lam = TRUE["lam"]
    print("true beta_h :", [round(TRUE["beta"] * (1 - lam ** (h + 1)), 3) for h in range(7)])
    print("true gamma_h:", [round(TRUE["gamma"] * (1 - lam ** (h + 1)), 3) for h in range(7)])
    print(p.shape)
