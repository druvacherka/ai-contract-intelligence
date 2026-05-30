from ml.inference.clause_predictor import (
    predict_clause
)

from ml.inference.confidence_scoring import (
    predict_with_confidence
)

from ml.inference.risk_scoring import (
    calculate_risk_score
)


def analyze_contract_clause(text):

    clause = predict_clause(text)

    prediction, confidence = (
        predict_with_confidence(text)
    )

    risk = calculate_risk_score(
        [clause]
    )

    return {

        "clause": clause,

        "confidence":
            round(confidence * 100, 2),

        "risk_score":
            risk["risk_score"],

        "risk_level":
            risk["risk_level"]
    }


if __name__ == "__main__":

    sample_text = (
        "This Agreement terminates "
        "upon breach."
    )

    result = analyze_contract_clause(
        sample_text
    )

    print("\nContract Analysis Result:\n")

    print(result)