import torch

from transformers import (
    AutoTokenizer,
    AutoModel
)

tokenizer = AutoTokenizer.from_pretrained(
    "nlpaueb/legal-bert-base-uncased"
)

model = AutoModel.from_pretrained(
    "nlpaueb/legal-bert-base-uncased"
)


def generate_embeddings(text):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )

    with torch.no_grad():

        outputs = model(**inputs)

    embeddings = outputs.last_hidden_state

    return embeddings


if __name__ == "__main__":

    sample_text = (
        "This Agreement shall terminate "
        "upon breach of contract."
    )

    embeddings = generate_embeddings(sample_text)

    print("Embedding Shape:")

    print(embeddings.shape)