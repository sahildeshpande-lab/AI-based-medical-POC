from app.pubmed.esearch import search_pubmed
from app.pubmed.efetch import fetch_abstracts
from app.pubmed.parser import parse_abstracts, parse_pmc_fulltext
from app.pubmed.pmc import get_pmc_id, fetch_pmc_fulltext
from app.embeddings.embedder import embed_text
from app.vectorstore.faiss_store import FAISSStore
from app.llm.groq_client import generate_answer
from app.validation.citation_validator import validate_citations

import numpy as np


async def handle_query(query: str):

    try:
        pmids = search_pubmed(query, retmax=5)

        if not pmids:
            return {"error": "No PubMed results found"}

        all_chunks = []

        # 🔁 For each PMID → Try PMC first
        for pmid in pmids:

            pmc_id = get_pmc_id(pmid)

            if pmc_id:
                full_xml = fetch_pmc_fulltext(pmc_id)
                sections = parse_pmc_fulltext(full_xml, pmid)

                if sections:
                    all_chunks.extend(sections)
                    continue

            # 🔄 Fallback to abstract
            xml_data = fetch_abstracts([pmid])
            abstracts = parse_abstracts(xml_data)

            all_chunks.extend(abstracts)

        if not all_chunks:
            return {"error": "No usable content found"}

        texts = [c["text"] for c in all_chunks]
        pmid_list = [c["pmid"] for c in all_chunks]

        embeddings = [embed_text(t) for t in texts]

        vectors = np.vstack(embeddings).astype("float32")
        dimension = vectors.shape[1]

        store = FAISSStore(dimension)
        store.index.add(vectors)
        store.documents = list(range(len(texts)))

        query_embedding = embed_text(query).astype("float32")

        D, I = store.index.search(
            np.array([query_embedding]),
            min(7, len(texts))
        )

        evidence_pack = []

        for idx in I[0]:
            evidence_pack.append({
                "pmid": pmid_list[idx],
                "text": texts[idx]
            })

        llm_output = generate_answer(query, evidence_pack)

        if not isinstance(llm_output, dict):
            return {"error": "Invalid LLM response format"}

        if "error" in llm_output:
            return llm_output

        if not validate_citations(llm_output, evidence_pack):
            return {"error": "Invalid citation detected"}

        return {
            "summary": llm_output.get("summary"),
            "citations": llm_output.get("citations"),
            "evidence_used": len(evidence_pack),
            "total_chunks_indexed": len(all_chunks)
        }

    except Exception as e:
        return {
            "error": "Internal server error",
            "details": str(e)
        }