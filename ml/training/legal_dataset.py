from transformers import AutoTokenizer

from ml.preprocessing.clause_labels import (
    get_label_id
)

tokenizer = AutoTokenizer.from_pretrained(
    "nlpaueb/legal-bert-base-uncased"
)


class LegalClauseDataset:

    def __init__(self):

        self.samples = [

            {
                "text": (
                    "This Agreement terminates upon breach."
                ),
                "label": "Termination"
            },

            {
                "text": (
                    "All confidential information must remain private."
                ),
                "label": "Confidentiality"
            }
        ]

    def __len__(self):

        return len(self.samples)

    def __getitem__(self, idx):

        sample = self.samples[idx]

        encoded = tokenizer(
            sample["text"],
            truncation=True,
            padding="max_length",
            max_length=128
        )

        return {

            "input_ids": encoded["input_ids"],

            "attention_mask":
                encoded["attention_mask"],

            "label":
                get_label_id(sample["label"])
        }


if __name__ == "__main__":

    dataset = LegalClauseDataset()

    sample = dataset[0]

    print(sample.keys())

    print("Label:", sample["label"])