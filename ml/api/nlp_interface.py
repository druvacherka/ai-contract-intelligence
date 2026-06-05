from ml.inference.nlp_service import (
    analyze_contract_clause
)


def analyze_contract(text):

    return analyze_contract_clause(text)


if __name__ == "__main__":

    sample_contract = (
        "This Agreement terminates upon breach."
    )

    result = analyze_contract(
        sample_contract
    )

    print(result)
