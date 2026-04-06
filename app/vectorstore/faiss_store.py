import numpy as np
import hnswlib

class FAISSStore:


    def __init__(self, dimension: int, max_elements: int = 5000, ef_construction: int = 200):
        self.dimension = dimension
        self.documents: list[str] = []
        self.embeddings = np.zeros((0, dimension), dtype="float32")
        self.index = None
        self.max_elements = max_elements
        self.ef_construction = ef_construction
        self._index_built = False

    def add(self, texts, embeddings):
        if not embeddings:
            raise ValueError("No embeddings to add to vector store")

        arr = np.vstack(embeddings).astype("float32")
        self.embeddings = np.vstack([self.embeddings, arr])
        self.documents.extend(texts)
        self._index_built = False

    def _build_index(self):
        """Build or rebuild the HNSW index from stored embeddings."""
        if len(self.documents) == 0:
            self.index = None
            self._index_built = False
            return

        self.index = hnswlib.Index(space='l2', dim=self.dimension)
        num_elements = len(self.documents)
        self.index.init_index(
            max_elements=max(num_elements + 100, self.max_elements),
            ef_construction=self.ef_construction,
            M=16
        )
        self.index.add_items(self.embeddings, np.arange(num_elements))
        self.index.set_ef(200)  
        self._index_built = True

    def search(self, query_embedding, k=10):
        if len(self.documents) == 0:
            return []

        if not self._index_built:
            self._build_index()

        if self.index is None:
            return []

        q = np.array([query_embedding]).astype("float32")
        labels, distances = self.index.knn_query(q, k=min(k, len(self.documents)))
        
        results = []
        for idx in labels[0]:
            if 0 <= idx < len(self.documents):
                results.append({"text": self.documents[idx], "index": int(idx)})
        return results