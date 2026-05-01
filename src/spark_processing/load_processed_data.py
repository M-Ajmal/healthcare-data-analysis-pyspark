# src/spark_processing/load_processed_data.py

from pyspark.sql import SparkSession, DataFrame


def load_data(spark: SparkSession, parquet_path: str) -> DataFrame:
    """
    Load the cleaned healthcare Parquet file into a Spark DataFrame.
    Schema is automatically inferred from the Parquet metadata.
    """
    # Prefix with file:// to force local filesystem — prevents Spark from
    # misrouting the path through HDFS (hdfs://localhost:9000/...) when a
    # Hadoop config is present on the machine.
    local_path = parquet_path if parquet_path.startswith("file://") else f"file://{parquet_path}"
    df = spark.read.parquet(local_path)

    print(f"[load] Loaded {df.count():,} rows from '{parquet_path}'")
    print(f"[load] Columns: {df.columns}")

    return df