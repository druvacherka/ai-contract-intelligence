from ml.inference.clause_severity import (
    get_clause_severity
)

SEVERITY_SCORES = {

    "Low": 1,

    "Medium": 2,

    "High": 3,

    "Critical": 4
}


def aggregate_contract_risk(clauses):

    total_score = 0

    for clause in clauses:

        severity = get_clause_severity(
            clause
        )

        total_score += SEVERITY_SCORES.get(
            severity,
            0
        )

    average = total_score / len(clauses)

    if average >= 3.5:

        overall_risk = "Critical"

    elif average >= 2.5:

        overall_risk = "High"

    elif average >= 1.5:

        overall_risk = "Medium"

    else:

        overall_risk = "Low"

    return {

        "average_score": round(
            average,
            2
        ),

        "overall_risk": overall_risk
    }


if __name__ == "__main__":

    clauses = [

        "Termination",

        "Liability",

        "Payment Terms"
    ]

    result = aggregate_contract_risk(
        clauses
    )

    print("\nContract Risk Summary:\n")

    print(result)