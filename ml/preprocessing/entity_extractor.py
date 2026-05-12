import spacy

nlp = spacy.load("en_core_web_sm")


def extract_entities(text):
    doc = nlp(text)

    entities = []

    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_
        })

    return entities


if __name__ == "__main__":

    sample_text = (
        "Google signed a contract on March 10, 2024 "
        "for $200000."
    )

    extracted = extract_entities(sample_text)

    print(extracted)