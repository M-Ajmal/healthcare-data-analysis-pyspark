import pandas as pd


# Ordinal encoding maps
TEST_RESULTS_ORDER  = {"Normal": 0, "Inconclusive": 1, "Abnormal": 2}
ADMISSION_TYPE_ORDER = {"Elective": 0, "Urgent": 1, "Emergency": 2}


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived features to the cleaned healthcare DataFrame.

    New columns added:
      - age_group               : clinical age bracket
      - stay_category           : length-of-stay bucket
      - billing_category        : billing amount tier
      - admission_year          : year extracted from date_of_admission
      - admission_month         : month (1–12)
      - admission_day_of_week   : day of week (0=Monday … 6=Sunday)
      - test_results_encoded    : ordinal int (Normal=0, Inconclusive=1, Abnormal=2)
      - admission_type_encoded  : ordinal int (Elective=0, Urgent=1, Emergency=2)

    Columns removed:
      - date_of_admission, discharge_date  (raw dates; features extracted above)
    """
    df = df.copy()

    # Age group 
    if "age" in df.columns:
        df["age_group"] = pd.cut(
            df["age"],
            bins=[0, 12, 17, 60, 120],
            labels=["Child", "Teenager", "Adult", "Senior"],
            right=True,
            include_lowest=True,
        )

    # Stay category 
    if "length_of_stay" in df.columns:
        df["stay_category"] = pd.cut(
            df["length_of_stay"],
            bins=[0, 7, 30, float("inf")],
            labels=["Short", "Medium", "Long"],
            right=True,
            include_lowest=True,
        )

    # Billing category 
    if "billing_amount" in df.columns:
        df["billing_category"] = pd.cut(
            df["billing_amount"],
            bins=[0, 25_000, 60_000, float("inf")],
            labels=["Low", "Medium", "High"],
            right=True,
            include_lowest=True,
        )

    # Temporal features from date_of_admission 
    if "date_of_admission" in df.columns:
        df["admission_year"]        = df["date_of_admission"].dt.year
        df["admission_month"]       = df["date_of_admission"].dt.month
        df["admission_day_of_week"] = df["date_of_admission"].dt.dayofweek  # 0=Mon

    #  Ordinal encoding for test_results 
    if "test_results" in df.columns:
        df["test_results_encoded"] = df["test_results"].map(TEST_RESULTS_ORDER)

    # Ordinal encoding for admission_type
    if "admission_type" in df.columns:
        df["admission_type_encoded"] = df["admission_type"].map(ADMISSION_TYPE_ORDER)

    # Drop raw date columns 
    date_cols = ["date_of_admission", "discharge_date"]
    df.drop(columns=[c for c in date_cols if c in df.columns], inplace=True)

    print(f"[transform] Features added: age_group, stay_category, billing_category, "
          f"admission_year, admission_month, admission_day_of_week, "
          f"test_results_encoded, admission_type_encoded")
    print(f"[transform] Raw date columns dropped.")

    return df