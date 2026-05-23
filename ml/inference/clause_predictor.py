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


def predict_clause(text):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():

        outputs = model(**inputs)

    logits = outputs.logits

    predicted_id = torch.argmax(
        logits,
        dim=1
    ).item()

    predicted_clause = LABEL_MAP[predicted_id]

    return predicted_clause


if __name__ == "__main__":

    sample_clause = (
        "This Agreement terminates "
        "upon breach of contract."
    )

    prediction = predict_clause(
        sample_clause
    )

    print("Predicted Clause:")

    print(prediction)