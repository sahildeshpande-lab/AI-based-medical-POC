import requests
from app.config import PUBMED_BASE


def fetch_abstracts(pmids):
    """
    Fetch abstracts from PubMed given a list of PMIDs.
    """

    if not pmids:
        return ""

    if isinstance(pmids, list):
        ids = ",".join(pmids)
    else:
        ids = str(pmids)

    url = f"{PUBMED_BASE}/efetch.fcgi"

    params = {
        "db": "pubmed",
        "id": ids,
        "retmode": "xml"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.text or ""

    except Exception as e:
        print("EFetch Error:", e)
        return ""