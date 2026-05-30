from ml.inference.nlp_service import (
    analyze_contract_clause
)

contracts = [

    "This Agreement terminates upon breach.",

    "Confidential information must remain private.",

    "Payment shall be completed in 30 days."
]


def analyze_multiple_contracts():

    results = []

    for contract in contracts:

        analysis = analyze_contract_clause(
            contract
        )

        results.append({
            "text": contract,
            "analysis": analysis
        })

    return results


if __name__ == "__main__":

    analyses = (
        analyze_multiple_contracts()
    )

    print("\nBatch Contract Analysis\n")

    for result in analyses:

        print(
            result["text"]
        )

        print(
            result["analysis"]
        )

        print()