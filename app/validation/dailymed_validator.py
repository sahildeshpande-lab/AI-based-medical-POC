import requests
from app.config import DAILYMED_BASE

def check_drug_label(drug_name):
    url = f"{DAILYMED_BASE}/spls.json"
    params = {"drug_name": drug_name}

    response = requests.get(url, params=params)
    return response.json()