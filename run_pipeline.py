from src.data_engineering.pipeline import run_pipeline

df = run_pipeline(
    input_path="data/raw/healthcare_dataset.csv",
    output_csv_path="data/processed/healthcare_clean.csv",
    output_parquet_path="data/processed/healthcare_clean.parquet",
)
