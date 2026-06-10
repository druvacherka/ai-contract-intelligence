import faiss
import numpy as np


def create_index(embeddings):

    dimension = len(
        embeddings[0]
    )

    index = faiss.IndexFlatL2(
        dimension
    )

    vectors = np.array(
        embeddings
    ).astype("float32")

    index.add(vectors)

    return index


def search_index(
    index,
    query_embedding,
    top_k=3
):

    distances, indices = (
        index.search(
            np.array(
                [query_embedding]
            ).astype("float32"),
            top_k
        )
    )

    return indices[0], distances[0]