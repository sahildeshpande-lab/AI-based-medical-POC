from lxml import etree


def parse_abstracts(xml_data):

    if not xml_data.strip():
        raise ValueError("No XML data received from PubMed")

    root = etree.fromstring(xml_data.encode())

    abstracts = []

    for article in root.findall(".//PubmedArticle"):

        pmid = article.findtext(".//PMID")

        abstract_parts = article.findall(".//AbstractText")

        text = " ".join(
            ["".join(a.itertext()).strip() for a in abstract_parts]
        )

        if text:
            abstracts.append({
                "pmid": pmid,
                "section": "abstract",
                "text": text
            })

    return abstracts


def parse_pmc_fulltext(xml_data, pmid):
    """
    Extract meaningful sections from PMC XML
    """

    root = etree.fromstring(xml_data.encode())

    sections = []

    for sec in root.findall(".//sec"):

        title = sec.findtext("title")

        paragraphs = sec.findall(".//p")

        for p in paragraphs:

            text = "".join(p.itertext()).strip()

            if len(text) > 100:

                sections.append({
                    "pmid": pmid,
                    "section": title if title else "body",
                    "text": text
                })

    return sections

