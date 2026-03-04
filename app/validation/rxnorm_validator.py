import requests
from app.config import RXNORM_BASE

def validate_drug(drug_name):
    url = f"{RXNORM_BASE}/rxcui.json"
    params = {"name": drug_name}

    response = requests.get(url, params=params)
    data = response.json()

    return data.get("idGroup", {}).get("rxnormId")