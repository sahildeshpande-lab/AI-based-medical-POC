def validate_citations(llm_output, evidence_pack):

    valid_pmids = {e["pmid"] for e in evidence_pack}

    cited = set(llm_output.get("citations", []))

    if not cited:
        return False

    return cited.issubset(valid_pmids)