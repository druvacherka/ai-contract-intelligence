from datasets import load_dataset
from ml.preprocessing.text_cleaner import clean_contract_text


def load_contracts():

    dataset = load_dataset(
        "theatticusproject/cuad",
        streaming=True
    )

    train_data = dataset["train"]

    contracts = []

    for sample in train_data:

        pdf = sample["pdf"]

        first_page = pdf.pages[0]

        text = first_page.extract_text()

        cleaned_text = clean_contract_text(text)

        contracts.append(cleaned_text)

        if len(contracts) == 3:
            break

    return contracts


if __name__ == "__main__":

    contracts = load_contracts()

    print(contracts[0][:1000])