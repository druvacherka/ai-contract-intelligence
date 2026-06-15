from ml.embeddings.semantic_similarity import (
    compute_similarity
)

clauses = [

    "This Agreement terminates upon breach.",

    "The contract shall end if either party violates terms.",

    "Payment must be completed within 30 days.",

    "Confidential information must remain private."
]


def retrieve_similar_clause(query):

    similarities = []

    for clause in clauses:

        score = compute_similarity(
            query,
            clause
        )

        similarities.append(
            (clause, score)
        )

    similarities.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return similarities[0]


if __name__ == "__main__":

    query = (
        "Agreement ends after violation."
    )

    result = retrieve_similar_clause(
        query
    )

    print("\nMost Similar Clause:\n")

    print(result)