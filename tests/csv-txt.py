import os
import pandas

csvFolder = os.path.join(os.getcwd(), os.pardir, "data", "Chatbot Training Data")
csvFile = os.path.join(csvFolder, "rdany.csv")
trainingFile = os.path.join(csvFolder, "train.txt")

data = pandas.read_csv(csvFile)
statements = []

def yoda():
    texts = data['text']
    character = data['character']

    for x, y in zip(texts, character):
        if isinstance(y, str):
            if y.lower() != "narrator":
                statements.append(x)

def rdany():
    texts = [text for text in data['text'] if text.strip() != "[START]"]
    for x in texts:
        statements.append(x)

rdany()

with open(trainingFile, "a", encoding="utf-8") as f:
    for statement in statements:
        end = "\n"
        if statement.endswith(end):
            end = ""
        f.write(statement + end)
