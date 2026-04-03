import streamlit as st
import asyncio
from app.services.query_service import handle_query

st.set_page_config(
    page_title="PubMed Based Retriever",
    layout="wide"
)


if "history" not in st.session_state:
    st.session_state.history = []

st.title("PubMed Based Retriever®")

col1, col2 = st.columns([6, 1])

with col2:
    if st.button("✎ New Conversation"):
        st.session_state.history = []

query = st.text_input(
    "Ask a medical question...",
    placeholder="Ask a medical question..."
)

ask = st.button("Ask")


if ask and query.strip():

    with st.spinner("Thinking..."):

        try:
            data = asyncio.run(handle_query(query))

            st.session_state.history.append({
                "question": query,
                "data": data
            })

        except Exception as e:
            st.error(f"Error: {e}")


for item in st.session_state.history:

    data = item.get("data", {})

    st.markdown("---")
    st.markdown(f"### 🔎 {item.get('question', '')}")

    if data.get("error"):
        st.error(data.get("error"))
        if data.get("details"):
            st.caption(data.get("details"))
        continue

    disease = data.get("disease", "Unknown condition")
    disease_summary = data.get("disease_summary", "No summary available.")
    treatment_summary = data.get("treatment_summary", "No treatment information available.")

    st.markdown(f"A **{disease}** {disease_summary}")
    st.markdown(treatment_summary)

    drugs = data.get("drugs")

    if not drugs and data.get("recommended_drugs"):
        drugs = [
            {"name": d, "rxnorm": None, "dosage": None}
            for d in data.get("recommended_drugs", [])
        ]

    if drugs:
        st.subheader("Medicines")

        cols = st.columns(3)

        for i, drug in enumerate(drugs):

            with cols[i % 3]:

                name = drug.get("name", "Unknown drug")
                rxnorm = drug.get("rxnorm")
                dosage = drug.get("dosage")

                st.markdown(f"**{name}**")

                if rxnorm:
                    st.caption(f"RxNorm: {rxnorm}")

                if dosage and isinstance(dosage, dict):
                    st.caption(dosage.get("label", ""))


    citations = data.get("citations", [])

    if citations:
        st.subheader("References")

        for i, c in enumerate(citations):
            url = f"https://pubmed.ncbi.nlm.nih.gov/{c}"
            st.markdown(f"{i+1}. [PubMed Article {c}]({url})")