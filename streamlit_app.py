import streamlit as st
import asyncio
from app.services.query_service import handle_query

st.set_page_config(
    page_title="PubMed Based Retriever",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background-color: #0b0f1a;
    color: #d6dce8;
}

.pubmed-header {
    padding: 2.5rem 0 1.5rem;
    border-bottom: 1px solid #1e2740;
    margin-bottom: 2rem;
}
.pubmed-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: #e8edf5;
    margin: 0;
    letter-spacing: -0.02em;
}
.pubmed-header p {
    font-size: 0.85rem;
    color: #4a5568;
    margin: 0.3rem 0 0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.stTextInput > div > div > input {
    background-color: #111827 !important;
    border: 1px solid #1e2d45 !important;
    border-radius: 10px !important;
    color: #cbd5e1 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s ease;
}
.stTextInput > div > div > input:focus {
    border-color: #2e6df5 !important;
    box-shadow: 0 0 0 3px rgba(46, 109, 245, 0.12) !important;
}
.stTextInput > div > div > input::placeholder {
    color: #3a4a60 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #1a4fd6, #2e6df5) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 2rem !important;
    letter-spacing: 0.03em;
    transition: opacity 0.2s ease, transform 0.1s ease !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

.result-block {
    background: #111827;
    border: 1px solid #1e2740;
    border-radius: 14px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
}
.result-block .question-label {
    font-family: 'DM Serif Display', serif;
    font-size: 1.25rem;
    color: #e2e8f0;
    margin-bottom: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.result-block .summary-text {
    font-size: 0.92rem;
    color: #94a3b8;
    line-height: 1.75;
    margin-bottom: 0.6rem;
}

.drug-pill {
    background: #0f1e35;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}
.drug-pill .drug-name {
    font-weight: 500;
    color: #93c5fd;
    font-size: 0.9rem;
}
.drug-pill .drug-meta {
    font-size: 0.78rem;
    color: #4a6080;
    margin-top: 0.2rem;
}

h3, .stSubheader, [data-testid="stSubheader"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #3b6fd4 !important;
    margin-top: 1.4rem !important;
    margin-bottom: 0.6rem !important;
}

hr {
    border-color: #1a2440 !important;
    margin: 1rem 0 !important;
}

.citation-item {
    font-size: 0.82rem;
    color: #4a6080;
    padding: 0.25rem 0;
}
.citation-item a {
    color: #3b6fd4 !important;
    text-decoration: none;
}
.citation-item a:hover {
    text-decoration: underline;
}

.stSpinner > div {
    border-top-color: #2e6df5 !important;
}
.st-emotion-cache-14vh5up {
    background-color: #0b0f1a;
    color: #d6dce8;
}

.stAlert {
    background-color: #1a0f18 !important;
    border-color: #6b2140 !important;Advanced app settings
    color: #f87171 !important;
    border-radius: 10px !important;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0b0f1a; }
::-webkit-scrollbar-thumb { background: #1e2d45; border-radius: 4px; }
</style>

<div class="pubmed-header">
    <h1>PubMed Retriever</h1>
    <p>Evidence-based medical query engine</p>
</div>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input(
    "",
    placeholder="Ask a medical question — e.g. treatment for type 2 diabetes"
)

ask = st.button("Ask")

if ask and query.strip():
    with st.spinner("Searching PubMed..."):
        try:
            data = asyncio.run(handle_query(query))
            st.session_state.history.append({"question": query, "data": data})
        except Exception as e:
            st.error(f"Error: {e}")

for item in reversed(st.session_state.history):

    data = item.get("data", {})

    st.markdown('<div class="result-block">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="question-label">🔎 {item.get("question", "")}</div>',
        unsafe_allow_html=True
    )

    if data.get("error"):
        st.error(data.get("error"))
        if data.get("details"):
            st.caption(data.get("details"))
        st.markdown('</div>', unsafe_allow_html=True)
        continue

    disease          = data.get("disease", "Unknown condition")
    disease_summary  = data.get("disease_summary", "No summary available.")
    treatment_summary = data.get("treatment_summary", "No treatment information available.")

    st.markdown(
        f'<p class="summary-text"><strong style="color:#cbd5e1">{disease}</strong> — {disease_summary}</p>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<p class="summary-text">{treatment_summary}</p>',
        unsafe_allow_html=True
    )

    drugs = data.get("drugs") or [
        {"name": d, "rxnorm": None, "dosage": None}
        for d in data.get("recommended_drugs", [])
    ]

    if drugs:
        st.subheader("Medicines")
        cols = st.columns(3)
        for i, drug in enumerate(drugs):
            with cols[i % 3]:
                name   = drug.get("name", "Unknown drug")
                rxnorm = drug.get("rxnorm")
                dosage = drug.get("dosage")
                meta_parts = []
                if rxnorm:
                    meta_parts.append(f"RxNorm: {rxnorm}")
                if dosage and isinstance(dosage, dict):
                    meta_parts.append(dosage.get("label", ""))
                meta_html = " · ".join(filter(None, meta_parts))
                st.markdown(
                    f'<div class="drug-pill">'
                    f'<div class="drug-name">{name}</div>'
                    f'<div class="drug-meta">{meta_html}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    citations = data.get("citations", [])
    if citations:
        st.subheader("References")
        for i, c in enumerate(citations):
            url = f"https://pubmed.ncbi.nlm.nih.gov/{c}"
            st.markdown(
                f'<div class="citation-item">{i+1}. <a href="{url}" target="_blank">PubMed {c}</a></div>',
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)