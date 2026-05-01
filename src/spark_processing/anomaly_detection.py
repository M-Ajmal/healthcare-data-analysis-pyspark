# src/spark_processing/anomaly_detection.py

from pyspark.sql import DataFrame


# ── Thresholds ────────────────────────────────────────────────────────────────
LONG_STAY_THRESHOLD    = 14       # days
HIGH_BILLING_THRESHOLD = 50_000   # USD


def detect_long_stays(df: DataFrame, output_path: str) -> DataFrame:
    """
    Flag patients whose hospital stay exceeded 14 days.
    Long stays may indicate complications or severe conditions.
    """
    result = (
        df.filter(df["length_of_stay"] > LONG_STAY_THRESHOLD)
          .orderBy("length_of_stay", ascending=False)
    )

    print(f"[anomaly] Long stays (>{LONG_STAY_THRESHOLD} days): {result.count():,} patients")
    result.show(10, truncate=False)
    result.write.mode("overwrite").csv(output_path, header=True)
    print(f"[anomaly] Long stay records saved → {output_path}")

    return result


def detect_high_billing(df: DataFrame, output_path: str) -> DataFrame:
    """
    Flag patients whose billing amount exceeded $50,000.
    High billing may indicate costly procedures or extended care.
    """
    result = (
        df.filter(df["billing_amount"] > HIGH_BILLING_THRESHOLD)
          .orderBy("billing_amount", ascending=False)
    )

    print(f"[anomaly] High billing (>${HIGH_BILLING_THRESHOLD:,}): {result.count():,} patients")
    result.show(10, truncate=False)
    result.write.mode("overwrite").csv(output_path, header=True)
    print(f"[anomaly] High billing records saved → {output_path}")

    return result


def detect_abnormal_tests(df: DataFrame, output_path: str) -> DataFrame:
    """
    Isolate all patients with Abnormal test results.
    Cross-referenced with condition and admission type for pattern detection.
    """
    result = (
        df.filter(df["test_results"] == "Abnormal")
          .orderBy("medical_condition")
    )

    print(f"[anomaly] Abnormal test results: {result.count():,} patients")
    result.show(10, truncate=False)
    result.write.mode("overwrite").csv(output_path, header=True)
    print(f"[anomaly] Abnormal test records saved → {output_path}")

    return result