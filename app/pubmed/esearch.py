import requests
from app.config import PUBMED_BASE


def search_pubmed(query, retmax=5):
    """
    Search PubMed and return list of PMIDs.
    Automatically enriches query for treatment-related searches.
    """

    # Auto-enrich query for treatment intent
    if "treat" in query.lower() or "therapy" in query.lower():
        query = f"({query}) AND (treatment OR therapy OR drug OR management)"

    url = f"{PUBMED_BASE}/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": retmax,
        "sort": "relevance",
        "lang": "eng"  # English only
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return data.get("esearchresult", {}).get("idlist", [])

    except Exception as e:
        print("ESearch Error:", e)
        return []