import pickle

LOAD_PATH = (
    "ml/embeddings/contract_embeddings.pkl"
)


def load_embeddings():

    with open(LOAD_PATH, "rb") as file:

        embeddings = pickle.load(file)

    return embeddings


if __name__ == "__main__":

    embeddings = load_embeddings()

    print(
        "\nLoaded Embeddings:\n"
    )

    for item in embeddings:

        print(item["text"])