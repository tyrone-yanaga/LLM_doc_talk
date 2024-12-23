import numpy as np
from typing import Any, List, Tuple, Union


def cosine_similarity(
    store_embeddings: np.ndarray, query_embedding: np.ndarray, top_k: int
) -> np.ndarray:
    """
    Compute the cosine similarity between a query embedding and a set of stored embeddings,
    and return the top_k indices of the most similar embeddings.

    Parameters
    ----------
    store_embeddings : np.ndarray
        A 2D numpy array where each row is an embedding for a stored document.
    query_embedding : np.ndarray
        A 1D numpy array representing the query embedding.
    top_k : int
        The number of top similar results to return.

    Returns
    -------
    np.ndarray
        An array of indices indicating the top_k most similar embeddings.
    """
    # Compute the dot product between query and all stored embeddings
    dot_product = np.dot(store_embeddings, query_embedding)

    # Compute the magnitude (L2 norm) of each stored embedding and the query embedding
    magnitude_a = np.linalg.norm(store_embeddings, axis=1)
    magnitude_b = np.linalg.norm(query_embedding)

    # Compute cosine similarity for each embedding
    similarity = dot_product / (magnitude_a * magnitude_b)

    # Sort by similarity (ascending), then reverse to get descending order
    sim = np.argsort(similarity)
    top_k_indices = sim[::-1][:top_k]

    return top_k_indices


class VectorDB:
    """
    A simple vector database that allows inserting documents (with embeddings and metadata)
    and performing similarity search using cosine similarity.

    Usage:
    ------
    1. Create an instance of VectorDB:

       db = VectorDB()

    2. Add documents with embeddings:

       embedding_1 = [0.1, 0.2, 0.3]  # This can be a list or a np.ndarray
       db.add(doc_id="doc1", embedding=embedding_1, meta={"title": "Document 1"})

       embedding_2 = [0.3, 0.1, 0.9]
       db.add(doc_id="doc2", embedding=embedding_2, meta={"title": "Document 2"})

    3. Perform a similarity search:

       query = [0.1, 0.2, 0.3]
       results = db.search(query, k=2)
       # results is a list of tuples (doc_id, embedding, metadata, similarity_score)

    Notes:
    ------
    - All embeddings added to the database must have the same dimensionality.
    - If you try to add an embedding with a different dimension, a ValueError is raised.
    - The query embedding must have the same dimension as the stored embeddings.
    """

    def __init__(self) -> None:
        # Lists to store document information
        self.ids: List[Union[str, int]] = []
        self.embeddings: List[np.ndarray] = []
        self.metadata: List[Any] = []

        # Dimension of embeddings once the first embedding is added
        self._dimension: int = -1

    def add(
        self,
        doc_id: Union[str, int],
        embedding: Union[List[float], np.ndarray],
        meta: Any,
    ) -> None:
        """
        Add a document (with embedding and metadata) to the vector database.

        Parameters
        ----------
        doc_id : Union[str, int]
            A unique identifier for the document.
        embedding : Union[List[float], np.ndarray]
            The embedding vector for the document. Can be a list of floats or a numpy array.
        meta : Any
            Any additional metadata associated with the document (e.g., title, text content).

        Raises
        ------
        ValueError
            If the embedding dimension does not match previously stored embeddings.
        """
        # Convert embedding to np.ndarray if it's a list
        if not isinstance(embedding, np.ndarray):
            embedding = np.array(embedding, dtype=np.float32)

        # Check or set the embedding dimension
        if self._dimension == -1:
            self._dimension = embedding.shape[0]
        else:
            if embedding.shape[0] != self._dimension:
                raise ValueError("All embeddings must have the same dimension.")

        # Store the document data
        self.ids.append(doc_id)
        self.embeddings.append(embedding)
        self.metadata.append(meta)

    def search(
        self, query_embedding: Union[List[float], np.ndarray], k: int = 5
    ) -> List[Tuple[Union[str, int], np.ndarray, Any, float]]:
        """
        Search for the top k most similar documents to the given query embedding.

        Parameters
        ----------
        query_embedding : Union[List[float], np.ndarray]
            The query embedding vector for which to find similar documents.
        k : int, optional
            The number of top similar documents to return, by default 5.

        Returns
        -------
        List[Tuple[Union[str, int], np.ndarray, Any, float]]
            A list of tuples containing:
            (doc_id, embedding, metadata, similarity_score)

        Raises
        ------
        ValueError
            If the query embedding dimension does not match the stored embeddings.
        """
        # Convert query_embedding to np.ndarray if it's a list
        if not isinstance(query_embedding, np.ndarray):
            query_embedding = np.array(query_embedding, dtype=np.float32)

        # Check that the query dimension matches
        if self._dimension != -1 and query_embedding.shape[0] != self._dimension:
            raise ValueError(
                "Query embedding dimension does not match the stored embeddings."
            )

        # Convert stored embeddings to a 2D numpy array
        emb_array = np.array(self.embeddings)

        # Compute top_k similar embeddings
        top_indices = cosine_similarity(emb_array, query_embedding, k)

        # Build the results list
        results = [
            (
                self.ids[i],
                self.embeddings[i],
                self.metadata[i],
                float(
                    np.dot(emb_array[i], query_embedding)
                    / (np.linalg.norm(emb_array[i]) * np.linalg.norm(query_embedding))
                ),
            )
            for i in top_indices
        ]

        return results
