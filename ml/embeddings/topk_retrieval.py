from ml.embeddings.similarity_ranking import (
    rank_clauses
)


def retrieve_top_k(query, k=2):

    rankings = rank_clauses(query)

    return rankings[:k]


if __name__ == "__main__":

    query = (
        "Agreement terminates after violation."
    )

    results = retrieve_top_k(
        query,
        k=2
    )

    print("\nTop Retrieved Clauses:\n")

    for result in results:

        print(
            result["clause"]
        )

        print(
            "Similarity:",
            round(result["score"], 3)
        )

        print()