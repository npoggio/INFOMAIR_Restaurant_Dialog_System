from transformers import DistilBertTokenizer, DistilBertModel

tokenizer = DistilBertTokenizer.from_pretrained(
    "distilbert-base-uncased"
)

model = DistilBertModel.from_pretrained(
    "distilbert-base-uncased"
)

text = "I am looking for a cheap Italian restaurant."

encoded_input = tokenizer(
    text,
    return_tensors="pt",
    padding=True,
    truncation=True,
    max_length=128
)

output = model(**encoded_input)

print(output.last_hidden_state.shape)