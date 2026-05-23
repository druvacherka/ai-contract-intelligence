import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

from torch.optim import AdamW

from ml.training.legal_dataset import (
    LegalClauseDataset
)

tokenizer = AutoTokenizer.from_pretrained(
    "nlpaueb/legal-bert-base-uncased"
)

model = AutoModelForSequenceClassification.from_pretrained(
    "nlpaueb/legal-bert-base-uncased",
    num_labels=5
)

dataset = LegalClauseDataset()

optimizer = AdamW(
    model.parameters(),
    lr=2e-5
)

model.train()

for epoch in range(2):

    print(f"\nEpoch {epoch + 1}\n")

    for sample in dataset:

        input_ids = torch.tensor(
            [sample["input_ids"]]
        )

        attention_mask = torch.tensor(
            [sample["attention_mask"]]
        )

        labels = torch.tensor(
            [sample["label"]]
        )

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )

        loss = outputs.loss

        print("Loss:", loss.item())

        loss.backward()

        optimizer.step()

        optimizer.zero_grad()