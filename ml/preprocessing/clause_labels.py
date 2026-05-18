CLAUSE_LABELS = {
    "Termination": 0,
    "Liability": 1,
    "Confidentiality": 2,
    "Payment Terms": 3,
    "Governing Law": 4
}


def get_label_id(clause_name):

    return CLAUSE_LABELS.get(clause_name, -1)


if __name__ == "__main__":

    clause = "Termination"

    label_id = get_label_id(clause)

    print("Clause:", clause)

    print("Label ID:", label_id)