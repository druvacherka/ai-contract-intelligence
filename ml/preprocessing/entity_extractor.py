import spacy

nlp = spacy.load(
    "en_core_web_sm"
)


LEGAL_PARTIES = {
    "lessee",
    "lessor",
    "tenant",
    "landlord",
    "buyer",
    "seller",
    "party",
    "parties"
}


def extract_entities(text):

    doc = nlp(text)

    entities = []

    for ent in doc.ents:

        label = ent.label_

        if ent.text.lower() in LEGAL_PARTIES:

            label = "PARTY"

        if ent.text.lower() == "agreement":

            label = "CONTRACT"

        entities.append({
            "text": ent.text,
            "label": label
        })

    return entities


if __name__ == "__main__":

    sample_text = (
        "The Lessee signed the Agreement "
        "on March 10, 2024."
    )

    print(
        extract_entities(
            sample_text
        )
    )