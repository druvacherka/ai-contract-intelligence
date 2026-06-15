from datasets import load_dataset
from transformers import AutoTokenizer

from ml.preprocessing.text_cleaner import (
    clean_contract_text
)

from ml.preprocessing.chunker import (
    chunk_contract
)

tokenizer = AutoTokenizer.from_pretrained(
    "nlpaueb/legal-bert-base-uncased"
)


def prepare_training_samples():

    dataset = load_dataset(
        "theatticusproject/cuad",
        streaming=True
    )

    train_data = dataset["train"]

    processed_samples = []

    for sample in train_data:

        pdf = sample["pdf"]

        first_page = pdf.pages[0]

        text = first_page.extract_text()

        cleaned_text = clean_contract_text(text)

        chunks = chunk_contract(cleaned_text)

        for chunk in chunks[:2]:

            encoded = tokenizer(
                chunk,
                truncation=True,
                padding="max_length",
                max_length=512
            )

            processed_samples.append({
                "input_ids": encoded["input_ids"],
                "attention_mask": encoded["attention_mask"]
            })

        if len(processed_samples) >= 5:
            break

    return processed_samples


if __name__ == "__main__":

    samples = prepare_training_samples()

    print("Prepared Samples:", len(samples))

    print(samples[0].keys())