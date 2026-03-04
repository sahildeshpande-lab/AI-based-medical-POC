from app.pubmed.esearch import search_pubmed
from app.pubmed.efetch import fetch_abstracts
from app.pubmed.parser import parse_abstracts
from app.embeddings.embedder import embed_text
from app.vectorstore.faiss_store import FAISSStore
from app.llm.groq_client import generate_answer
from app.validation.citation_validator import validate_citations

import numpy as np


async def handle_query(query: str):

    try:
        pmids = search_pubmed(query)

        if not pmids:
            return {"error": "No PubMed results found"}
        xml_data = fetch_abstracts(pmids)
        abstracts = parse_abstracts(xml_data)

        if not abstracts:
            return {"error": "No abstracts found for this query"}
        
        texts = []
        pmid_list = []

        for article in abstracts:
            if article.get("text"):
                texts.append(article["text"])
                pmid_list.append(article["pmid"])

        if not texts:
            return {"error": "No valid abstract text available"}

        embeddings = [embed_text(t) for t in texts]

        if len(embeddings) == 0:
            return {"error": "Embedding generation failed"}

        vectors = np.vstack(embeddings).astype("float32")
        dimension = vectors.shape[1]
        store = FAISSStore(dimension)

        store.index.add(vectors)
        store.documents = list(range(len(texts))) 
        query_embedding = embed_text(query).astype("float32")

        D, I = store.index.search(
            np.array([query_embedding]), 
            min(5, len(texts))
        )

        if len(I[0]) == 0:
            return {"error": "Vector search failed"}

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
            "evidence_count": len(evidence_pack)
        }

    except Exception as e:
        return {
            "error": "Internal server error",
            "details": str(e)
        }