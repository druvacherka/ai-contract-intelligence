import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

LABEL_MAP = {
    0: "Termination",
    1: "Liability",
    2: "Confidentiality",
    3: "Payment Terms",
    4: "Governing Law"
}

tokenizer = AutoTokenizer.from_pretrained(
    "nlpaueb/legal-bert-base-uncased"
)

model = AutoModelForSequenceClassification.from_pretrained(
    "nlpaueb/legal-bert-base-uncased",
    num_labels=5
)

model.eval()


def batch_predict(texts):

    inputs = tokenizer(
        texts,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():

        outputs = model(**inputs)

    predictions = torch.argmax(
        outputs.logits,
        dim=1
    )

    results = []

    for prediction in predictions:

        results.append(
            LABEL_MAP[prediction.item()]
        )

    return results


if __name__ == "__main__":

    clauses = [

        "This Agreement terminates upon breach.",

        "Confidential information must remain private."
    ]

    predictions = batch_predict(
        clauses
    )

    print("\nPredictions:\n")

    for prediction in predictions:

        print("-", prediction)