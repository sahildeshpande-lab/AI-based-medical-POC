import requests
from lxml import etree
from app.config import PUBMED_BASE


def get_pmc_id(pmid):
    """
    Convert PMID → PMC ID if available
    """

    url = f"{PUBMED_BASE}/elink.fcgi"

    params = {
        "dbfrom": "pubmed",
        "db": "pmc",
        "id": pmid
    }

    try:

        response = requests.get(url, params=params, timeout=10)

        if not response.text.strip():
            return None

        root = etree.fromstring(response.content)

        link = root.find(".//Link/Id")

        if link is not None:
            return link.text

    except Exception:
        return None

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