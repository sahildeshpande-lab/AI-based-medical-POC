import requests


RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"


def normalize_drug(drug_name):
    """
    Convert drug name to RxNorm standard.
    """

    try:
        url = f"{RXNORM_BASE}/rxcui.json"
        params = {"name": drug_name}

        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        ids = data.get("idGroup", {}).get("rxnormId", [])

        if not ids:
            return None

        return {
            "name": drug_name,
            "rxcui": ids[0]
        }

    except Exception:
        return None