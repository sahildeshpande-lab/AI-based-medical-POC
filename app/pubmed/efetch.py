import requests
from app.config import PUBMED_BASE

def fetch_abstracts(pmids):
    ids = ",".join(pmids)
    url = f"{PUBMED_BASE}/efetch.fcgi"

    params = {
        "db": "pubmed",
        "id": ids,
        "retmode": "xml"
    }

    response = requests.get(url, params=params)
    return response.text