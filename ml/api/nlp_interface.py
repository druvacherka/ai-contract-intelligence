from ml.inference.nlp_service import (
    analyze_contract_clause
)

from ml.preprocessing.entity_extractor import (
    extract_entities
)


def analyze_contract(text):

    analysis = (
        analyze_contract_clause(text)
    )

    entities = (
        extract_entities(text)
    )

    analysis["entities"] = (
        entities
    )

    return analysis


if __name__ == "__main__":

    sample_contract = (
        "Google signed a contract "
        "on March 10, 2024 "
        "for $200000."
    )

    result = analyze_contract(
        sample_contract
    )

    print(result)