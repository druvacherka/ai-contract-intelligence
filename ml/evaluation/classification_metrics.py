from sklearn.metrics import (
    accuracy_score,
    f1_score
)

true_labels = [
    0,
    2,
    1,
    0
]

predicted_labels = [
    0,
    2,
    1,
    1
]


def evaluate_model():

    accuracy = accuracy_score(
        true_labels,
        predicted_labels
    )

    f1 = f1_score(
        true_labels,
        predicted_labels,
        average="weighted"
    )

    print("Accuracy:", round(accuracy, 2))

    print("F1 Score:", round(f1, 2))


if __name__ == "__main__":

    evaluate_model()