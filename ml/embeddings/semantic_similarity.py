import torch
import torch.nn.functional as F

from ml.embeddings.generate_embeddings import (
    generate_embedding
)


def compute_similarity(text1, text2):

    embedding1 = generate_embedding(text1)

    embedding2 = generate_embedding(text2)

    similarity = F.cosine_similarity(
        embedding1,
        embedding2
    )

    return similarity.item()


if __name__ == "__main__":

    clause1 = (
        "This Agreement terminates upon breach."
    )

    clause2 = (
        "The contract shall end if either party breaches terms."
    )

    score = compute_similarity(
        clause1,
        clause2
    )

    print("Similarity Score:")

    print(score)