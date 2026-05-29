from ml.inference.aggregate_risk import (
    aggregate_contract_risk
)


def generate_legal_insights():

    clauses = [

        "Termination",

        "Liability",

        "Confidentiality"
    ]

    risk = aggregate_contract_risk(
        clauses
    )

    print("\nAI Legal Insights\n")

    print(
        "Detected Clauses:"
    )

    for clause in clauses:

        print("-", clause)

    print(
        "\nOverall Contract Risk:"
    )

    print(
        risk["overall_risk"]
    )

    print(
        "\nAI Recommendation:"
    )

    if risk["overall_risk"] in [
        "High",
        "Critical"
    ]:

        print(
            "Manual legal review recommended."
        )

    else:

        print(
            "Contract risk appears manageable."
        )


if __name__ == "__main__":

    generate_legal_insights()