from lxml import etree

def parse_abstracts(xml_data):
    root = etree.fromstring(xml_data.encode())

    abstracts = []

    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        abstract = article.findtext(".//AbstractText")

        if abstract:
            abstracts.append({
                "pmid": pmid,
                "text": abstract
            })

    return abstracts