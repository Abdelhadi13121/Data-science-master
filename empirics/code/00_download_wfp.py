"""Download the WFP 'Global - Food Prices' yearly CSVs and metadata from HDX (CKAN API).

Requires network access to data.humdata.org. Output: data/raw/wfp/*.csv
"""
import json
import os
import urllib.request

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "wfp")
API = "https://data.humdata.org/api/3/action/package_show?id=global-wfp-food-prices"

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with urllib.request.urlopen(API) as r:
        resources = json.load(r)["result"]["resources"]
    for res in resources:
        url = res["url"]
        name = url.rsplit("/", 1)[1]
        if name.endswith("_1900.csv"):  # placeholder file
            continue
        dest = os.path.join(OUT, name)
        if not os.path.exists(dest):
            urllib.request.urlretrieve(url, dest)
        print(name, os.path.getsize(dest))
