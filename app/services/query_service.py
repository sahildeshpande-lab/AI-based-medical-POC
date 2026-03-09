import asyncio
from app.pubmed.esearch import search_pubmed
from app.pubmed.efetch import fetch_abstracts
from app.pubmed.parser import parse_abstracts, parse_pmc_fulltext

from app.pubmed.pmc import get_pmc_id, fetch_pmc_fulltext

from app.embeddings.embedder import embed_text
from app.vectorstore.faiss_store import FAISSStore

from app.llm.groq_client import generate_answer

from app.validation.drug_validator import normalize_drug
from app.validation.dose_fetcher import get_dosage

from app.services.clinical_trials import search_trials, trials_to_evidence


async def handle_query(query: str):

    pmids = search_pubmed(query)

    if not pmids:
        return {"error": "No PubMed results found"}

    xml_data = fetch_abstracts(pmids)

    if not xml_data:
        return {"error": "Failed to fetch PubMed abstracts"}

    abstracts = parse_abstracts(xml_data)

    if not abstracts:
        return {"error": "No abstracts found"}

    all_sections = []

    for article in abstracts:

        pmid = article.get("pmid")

        if not pmid:
            continue

        all_sections.append(article)

        pmc_id = get_pmc_id(pmid)

        if pmc_id:
            try:
                full_xml = fetch_pmc_fulltext(pmc_id)

                sections = parse_pmc_fulltext(full_xml, pmid)

                all_sections.extend(sections)

            except Exception:
                pass

    if not all_sections:
        return {"error": "No text sections available"}

    store = FAISSStore(384)

    texts = [s["text"] for s in all_sections if s["text"].strip()]

    embeddings = [embed_text(t) for t in texts]

    store.add(texts, embeddings)

    query_embedding = embed_text(query)

    search_results = store.search(query_embedding)

    evidence_pack = []

    for i, chunk in enumerate(search_results):

        if i >= len(all_sections):
            break

        evidence_pack.append({
            "pmid": all_sections[i]["pmid"],
            "text": chunk
        })

    trials = await search_trials(query)

    trial_evidence = trials_to_evidence(trials)

    evidence_pack.extend(trial_evidence)

    llm_output = generate_answer(query, evidence_pack)

    if not llm_output or "error" in llm_output:
        return {"error": "LLM generation failed"}

    drugs = llm_output.get("recommended_drugs", [])

    enriched_drugs = []

    for drug in drugs:

        normalized = normalize_drug(drug)

        dosage = get_dosage(drug)

        enriched_drugs.append({
            "name": drug,
            "rxnorm": normalized["rxcui"] if normalized else None,
            "dosage": dosage
        })

    return {
        "disease": llm_output.get("disease"),
        "disease_summary": llm_output.get("disease_summary"), 
        "treatment_summary": llm_output.get("treatment_summary"),
        "drugs": enriched_drugs,
        "citations": llm_output.get("citations", [])
    }