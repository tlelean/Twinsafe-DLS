import pandas as pd
from visualisation.backend.config import HISTORICAL_CSV

def trim_csv(path=HISTORICAL_CSV, max_rows=30000):
    df = pd.read_csv(path, header=None)
    if len(df) > max_rows:
        df.tail(max_rows).to_csv(path, index=False, header=False)

if __name__ == "__main__":
    trim_csv()