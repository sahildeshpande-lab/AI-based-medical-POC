import requests
from app.config import PUBMED_BASE


def search_pubmed(query, retmax=10):
    """
    Search PubMed and return list of PMIDs.

    The ``retmax`` parameter controls how many results to fetch from the
    ESearch API (the earlier name ``max_results`` used in this project was
    incorrect).  The function also applies a small query enrichment when the
    input mentions treatment keywords to focus on human drug therapy studies.
    """

    if "treat" in query.lower() or "therapy" in query.lower():
        query = f"""({query}) AND (humans[MeSH Terms]) AND (english[lang]) AND ("Drug Therapy"[MeSH Terms] OR "Therapeutics"[MeSH Terms])"""

    url = f"{PUBMED_BASE}/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": retmax,
        "sort": "relevance",
        "lang": "eng"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return data.get("esearchresult", {}).get("idlist", [])

    except Exception as e:
        print("ESearch Error:", e)
        return []