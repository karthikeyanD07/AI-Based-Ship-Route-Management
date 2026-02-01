import pandas as pd

ais_file = "ais_data.csv"
ais_data = pd.read_csv(ais_file)

print(ais_data.columns)  # Display column names
