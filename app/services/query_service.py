from app.pubmed.esearch import search_pubmed
from app.pubmed.efetch import fetch_abstracts
from app.pubmed.parser import parse_abstracts

from app.embeddings.embedder import embed_text
from app.vectorstore.faiss_store import FAISSStore

from app.llm.groq_client import generate_answer

from app.validation.drug_validator import normalize_drug
from app.validation.dose_fetcher import get_dosage


async def handle_query(query):

    pmids = search_pubmed(query)

    xml_data = fetch_abstracts(pmids)

    abstracts = parse_abstracts(xml_data)

    if not abstracts:
        return {"error": "No abstracts found"}

    store = FAISSStore(384)

    texts = [a["text"] for a in abstracts]

    embeddings = [embed_text(t) for t in texts]

    store.add(texts, embeddings)

    query_embedding = embed_text(query)

    top_chunks = store.search(query_embedding)

    evidence_pack = [
        {"pmid": abstracts[i]["pmid"], "text": top_chunks[i]}
        for i in range(min(len(abstracts), len(top_chunks)))
    ]

    llm_output = generate_answer(query, evidence_pack)

    if "error" in llm_output:
        return llm_output

    drugs = llm_output.get("recommended_drugs", [])

    enriched_drugs = []

    for drug in drugs:

        normalized = normalize_drug(drug)

        if not normalized:
            continue

        dosage = get_dosage(drug)

        enriched_drugs.append({
            "name": drug,
            "rxnorm": normalized["rxcui"],
            "dosage": dosage
        })

    return {
        "disease": llm_output.get("disease"),
        "treatment_summary": llm_output.get("treatment_summary"),
        "drugs": enriched_drugs,
        "citations": llm_output.get("citations")
    }