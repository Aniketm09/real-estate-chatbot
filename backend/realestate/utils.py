import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "sample_data.xlsx"

_df_cache = None

def get_dataset():
    global _df_cache
    if _df_cache is None:
        df = pd.read_excel(DATA_PATH)
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
        _df_cache = df
    return _df_cache
