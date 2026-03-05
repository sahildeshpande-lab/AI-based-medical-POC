import requests

DAILYMED_BASE = "https://dailymed.nlm.nih.gov/dailymed/services/v2"


def get_dosage(drug_name):

    try:

        url = f"{DAILYMED_BASE}/spls.json"
        params = {"drug_name": drug_name}

        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        spls = data.get("data", [])

        if not spls:
            return None

        return {
            "drug": drug_name,
            "label": spls[0].get("title")
        }

    except Exception:
        return None