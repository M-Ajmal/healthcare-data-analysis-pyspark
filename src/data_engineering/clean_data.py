import re
import pandas as pd


# CONSTANTS
COLUMNS_TO_DROP = ["Name", "Doctor", "Room Number"]
VALID_GENDERS         = {"Male", "Female"}
VALID_BLOOD_TYPES     = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
VALID_MEDICAL_CONDITIONS = {
    "Diabetes", "Hypertension", "Asthma", "Obesity",
    "Cancer", "Arthritis", "Heart Disease", "Pneumonia",
}
VALID_TEST_RESULTS    = {"Normal", "Inconclusive", "Abnormal"}
VALID_ADMISSION_TYPES = {"Elective", "Urgent", "Emergency"}


# HELPER FUNCTIONS

def _to_snake_case(name: str) -> str:
    
    name = name.strip()
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", "_", name)
    
    return name.lower()


def _report_invalid(df: pd.DataFrame, col: str, valid_set: set) -> None:
    invalid_mask  = ~df[col].isin(valid_set)
    invalid_count = invalid_mask.sum()
    
    if invalid_count > 0:
        bad_vals = df.loc[invalid_mask, col].unique()[:5]
        print(f"  [warn] '{col}': {invalid_count:,} unexpected values → {bad_vals}")


# MAIN FUNCTION

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw healthcare DataFrame.

    Steps:
      1.  Rename columns to snake_case            
      2.  Drop PII and non-analytical columns     
      3.  Strip whitespace from all text columns
      4.  Standardize categorical fields         
      5.  Parse date columns to datetime
      6.  Enforce numeric types + cast age to int
      7.  Recompute length_of_stay from dates     
      8.  Round billing_amount to 2 decimal places
      9.  Remove rows that violate business rules
    """
    df = df.copy()
    original_len = len(df)

    # Rename columns to snake_case 
    df.columns = [_to_snake_case(col) for col in df.columns]
    print(f"[clean] Columns renamed: {df.columns.tolist()}")

    # Drop PII and non-analytical columns 
    cols_to_drop = [_to_snake_case(c) for c in COLUMNS_TO_DROP]
    existing_drops = [c for c in cols_to_drop if c in df.columns]
    
    df.drop(columns=existing_drops, inplace=True)
    print(f"[clean] Dropped columns: {existing_drops}")

    # Strip whitespace from all text columns 
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())

    # Standardize categorical fields 
    title_case_cols = [
        "gender", "medical_condition", "admission_type",
        "test_results", "medication", "insurance_provider",
    ]
    for col in title_case_cols:
        if col in df.columns:
            df[col] = df[col].str.title()

    if "blood_type" in df.columns:
        df["blood_type"] = df["blood_type"].str.upper()

    _report_invalid(df, "gender",            VALID_GENDERS)
    _report_invalid(df, "blood_type",        VALID_BLOOD_TYPES)
    _report_invalid(df, "medical_condition", VALID_MEDICAL_CONDITIONS)
    _report_invalid(df, "test_results",      VALID_TEST_RESULTS)
    _report_invalid(df, "admission_type",    VALID_ADMISSION_TYPES)

    # Parse date columns 
    for date_col in ["date_of_admission", "discharge_date"]:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            n_nat = df[date_col].isnull().sum()
            if n_nat > 0:
                print(f"  [warn] '{date_col}': {n_nat:,} unparseable values → NaT")

    # Enforce numeric types 
    if "billing_amount" in df.columns:
        df["billing_amount"] = pd.to_numeric(df["billing_amount"], errors="coerce")

    # FIX (moderate): age should be a whole number, not 45.0
    if "age" in df.columns:
        df["age"] = pd.to_numeric(df["age"], errors="coerce").astype("Int64")

    # Recompute length_of_stay from parsed dates 
    if "date_of_admission" in df.columns and "discharge_date" in df.columns:
        computed_stay = (df["discharge_date"] - df["date_of_admission"]).dt.days

        if "length_of_stay" in df.columns:
            mismatches = (df["length_of_stay"] != computed_stay).sum()
            if mismatches > 0:
                print(f"  [warn] 'length_of_stay': {mismatches:,} rows mismatched "
                      f"pre-calculated value — overwriting with computed value.")

        df["length_of_stay"] = computed_stay.astype("Int64")
        print(f"[clean] 'length_of_stay' recomputed from dates.")

    # Round billing_amount to 2 decimal places 
    if "billing_amount" in df.columns:
        df["billing_amount"] = df["billing_amount"].round(2)

    # Remove rows that violate business rules
    if "age" in df.columns:
        df = df[df["age"].between(0, 120)]

    if "length_of_stay" in df.columns:
        df = df[df["length_of_stay"] >= 0]

    if "date_of_admission" in df.columns and "discharge_date" in df.columns:
        df = df[df["discharge_date"] >= df["date_of_admission"]]

    removed = original_len - len(df)
    print(f"[clean] {removed:,} invalid rows removed. {len(df):,} rows remaining.")

    return df