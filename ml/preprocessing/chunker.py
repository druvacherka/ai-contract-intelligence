from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "nlpaueb/legal-bert-base-uncased"
)


def chunk_contract(
    text,
    max_tokens=512,
    overlap=100
):

    tokens = tokenizer.tokenize(text)

    chunks = []

    start = 0

    while start < len(tokens):

        end = start + max_tokens

        chunk_tokens = tokens[start:end]

        chunk_text = tokenizer.convert_tokens_to_string(
            chunk_tokens
        )

        chunks.append(chunk_text)

        start += max_tokens - overlap

    return chunks


if __name__ == "__main__":

    sample_text = (
        "This Agreement is entered into by Microsoft Corporation. "
    ) * 300

    chunks = chunk_contract(sample_text)

    print("Total Chunks:", len(chunks))

    print("\nFirst Chunk:\n")

    print(chunks[0][:1000])