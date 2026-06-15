CLAUSE_RISK_WEIGHTS = {

    "Termination": 0.8,

    "Liability": 0.9,

    "Confidentiality": 0.4,

    "Payment Terms": 0.5,

    "Governing Law": 0.3
}


def calculate_risk_score(predicted_clauses):

    total_score = 0

    for clause in predicted_clauses:

        total_score += CLAUSE_RISK_WEIGHTS.get(
            clause,
            0
        )

    average_risk = (
        total_score / len(predicted_clauses)
    )

    risk_percentage = round(
        average_risk * 100
    )

    if risk_percentage >= 75:

        risk_level = "High"

    elif risk_percentage >= 45:

        risk_level = "Medium"

    else:

        risk_level = "Low"

    return {

        "risk_score": risk_percentage,

        "risk_level": risk_level
    }


if __name__ == "__main__":

    clauses = [

        "Termination",

        "Liability",

        "Confidentiality"
    ]

    result = calculate_risk_score(
        clauses
    )

    print(result)