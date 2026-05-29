CLAUSE_SEVERITY = {

    "Termination": "High",

    "Liability": "Critical",

    "Confidentiality": "Medium",

    "Payment Terms": "Medium",

    "Governing Law": "Low"
}


def get_clause_severity(clause):

    return CLAUSE_SEVERITY.get(
        clause,
        "Unknown"
    )


if __name__ == "__main__":

    clauses = [

        "Termination",

        "Liability",

        "Confidentiality"
    ]

    print("\nClause Severity Analysis:\n")

    for clause in clauses:

        severity = get_clause_severity(
            clause
        )

        print(
            f"{clause}: {severity}"
        )