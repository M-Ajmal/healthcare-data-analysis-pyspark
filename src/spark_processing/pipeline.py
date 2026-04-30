# src/spark_processing/pipeline.py

import os

from spark_processing.spark_session        import create_spark_session
from spark_processing.load_processed_data  import load_data
from spark_processing.disease_analysis     import top_medical_conditions, test_results_distribution
from spark_processing.demographic_analysis import disease_by_gender, disease_by_age_group
from spark_processing.anomaly_detection    import detect_long_stays, detect_high_billing, detect_abnormal_tests


# ── Absolute base path ────────────────────────────────────────────────────────
# FIX (cause 2): Build all paths relative to THIS file's location, not the
#                working directory. Works correctly with both python and spark-submit.
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

# ── Input ─────────────────────────────────────────────────────────────────────
PARQUET_INPUT = os.path.join(BASE_DIR, "data", "processed", "healthcare_cleaned.parquet")

# ── Output paths ──────────────────────────────────────────────────────────────
OUT_TOP_CONDITIONS = os.path.join(BASE_DIR, "data", "output", "top_conditions")
OUT_TEST_RESULTS   = os.path.join(BASE_DIR, "data", "output", "test_results")
OUT_BY_GENDER      = os.path.join(BASE_DIR, "data", "output", "disease_by_gender")
OUT_BY_AGE         = os.path.join(BASE_DIR, "data", "output", "disease_by_age")
OUT_LONG_STAY      = os.path.join(BASE_DIR, "data", "output", "long_stay")
OUT_HIGH_BILLING   = os.path.join(BASE_DIR, "data", "output", "high_billing")
OUT_ABNORMAL_TESTS = os.path.join(BASE_DIR, "data", "output", "abnormal_tests")

ALL_OUTPUT_PATHS = [
    OUT_TOP_CONDITIONS, OUT_TEST_RESULTS,
    OUT_BY_GENDER,      OUT_BY_AGE,
    OUT_LONG_STAY,      OUT_HIGH_BILLING,
    OUT_ABNORMAL_TESTS,
]


def _local(path: str) -> str:
    """Prefix a local path with file:// so Spark never routes it through HDFS."""
    return path if path.startswith("file://") else f"file://{path}"


def _create_output_dirs():
    """
    FIX (cause 1, 3, 4): Create all output directories before Spark writes anything.
    os.makedirs with exist_ok=True is safe to call even if the folder already exists.
    """
    for path in ALL_OUTPUT_PATHS:
        os.makedirs(path, exist_ok=True)
    print(f"[pipeline] Output directories ready under: {os.path.join(BASE_DIR, 'data', 'output')}")


def run_pipeline():
    """
    Full Spark processing pipeline:
      1. Create output directories
      2. Create SparkSession
      3. Load cleaned Parquet
      4. Run disease analysis
      5. Run demographic analysis
      6. Run anomaly detection
      7. Stop SparkSession
    """

    # ── 1. Create output directories FIRST ───────────────────────────────────
    _create_output_dirs()

    # ── 2. Start Spark ────────────────────────────────────────────────────────
    spark = create_spark_session()

    # ── 3. Load data ──────────────────────────────────────────────────────────
    df = load_data(spark, PARQUET_INPUT)

    # ── 4. Disease analysis ───────────────────────────────────────────────────
    print("\n── DISEASE ANALYSIS ─────────────────────────────────")
    top_medical_conditions(df,    _local(OUT_TOP_CONDITIONS))
    test_results_distribution(df, _local(OUT_TEST_RESULTS))

    # ── 5. Demographic analysis ───────────────────────────────────────────────
    print("\n── DEMOGRAPHIC ANALYSIS ─────────────────────────────")
    disease_by_gender(df,    _local(OUT_BY_GENDER))
    disease_by_age_group(df, _local(OUT_BY_AGE))

    # ── 6. Anomaly detection ──────────────────────────────────────────────────
    print("\n── ANOMALY DETECTION ────────────────────────────────")
    detect_long_stays(df,     _local(OUT_LONG_STAY))
    detect_high_billing(df,   _local(OUT_HIGH_BILLING))
    detect_abnormal_tests(df, _local(OUT_ABNORMAL_TESTS))

    # ── 7. Done ───────────────────────────────────────────────────────────────
    print(f"\n[pipeline] All analysis complete.")
    print(f"[pipeline] Results saved to: {os.path.join(BASE_DIR, 'data', 'output')}")
    spark.stop()
    print("[pipeline] SparkSession stopped.")