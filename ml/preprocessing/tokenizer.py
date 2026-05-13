from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "nlpaueb/legal-bert-base-uncased"
)


def tokenize_contract(text):

    tokens = tokenizer(
        text,
        truncation=True,
        padding="max_length",
        max_length=512,
        return_tensors="pt"
    )

    return tokens


if __name__ == "__main__":

    sample_text = (
        "This Agreement is entered into by Microsoft Corporation."
    )

    output = tokenize_contract(sample_text)

    print(output.keys())