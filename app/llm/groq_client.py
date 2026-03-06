import json
import re
from groq import Groq
from app.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def extract_json(text):
    """
    Safely extract the first valid JSON object from LLM output
    """
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return None

    return text[start:end + 1]


def generate_answer(query, evidence_pack):
    """
    Generate structured medical answer using Groq LLM
    """

    # Build research context
    context = "\n\n".join(
        [
            f"""
PMID: {e['pmid']}
Evidence:
{e['text']}
"""
            for e in evidence_pack
        ]
    )

    messages = [
        {
            "role": "system",
            "content": """
You are a clinical research evidence assistant used by doctors.

STRICT RULES:

1. Use ONLY the provided research evidence.
2. Do NOT invent medical facts.
3. Extract drugs ONLY if mentioned in the evidence.
4. Every treatment claim MUST reference a PMID.
5. Disease summary should follow WHO-style medical description.
6. If evidence does not mention drugs, return an empty list.
7. Output STRICTLY VALID JSON only.
8. Do NOT add explanations outside JSON.

JSON FORMAT:

{
  "disease": "detected disease",

  "disease_summary": "short WHO-style description including cause, pathogen, and key symptoms",

  "treatment_summary": "brief summary of treatment based on evidence",

  "recommended_drugs": ["drug1","drug2"],

  "citations": ["PMID1","PMID2"]
}
"""
        },
        {
            "role": "user",
            "content": f"""
Clinical Research Evidence:

{context}

User Question:
{query}

Tasks:

1. Identify the disease mentioned in the evidence.
2. Write a short WHO-style disease summary.
3. Summarize the treatment approach.
4. Extract drug names ONLY if mentioned in the evidence.
5. Cite the PMID sources used.

Return STRICT JSON only.
"""
        }
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0
        )

        raw_output = response.choices[0].message.content.strip()

    except Exception as e:
        return {
            "error": "Groq API call failed",
            "details": str(e)
        }

    json_block = extract_json(raw_output)

    if not json_block:
        return {
            "error": "No JSON found in LLM response",
            "raw_output": raw_output
        }

    try:
        parsed = json.loads(json_block)
        return parsed

    except json.JSONDecodeError as e:
        return {
            "error": "Invalid JSON returned by LLM",
            "details": str(e),
            "raw_output": raw_output
        }
