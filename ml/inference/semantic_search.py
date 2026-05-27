from ml.embeddings.topk_retrieval import (
    retrieve_top_k
)


def semantic_search(query):

    results = retrieve_top_k(
        query,
        k=3
    )

    print("\nSemantic Search Results:\n")

    for idx, result in enumerate(results):

        print(
            f"{idx + 1}.",
            result["clause"]
        )

        print(
            "Similarity:",
            round(result["score"], 3)
        )

        print()


if __name__ == "__main__":

    search_query = (
        "Contract ends after breach."
    )

    semantic_search(search_query)