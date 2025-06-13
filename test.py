import pandas as pd

file = pd.read_json("corrected_JSON_novel_1.json")
print(file)


file_2 = file["emotions"]
result = pd.DataFrame(file_2)
print([result.iloc[0]])
