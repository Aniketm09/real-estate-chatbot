import pandas as pd
from pathlib import Path

# Path to CSV file
DATA_PATH = Path(__file__).resolve().parent.parent / "Sample_data.csv"

_df_cache = None

def get_dataset():
    global _df_cache

    if _df_cache is None:
        print("Loading dataset from:", DATA_PATH)

        df = pd.read_csv(DATA_PATH)

        # Clean column names
        df.columns = df.columns.str.strip()

        # Convert numeric columns safely
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass

        _df_cache = df

    return _df_cache