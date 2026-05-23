training_losses = [
    1.72,
    1.51,
    1.30,
    1.12
]


def print_training_summary(losses):

    print("\nTraining Summary\n")

    print("Initial Loss:", losses[0])

    print("Final Loss:", losses[-1])

    improvement = losses[0] - losses[-1]

    print("Improvement:", round(improvement, 3))


if __name__ == "__main__":

    print_training_summary(
        training_losses
    )