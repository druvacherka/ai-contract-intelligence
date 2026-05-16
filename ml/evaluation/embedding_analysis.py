from ml.embeddings.generate_embeddings import (
    generate_embedding
)


def inspect_embedding(text):

    embedding = generate_embedding(text)

    print("Embedding Shape:")
    print(embedding.shape)

    print("\nFirst 10 Values:\n")

    print(embedding[0][:10])


if __name__ == "__main__":

    sample_text = (
        "Confidentiality obligations survive termination."
    )

    inspect_embedding(sample_text)