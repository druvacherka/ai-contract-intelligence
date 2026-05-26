from ml.embeddings.generate_embeddings import (
    generate_embedding
)

contracts = [

    "This Agreement terminates upon breach.",

    "Confidential information must remain private.",

    "Payment must be completed within 30 days."
]


def generate_contract_embeddings():

    embeddings = []

    for contract in contracts:

        embedding = generate_embedding(
            contract
        )

        embeddings.append({
            "text": contract,
            "embedding": embedding
        })

    return embeddings


if __name__ == "__main__":

    results = generate_contract_embeddings()

    print(
        "\nGenerated Embeddings:\n"
    )

    for result in results:

        print(
            result["text"]
        )

        print(
            result["embedding"].shape
        )

        print()