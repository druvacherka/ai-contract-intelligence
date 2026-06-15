def refine_prediction(text, predicted_clause):

    text = text.lower()

    if "terminate" in text:

        return "Termination"

    if "confidential" in text:

        return "Confidentiality"

    if "payment" in text:

        return "Payment Terms"

    return predicted_clause


if __name__ == "__main__":

    sample_text = (
        "This agreement will terminate immediately."
    )

    raw_prediction = "Liability"

    refined = refine_prediction(
        sample_text,
        raw_prediction
    )

    print("Raw Prediction:")

    print(raw_prediction)

    print("\nRefined Prediction:")

    print(refined)