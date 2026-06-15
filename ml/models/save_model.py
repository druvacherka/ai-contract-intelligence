from transformers import (
    AutoModelForSequenceClassification
)

model = AutoModelForSequenceClassification.from_pretrained(
    "nlpaueb/legal-bert-base-uncased",
    num_labels=5
)

SAVE_PATH = "ml/models/legalbert_classifier"


def save_model():

    model.save_pretrained(
        SAVE_PATH
    )

    print(
        f"Model saved to: {SAVE_PATH}"
    )


if __name__ == "__main__":

    save_model()