# src/spark_processing/disease_analysis.py

from pyspark.sql import DataFrame
from pyspark.sql.functions import count, col


def top_medical_conditions(df: DataFrame, output_path: str) -> DataFrame:
    """
    Count patients per medical condition, ordered from most to least common.
    Answers: Which diseases are most prevalent in this dataset?
    """
    result = (
        df.groupBy("medical_condition")
          .agg(count("*").alias("patient_count"))
          .orderBy(col("patient_count").desc())
    )

    result.show(truncate=False)
    result.write.mode("overwrite").csv(output_path, header=True)
    print(f"[disease] Top conditions saved → {output_path}")

    return result


def test_results_distribution(df: DataFrame, output_path: str) -> DataFrame:
    """
    Count how many patients received each test result (Normal/Abnormal/Inconclusive).
    Answers: What proportion of patients have abnormal results?
    """
    result = (
        df.groupBy("test_results")
          .agg(count("*").alias("patient_count"))
          .orderBy(col("patient_count").desc())
    )

    result.show(truncate=False)
    result.write.mode("overwrite").csv(output_path, header=True)
    print(f"[disease] Test results distribution saved → {output_path}")

    return result