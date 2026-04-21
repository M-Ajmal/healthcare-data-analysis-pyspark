import os
import pandas as pd

from src.data_engineering.load_data import load_data
from src.data_engineering.clean_data import clean_data
from src.data_engineering.transform_data import transform_data


def run_pipeline(input_path: str, output_csv_path: str, output_parquet_path: str,) -> pd.DataFrame:
    """
    Execute the full data engineering pipeline.

    Flow: raw CSV → load → clean → transform → save (CSV + Parquet)

    Args:
        input_path          : path to the raw CSV file
        output_csv_path     : destination for the cleaned CSV (human review)
        output_parquet_path : destination for the Spark-ready Parquet file

    Returns:
        The final processed DataFrame.
    """
    # Load raw data
    df_raw = load_data(input_path)
    raw_shape = df_raw.shape

    # Clean
    df_clean = clean_data(df_raw)

    # Transform 
    df_final = transform_data(df_clean)

    # Save outputs
    os.makedirs(os.path.dirname(output_csv_path),     exist_ok=True)
    os.makedirs(os.path.dirname(output_parquet_path), exist_ok=True)

    df_final.to_csv(output_csv_path, index=False)
    df_final.to_parquet(output_parquet_path, index=False, engine="pyarrow")

    # ── Step 5: Summary ───────────────────────────────────────────────────────
    print(f"\n[pipeline] ── SUMMARY ──────────────────────────────")
    print(f"[pipeline] Raw shape     : {raw_shape[0]:,} rows × {raw_shape[1]} cols")
    print(f"[pipeline] Final shape   : {df_final.shape[0]:,} rows × {df_final.shape[1]} cols")
    print(f"[pipeline] Rows removed  : {raw_shape[0] - df_final.shape[0]:,}")
    print(f"[pipeline] CSV saved     → {output_csv_path}")
    print(f"[pipeline] Parquet saved → {output_parquet_path}")
    print(f"[pipeline] Final columns :")
    for col in df_final.columns:
        print(f"             {col}  ({df_final[col].dtype})")
    print(f"[pipeline] ────────────────────────────────────────")

    return df_final