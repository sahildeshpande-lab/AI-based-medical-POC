import faiss
import numpy as np

class FAISSStore:

    def __init__(self, dimension):
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []

    def add(self, texts, embeddings):

        if len(embeddings) == 0:
            raise ValueError("No embeddings to add to FAISS index")

        vectors = np.vstack(embeddings).astype("float32")

        self.index.add(vectors)

        self.documents.extend(texts)


    def search(self, query_embedding, k=10):

        D, I = self.index.search(
            np.array([query_embedding]).astype("float32"),
            k
        )

        results = []

        for idx in I[0]:

            if idx < len(self.documents):
                results.append({
                    "text": self.documents[idx],
                    "index": int(idx)
                })

        return results