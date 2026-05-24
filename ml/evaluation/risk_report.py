from ml.inference.risk_scoring import (
    calculate_risk_score
)


def generate_report():

    clauses = [

        "Termination",

        "Liability",

        "Confidentiality"
    ]

    risk_result = calculate_risk_score(
        clauses
    )

    print("\nContract Risk Analysis\n")

    print(
        "Detected Clauses:"
    )

    for clause in clauses:

        print("-", clause)

    print(
        "\nRisk Score:",
        risk_result["risk_score"]
    )

    print(
        "Risk Level:",
        risk_result["risk_level"]
    )


if __name__ == "__main__":

    generate_report()