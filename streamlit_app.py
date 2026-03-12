import streamlit as st
import asyncio
from app.services.query_service import handle_query

st.set_page_config(
    page_title="PubMed Based Retriever",
    layout="wide"
)

st.session_state.history = []

st.title("PubMed Based Retriever®")

col1, col2 = st.columns([6,1])

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

    data = item["data"]

    st.markdown("---")

    st.markdown(f"### 🔎 {item['question']}")

    st.markdown(
        f"A **{data['disease']}** {data['disease_summary']}"
    )

    st.markdown(data["treatment_summary"])

    if data.get("drugs"):

        st.subheader("Drugs")

        cols = st.columns(3)

        for i, drug in enumerate(data["drugs"]):

            with cols[i % 3]:

                st.markdown(
                    f"""
                    **{drug['name']}**

                    {'RxNorm: ' + drug['rxnorm'] if drug.get('rxnorm') else ''}

                    {drug['dosage']['label'] if drug.get('dosage') else ''}
                    """
                )


    if data.get("citations"):

        st.subheader("References")

        for i, c in enumerate(data["citations"]):

            url = f"https://pubmed.ncbi.nlm.nih.gov/{c}"

            st.markdown(
                f"{i+1}. [PubMed Article {c}]({url})"
            )