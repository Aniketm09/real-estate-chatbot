import pandas as pd
from pathlib import Path

# Path to CSV file
DATA_PATH = Path(__file__).resolve().parent.parent / "Sample_data.csv"

_df_cache = None


def get_dataset():
    global _df_cache

    if _df_cache is None:

        print("Loading dataset from:", DATA_PATH)

        _df_cache = pd.read_csv(DATA_PATH)

        # normalize column names
        _df_cache.columns = _df_cache.columns.str.strip()

    return _df_cache