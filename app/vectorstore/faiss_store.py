import numpy as np

class FAISSStore:
    """A lightweight in‑memory vector store.

    The original implementation relied on the faiss package, which pulls
    in a large native binary that easily pushes the memory usage of the
    process over Render's 512 MiB limit.  For the small number of
    embeddings we generate during a request it is much simpler (and
    lighter) to just keep vectors in a numpy array and perform a brute
    force search.  This avoids the faiss dependency entirely.
    """

    def __init__(self, dimension: int):
        self.dimension = dimension
        self.documents: list[str] = []
        self.embeddings = np.zeros((0, dimension), dtype="float32")

    def add(self, texts, embeddings):
        if not embeddings:
            raise ValueError("No embeddings to add to vector store")

        arr = np.vstack(embeddings).astype("float32")
        self.embeddings = np.vstack([self.embeddings, arr])
        self.documents.extend(texts)

    def search(self, query_embedding, k=10):
        if len(self.documents) == 0:
            return []

        q = np.array(query_embedding).astype("float32")
        # Euclidean distance – the original faiss.IndexFlatL2 behaviour
        dists = np.linalg.norm(self.embeddings - q, axis=1)
        idxs = np.argsort(dists)[:k]
        results = []
        for i in idxs:
            results.append({"text": self.documents[i], "index": int(i)})
        return results