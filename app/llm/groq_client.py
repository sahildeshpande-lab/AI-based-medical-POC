import json
import re
from groq import Groq
from app.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def extract_json(text):
    """
    Extract first JSON object using regex (more reliable than find/rfind)
    """
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return match.group(0) if match else None
    except Exception:
        return None


def generate_answer(query, evidence_pack):
    """
    Generate structured medical answer using Groq LLM
    """

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

1. If user greets greet him in a same way back
2. Use ONLY the provided research evidence.
3. Do NOT invent medical facts.
4. Extract drugs ONLY if mentioned in the evidence.
5. Every treatment claim MUST reference a PMID.
6. Disease summary should follow WHO-style medical description.
7. If evidence does not mention drugs, return an empty list.
8. Output ONLY valid JSON.
9. Do NOT add any text before or after JSON.
10. Do NOT include markdown or explanations.

JSON FORMAT:

{
  "disease": "detected disease",
  "disease_summary": "MANDATORY: short WHO-style description including cause, pathogen, and key symptoms",
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

Return ONLY valid JSON.
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
        print("\n===== RAW LLM OUTPUT =====")
        print(raw_output)
        print("===== END RAW OUTPUT =====\n")

    except Exception as e:
        return {
            "disease": "",
            "disease_summary": "",
            "treatment_summary": "",
            "drugs": [],
            "citations": [],
            "error": "Groq API call failed",
            "details": str(e)
        }

    json_block = extract_json(raw_output)

    print("\n===== EXTRACTED JSON BLOCK =====")
    print(json_block)
    print("===== END JSON BLOCK =====\n")

    if not json_block:
        return {
            "disease": "",
            "disease_summary": "",
            "treatment_summary": "",
            "drugs": [],
            "citations": [],
            "error": "No JSON found in LLM response",
            "raw_output": raw_output
        }

    try:
        parsed = json.loads(json_block)

    except json.JSONDecodeError as e:
        return {
            "disease": "",
            "disease_summary": "",
            "treatment_summary": "",
            "drugs": [],
            "citations": [],
            "error": "Invalid JSON returned by LLM",
            "details": str(e),
            "raw_output": raw_output
        }

    parsed.setdefault("disease", "")
    parsed.setdefault("disease_summary", "")
    parsed.setdefault("treatment_summary", "")
    parsed.setdefault("recommended_drugs", [])
    parsed.setdefault("citations", [])

    parsed["drugs"] = [
        {
            "name": d,
            "rxnorm": None,
            "dosage": None
        }
        for d in parsed.get("recommended_drugs", [])
    ]

    if not parsed["disease_summary"] and parsed["disease"]:
        parsed["disease_summary"] = (
            f"{parsed['disease']} is a medical condition described in clinical literature. "
            f"Refer to cited studies for detailed epidemiology, pathogenesis, and treatment guidance."
        )

    return {
        "disease": parsed["disease"],
        "disease_summary": parsed["disease_summary"],
        "treatment_summary": parsed["treatment_summary"],
        "drugs": parsed["drugs"],
        "recommended_drugs": parsed.get("recommended_drugs", []),
        "citations": parsed["citations"]
    }