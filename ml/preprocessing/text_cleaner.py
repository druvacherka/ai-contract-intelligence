import re


def clean_contract_text(text):

    text = re.sub(r"\s+", " ", text)

    text = text.strip()

    return text


if __name__ == "__main__":

    sample = """
    THIS   AGREEMENT

    is signed    on 2025.
    """

    cleaned = clean_contract_text(sample)

    print(cleaned)