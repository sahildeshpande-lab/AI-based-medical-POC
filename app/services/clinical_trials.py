import httpx
import textwrap
from typing import List, Dict, Any

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

async def search_trials(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch clinical trials from ClinicalTrials.gov for a given disease query.
    """
    params = {
        "query.term": query, 
        "pageSize": limit
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(BASE_URL, params=params)

        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return []

        data = response.json()
        trials = []

        for study in data.get("studies", []):
            protocol = study.get("protocolSection", {})

            identification = protocol.get("identificationModule", {})
            description = protocol.get("descriptionModule", {})
            design = protocol.get("designModule", {})
            conditions = protocol.get("conditionsModule", {})

            trials.append({
                "nct_id": identification.get("nctId"),
                "title": identification.get("briefTitle", "No title provided"),
                "condition": conditions.get("conditions") or [],
                "summary": description.get("briefSummary", "No summary available"),
                "study_type": design.get("studyType", "Unknown")
            })

        return trials

    except Exception as e:
        print(f"Exception occurred while fetching trials: {e}")
        return []

def trials_to_evidence(trials: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Convert a list of clinical trials into an evidence format.
    """
    evidence = []

    for t in trials:
        text = textwrap.dedent(f"""
            Clinical Trial: {t['title']}
            Condition: {', '.join(t['condition'] or [])}
            Summary: {t['summary']}
            Study Type: {t['study_type']}
        """).strip()

        evidence.append({
            "pmid": f"NCT:{t['nct_id']}",
            "text": text
        })

    return evidence

