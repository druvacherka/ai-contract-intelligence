import torch
import torch.nn.functional as F

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


def predict_with_confidence(text):

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

    probabilities = F.softmax(
        logits,
        dim=1
    )

    confidence, predicted_id = torch.max(
        probabilities,
        dim=1
    )

    clause = LABEL_MAP[
        predicted_id.item()
    ]

    return clause, confidence.item()


if __name__ == "__main__":

    sample_text = (
        "All confidential information "
        "must remain private."
    )

    clause, confidence = predict_with_confidence(
        sample_text
    )

    print("Clause:", clause)

    print(
        "Confidence:",
        round(confidence * 100, 2),
        "%"
    )