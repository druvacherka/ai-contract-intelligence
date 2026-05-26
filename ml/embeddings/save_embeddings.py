import pickle

from ml.embeddings.batch_embeddings import (
    generate_contract_embeddings
)

SAVE_PATH = (
    "ml/embeddings/contract_embeddings.pkl"
)


def save_embeddings():

    embeddings = (
        generate_contract_embeddings()
    )

    with open(SAVE_PATH, "wb") as file:

        pickle.dump(
            embeddings,
            file
        )

    print(
        f"Embeddings saved to: {SAVE_PATH}"
    )


if __name__ == "__main__":

    save_embeddings()