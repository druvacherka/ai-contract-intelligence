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


def generate_embedding(text):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )

    with torch.no_grad():

        outputs = model(**inputs)

    cls_embedding = outputs.last_hidden_state[:, 0, :]

    return cls_embedding


if __name__ == "__main__":

    sample_contract = (
        "This Agreement shall terminate "
        "upon material breach."
    )

    embedding = generate_embedding(sample_contract)

    print("Embedding Shape:")

    print(embedding.shape)