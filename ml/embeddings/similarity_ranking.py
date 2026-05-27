from ml.embeddings.semantic_similarity import (
    compute_similarity
)

clauses = [

    "This Agreement terminates upon breach.",

    "Confidential information must remain private.",

    "Payment must be completed within 30 days.",

    "The contract ends if obligations are violated."
]


def rank_clauses(query):

    rankings = []

    for clause in clauses:

        similarity = compute_similarity(
            query,
            clause
        )

        rankings.append({
            "clause": clause,
            "score": similarity
        })

    rankings.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return rankings


if __name__ == "__main__":

    query = (
        "Agreement ends after breach."
    )

    ranked = rank_clauses(query)

    print("\nClause Rankings:\n")

    for item in ranked:

        print(
            item["clause"]
        )

        print(
            "Score:",
            round(item["score"], 3)
        )

        print()