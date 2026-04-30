# src/spark_processing/spark_session.py

from pyspark.sql import SparkSession


def create_spark_session() -> SparkSession:
    """Create and return a local SparkSession for healthcare analysis."""
    spark = (
        SparkSession.builder
        .appName("HealthcareAnalysisSystem")
        .master("local[*]")          # use all available CPU cores locally
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")   # suppress INFO/WARN noise in terminal
    print("[spark] SparkSession created.")
    return spark