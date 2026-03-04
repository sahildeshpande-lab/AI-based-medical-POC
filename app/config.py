import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"
DAILYMED_BASE = "https://dailymed.nlm.nih.gov/dailymed/services/v2"