import pandas as pd

nested = {"column1": {"row1": 1, "row2": 2}, "column2": {"row1": 3, "row2": 4}}
df = pd.DataFrame(nested)
df2 = pd.DataFrame([[1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]])
df2[:1] = 5
print(df[:"row1"])
print(df2)
