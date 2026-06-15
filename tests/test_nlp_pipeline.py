from ml.inference.nlp_service import (
    analyze_contract_clause
)


def test_nlp_pipeline():

    text = (
        "This Agreement terminates upon breach."
    )

    result = analyze_contract_clause(
        text
    )

    required_keys = [

        "clause",

        "confidence",

        "risk_score",

        "risk_level"
    ]

    for key in required_keys:

        assert key in result

    print(
        "NLP Pipeline Test Passed"
    )


if __name__ == "__main__":

    test_nlp_pipeline()