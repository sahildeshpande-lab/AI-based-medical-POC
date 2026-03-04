import requests
from app.config import PUBMED_BASE

def search_pubmed(query, retmax=10):
    url = f"{PUBMED_BASE}/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": retmax,
        "sort": "relevance"
    }

    response = requests.get(url, params=params)
    data = response.json()
    return data["esearchresult"]["idlist"]