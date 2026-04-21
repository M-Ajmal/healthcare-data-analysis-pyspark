# pyspark-recommendation-system

## Project structure
 
```
project_root/
├── data/
│   ├── raw/
│   │   └── modified_healthcare_dataset.csv   ← place raw file here
│   └── processed/                            ← pipeline writes here
│       ├── healthcare_clean.csv
│       └── healthcare_clean.parquet
│
├── src/
│   └── data_engineering/
│       ├── __init__.py
│       ├── load_data.py
│       ├── clean_data.py
│       ├── transform_data.py
│       └── pipeline.py
│
├── run_pipeline.py                           ← entry point
└── requirements.txt
```
 
---
 
## Requirements
 
Python 3.8 or higher.
 
Install dependencies:
 
```bash
pip install -r requirements.txt
```
 
`requirements.txt`:
 
```
pandas>=1.5.0
pyarrow>=10.0.0
```
 
---
 
## Setup
 
**1. Clone or download the project.**
 
**2. Place the raw dataset** at:
 
```
data/raw/modified_healthcare_dataset.csv
```
 
**3. Create the `__init__.py`** file so Python treats the folder as a package:
 
```bash
touch src/data_engineering/__init__.py
```
 
**4. Create `run_pipeline.py`** at the project root with this content:
 
```python
import sys
import os
 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
 
from data_engineering.pipeline import run_pipeline
 
df = run_pipeline(
    input_path          = "data/raw/modified_healthcare_dataset.csv",
    output_csv_path     = "data/processed/healthcare_clean.csv",
    output_parquet_path = "data/processed/healthcare_clean.parquet",
)
```
 
---
 
## Running the pipeline
 
From the project root:
 
```bash
python run_pipeline.py
```
 
Expected output:
 
```
[load]      55,500 rows × 16 columns  ← data/raw/modified_healthcare_dataset.csv
[clean]     Columns renamed: ['age', 'gender', 'blood_type', ...]
[clean]     Dropped columns: ['name', 'doctor', 'room_number']
[clean]     'length_of_stay' recomputed from dates.
[clean]     0 invalid rows removed. 55,500 rows remaining.
[transform] Features added: age_group, stay_category, billing_category, ...
[transform] Raw date columns dropped.
 
[pipeline] ── SUMMARY ──────────────────────────────
[pipeline] Raw shape     : 55,500 rows × 16 cols
[pipeline] Final shape   : 55,500 rows × 19 cols
[pipeline] Rows removed  : 0
[pipeline] CSV saved     → data/processed/healthcare_clean.csv
[pipeline] Parquet saved → data/processed/healthcare_clean.parquet
```
 
---
 
## Output files
 
| File | Format | Purpose |
|---|---|---|
| `healthcare_clean.csv` | CSV | Human review, Excel, notebooks |
| `healthcare_clean.parquet` | Parquet (Snappy) | Spark input — preserves schema, faster reads |
 
### Final columns (19)
 
| Column | Type | Description |
|---|---|---|
| `age` | Int64 | Patient age (validated 0–120) |
| `gender` | string | Male / Female |
| `blood_type` | string | A+, A−, B+, B−, AB+, AB−, O+, O− |
| `medical_condition` | string | One of 8 known conditions |
| `hospital` | string | Admitting hospital |
| `insurance_provider` | string | Patient's insurer |
| `billing_amount` | float64 | Total charge, rounded to 2 d.p. |
| `admission_type` | string | Elective / Urgent / Emergency |
| `medication` | string | Prescribed medication |
| `test_results` | string | Normal / Inconclusive / Abnormal |
| `length_of_stay` | Int64 | Days (recomputed from dates) |
| `age_group` | category | Child / Teenager / Adult / Senior |
| `stay_category` | category | Short (≤7d) / Medium (≤30d) / Long |
| `billing_category` | category | Low / Medium / High |
| `admission_year` | int32 | Year of admission |
| `admission_month` | int32 | Month of admission (1–12) |
| `admission_day_of_week` | int32 | 0 = Monday … 6 = Sunday |
| `test_results_encoded` | int64 | Normal=0, Inconclusive=1, Abnormal=2 |
| `admission_type_encoded` | int64 | Elective=0, Urgent=1, Emergency=2 |
 
---