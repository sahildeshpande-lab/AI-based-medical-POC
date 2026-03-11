import os

os.environ['TOKENIZERS_PARALLELISM'] = 'false'
cache_dir = os.getenv('TRANSFORMERS_CACHE', '/tmp/transformers_cache')

_model = None

def _load_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=cache_dir, device='cpu')
    return _model


def embed_text(text):
    """Return an embedding for the given text.

    The model is only instantiated on the first call instead of during
    module import, which keeps the memory footprint lower during
    service startup (important when running on a small Render instance).
    """
    model = _load_model()
    return model.encode(text)