import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

tokenizer = AutoTokenizer.from_pretrained(
    "nlpaueb/legal-bert-base-uncased"
)

model = AutoModelForSequenceClassification.from_pretrained(
    "nlpaueb/legal-bert-base-uncased",
    num_labels=5
)


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

    predicted_label = torch.argmax(
        logits,
        dim=1
    )

    return predicted_label.item()


if __name__ == "__main__":

    sample_clause = (
        "This Agreement terminates immediately "
        "upon material breach."
    )

    prediction = predict_clause(sample_clause)

    print("Predicted Label ID:")

    print(prediction)