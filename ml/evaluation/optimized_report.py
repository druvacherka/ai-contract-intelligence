from ml.inference.batch_analysis import (
    analyze_multiple_contracts
)


def generate_optimized_report():

    results = (
        analyze_multiple_contracts()
    )

    print("\nOPTIMIZED NLP REPORT\n")

    for idx, result in enumerate(results):

        print(
            f"\nContract {idx + 1}\n"
        )

        print(
            "Text:"
        )

        print(
            result["text"]
        )

        print(
            "\nAnalysis:"
        )

        analysis = result["analysis"]

        print(
            "Clause:",
            analysis["clause"]
        )

        print(
            "Confidence:",
            analysis["confidence"]
        )

        print(
            "Risk Level:",
            analysis["risk_level"]
        )


if __name__ == "__main__":

    generate_optimized_report()