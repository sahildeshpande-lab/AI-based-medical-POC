# AI-based Medical POC Documentation

## Problem Statement 📌
Clinicians often need to quickly synthesize insights from a vast and growing body of medical literature and clinical trial data. Manual searches across PubMed, ClinicalTrials.gov, and other sources can be time-consuming and error-prone. There is a need for an automated assistant that retrieves, analyzes, and summarizes medical evidence to answer clinical questions with supporting citations.

## Project Description 💡
This proof-of-concept application uses AI and open biomedical APIs to fetch and process research data, generate concise medical answers, and present them through a simple web interface. Users submit clinical questions, and the system searches PubMed abstracts and clinical trial databases. Retrieved documents are embedded, stored in a vector database, and relevant passages are fed into an LLM (Groq) for structured answer generation. The app enriches drug information with normalization and dosage details.

## Architecture Overview 🏗️
```mermaid
flowchart LR
    subgraph Backend
        A[FastAPI Server] --> B(Query Service)
        B -->|PubMed search| C[ESearch + EFetch]
        B --> D[PubMed parser]
        B --> E[PMC fetch & parser]
        B --> F[ClinicalTrials.gov service]
        B --> G[FAISS Vector Store]
        B --> H[Embedding (SentenceTransformer)]
        B --> I[Groq LLM client]
        B --> J[Drug Validator & Dose Fetcher]
    end
    subgraph Frontend
        U[React UI] -->|POST /query| A
    end
    style Backend fill:#f9f,stroke:#333,stroke-width:1px
    style Frontend fill:#bbf,stroke:#333,stroke-width:1px
```
*The backend orchestrates search, embedding, retrieval, LLM generation, and validation.*

## Flowchart 🔄
```mermaid
flowchart TD
    user[User question] -->|HTTP POST| server[FastAPI /query]
    server --> service{handle_query}
    service --> esearch[search_pubmed]
    esearch --> efetch[fetch_abstracts]
    efetch --> parser[parse_abstracts]
    parser --> sections[collect sections]
    sections --> pmc_lookup[get_pmc_id && fetch & parse]
    sections --> embedding[embed_text]
    embedding --> faiss[FAISSStore.add]
    service --> query_embed[embed_text(query)]
    query_embed --> faiss_search[FAISSStore.search]
    faiss_search --> evidence_pack[prepare evidence]
    service --> trials[search_trials]
    trials --> trials_to_evidence
    evidence_pack --> llm[generate_answer]
    llm --> later[drug normalization & dosage]
    later --> response[return JSON]
    response --> user
```
*A high-level flow from user input to final JSON response.*

## Technologies Used 🛠️
- **Backend:** Python, FastAPI, asyncio
- **Embedding & Vector Search:** SentenceTransformers (`all-MiniLM-L6-v2`), FAISS
- **LLM Integration:** Groq API (llama-3.1-8b-instant)
- **HTTP Clients:** `requests`, `httpx`
- **Parsing:** `lxml`
- **Frontend:** React, Vite, CSS
- **Environment:** `python-dotenv` for config

## External APIs Used 🌐
- **PubMed E-utilities:** esearch.fcgi, efetch.fcgi, elink.fcgi for abstracts and PMC IDs
- **ClinicalTrials.gov API:** JSON endpoints for trial search
- **RxNorm:** `/rxcui.json` for drug normalization
- **DailyMed:** `/spls.json` for dosage information
- **Groq LLM:** chat completions endpoint

---

This document outlines the core components and flows of the AI-based medical assistant POC. It can serve as a reference for developers and stakeholders understanding system design and technology choices.