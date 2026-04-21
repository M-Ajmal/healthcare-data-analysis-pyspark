import pandas as pd


def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    print(f"[load]  {len(df):,} rows × {df.shape[1]} columns  ← {file_path}")
    
    return df