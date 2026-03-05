import requests
from app.config import PUBMED_BASE

def get_pmc_id(pmid):
    """
    Convert PMID → PMC ID if available
    """
    url = f"{PUBMED_BASE}/elink.fcgi"
    params = {
        "dbfrom": "pubmed",
        "db": "pmc",
        "id": pmid,
        "retmode": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()

    try:
        links = data["linksets"][0]["linksetdbs"][0]["links"]
        return links[0]  # PMC ID
    except (KeyError, IndexError):
        return None


def fetch_pmc_fulltext(pmc_id):
    """
    Fetch full XML from PMC
    """
    url = f"{PUBMED_BASE}/efetch.fcgi"
    params = {
        "db": "pmc",
        "id": pmc_id,
        "retmode": "xml"
    }

    response = requests.get(url, params=params)
    return response.text