import json
from groq import Groq
from app.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def generate_answer(query, evidence_pack):
    context = "\n\n".join(
        [f"PMID:{e['pmid']} - {e['text']}" for e in evidence_pack]
    )

    messages = [
    {
        "role": "system",
        "content": """
You are a clinical evidence assistant.

RULES:
- Use ONLY provided research evidence.
- Extract treatment drugs mentioned.
- Every claim must cite PMID.
- Return ONLY JSON.
- Do NOT add explanations.

Output format:

{
  "disease": "detected disease",
  "recommended_drugs": ["drug1","drug2"],
  "treatment_summary": "short explanation",
  "citations": ["PMID1","PMID2"]
}
"""
    },
    {
        "role": "user",
        "content": f"""
Evidence:
{context}

Question:
{query}
"""
    }
]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw_output)
        return parsed
    except json.JSONDecodeError:
        return {
            "error": "LLM returned invalid JSON",
            "raw_output": raw_output
        }