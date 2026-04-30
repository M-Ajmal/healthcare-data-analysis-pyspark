# src/spark_processing/demographic_analysis.py

from pyspark.sql import DataFrame
from pyspark.sql.functions import count, col


def disease_by_gender(df: DataFrame, output_path: str) -> DataFrame:
    """
    Count patients per medical condition broken down by gender.
    Answers: Are certain diseases more common in male or female patients?
    """
    result = (
        df.groupBy("medical_condition", "gender")
          .agg(count("*").alias("patient_count"))
          .orderBy("medical_condition", col("patient_count").desc())
    )

    result.show(truncate=False)
    result.write.mode("overwrite").csv(output_path, header=True)
    print(f"[demographic] Disease by gender saved → {output_path}")

    return result


def disease_by_age_group(df: DataFrame, output_path: str) -> DataFrame:
    """
    Count patients per medical condition broken down by age group.
    Answers: Which age groups are most affected by each condition?
    """
    result = (
        df.groupBy("medical_condition", "age_group")
          .agg(count("*").alias("patient_count"))
          .orderBy("medical_condition", col("patient_count").desc())
    )

    result.show(truncate=False)
    result.write.mode("overwrite").csv(output_path, header=True)
    print(f"[demographic] Disease by age group saved → {output_path}")

    return result