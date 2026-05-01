# src/spark_processing/visualize.py

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ── Style ─────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams.update({
    "figure.dpi": 130,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
})

# ── Base paths ────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")
CHARTS_DIR = os.path.join(OUTPUT_DIR, "charts")


# ── Helper ────────────────────────────────────────────────────────────────────

def _read_spark_csv(folder_name: str) -> pd.DataFrame:
    """
    Spark writes CSV output as part files (part-00000-....csv) inside a folder.
    This helper reads all part files in that folder and combines them into
    a single pandas DataFrame.
    """
    folder_path = os.path.join(OUTPUT_DIR, folder_name)
    part_files  = glob.glob(os.path.join(folder_path, "part-*.csv"))

    if not part_files:
        raise FileNotFoundError(
            f"No part files found in '{folder_path}'.\n"
            f"Make sure the Spark pipeline has been run first."
        )

    df = pd.concat([pd.read_csv(f) for f in part_files], ignore_index=True)
    return df


def _save(fig: plt.Figure, filename: str) -> None:
    """Save a figure to data/output/charts/ and close it."""
    os.makedirs(CHARTS_DIR, exist_ok=True)
    path = os.path.join(CHARTS_DIR, filename)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[viz] Saved → {path}")


# ── 1. Top Medical Conditions ─────────────────────────────────────────────────

def plot_top_conditions():
    """Horizontal bar chart — patient count per medical condition."""
    df = _read_spark_csv("top_conditions")
    df = df.sort_values("patient_count", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df["medical_condition"], df["patient_count"],
                   color=sns.color_palette("muted", len(df)))

    ax.bar_label(bars, fmt="{:,.0f}", padding=4, fontsize=10)
    ax.set_title("Patient Count by Medical Condition")
    ax.set_xlabel("Number of Patients")
    ax.set_ylabel("Medical Condition")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.set_xlim(0, df["patient_count"].max() * 1.12)

    _save(fig, "01_top_conditions.png")


# ── 2. Test Results Distribution ──────────────────────────────────────────────

def plot_test_results():
    """Pie chart + bar chart — proportion of Normal / Inconclusive / Abnormal."""
    df = _read_spark_csv("test_results")

    COLORS = {
        "Normal":       "#55a868",
        "Inconclusive": "#f5c518",
        "Abnormal":     "#c44e52",
    }
    colors = [COLORS.get(r, "#999999") for r in df["test_results"]]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Test Results Distribution", fontsize=14, fontweight="bold")

    # Pie
    axes[0].pie(
        df["patient_count"],
        labels=df["test_results"],
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        wedgeprops=dict(edgecolor="white", linewidth=1.5),
    )
    axes[0].set_title("Proportion")

    # Bar
    bars = axes[1].bar(df["test_results"], df["patient_count"], color=colors,
                       edgecolor="white", linewidth=1.2)
    axes[1].bar_label(bars, fmt="{:,.0f}", padding=4, fontsize=10)
    axes[1].set_title("Count")
    axes[1].set_xlabel("Test Result")
    axes[1].set_ylabel("Number of Patients")
    axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:,.0f}"))

    _save(fig, "02_test_results.png")


# ── 3. Disease by Gender ──────────────────────────────────────────────────────

def plot_disease_by_gender():
    """Grouped bar chart — male vs female count per medical condition."""
    df = _read_spark_csv("disease_by_gender")

    pivot = df.pivot(index="medical_condition",
                     columns="gender",
                     values="patient_count").fillna(0)
    pivot = pivot.sort_values(pivot.columns[0], ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    pivot.plot.bar(ax=ax, color=["#4C72B0", "#DD8452"],
                   edgecolor="white", linewidth=0.8, width=0.7)

    ax.set_title("Disease Distribution by Gender")
    ax.set_xlabel("Medical Condition")
    ax.set_ylabel("Number of Patients")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:,.0f}"))
    ax.legend(title="Gender")

    _save(fig, "03_disease_by_gender.png")


# ── 4. Disease by Age Group (Heatmap) ─────────────────────────────────────────

def plot_disease_by_age():
    """Heatmap — patient count per condition × age group."""
    df = _read_spark_csv("disease_by_age")

    AGE_ORDER = ["Child", "Teenager", "Adult", "Senior"]
    pivot = df.pivot(index="medical_condition",
                     columns="age_group",
                     values="patient_count").fillna(0)

    # Keep only columns that exist in the data
    age_cols = [c for c in AGE_ORDER if c in pivot.columns]
    pivot = pivot[age_cols]

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(
        pivot, annot=True, fmt=".0f", cmap="YlOrRd",
        linewidths=0.5, linecolor="white",
        ax=ax, cbar_kws={"label": "Patient Count"},
    )
    ax.set_title("Patient Count by Medical Condition and Age Group")
    ax.set_xlabel("Age Group")
    ax.set_ylabel("Medical Condition")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    _save(fig, "04_disease_by_age_heatmap.png")


# ── 5. Anomaly — Long Hospital Stays ─────────────────────────────────────────

def plot_long_stays():
    """Histogram of stay duration + bar chart of long stays by condition."""
    df = _read_spark_csv("long_stay")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Anomaly: Long Hospital Stays (> 14 Days)",
                 fontsize=14, fontweight="bold")

    # Histogram of length_of_stay values
    axes[0].hist(df["length_of_stay"], bins=30,
                 color="#c44e52", edgecolor="white", alpha=0.85)
    axes[0].axvline(14, color="black", linestyle="--",
                    linewidth=1.5, label="Threshold (14 days)")
    axes[0].set_title("Distribution of Long Stays")
    axes[0].set_xlabel("Length of Stay (days)")
    axes[0].set_ylabel("Number of Patients")
    axes[0].legend()

    # Count of long stays per condition
    condition_counts = (
        df.groupby("medical_condition")["length_of_stay"]
        .count()
        .reset_index(name="count")
        .sort_values("count", ascending=True)
    )
    bars = axes[1].barh(condition_counts["medical_condition"],
                        condition_counts["count"],
                        color="#c44e52", edgecolor="white", alpha=0.85)
    axes[1].bar_label(bars, fmt="{:,.0f}", padding=4, fontsize=10)
    axes[1].set_title("Long Stay Patients by Condition")
    axes[1].set_xlabel("Number of Patients")

    _save(fig, "05_anomaly_long_stays.png")


# ── 6. Anomaly — High Billing ─────────────────────────────────────────────────

def plot_high_billing():
    """Histogram of billing amounts + box plot by medical condition."""
    df = _read_spark_csv("high_billing")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Anomaly: High Billing Cases (> $50,000)",
                 fontsize=14, fontweight="bold")

    # Histogram
    axes[0].hist(df["billing_amount"], bins=30,
                 color="#e07b39", edgecolor="white", alpha=0.85)
    axes[0].axvline(50_000, color="black", linestyle="--",
                    linewidth=1.5, label="Threshold ($50,000)")
    axes[0].set_title("Distribution of High Billing Amounts")
    axes[0].set_xlabel("Billing Amount ($)")
    axes[0].set_ylabel("Number of Patients")
    axes[0].xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    axes[0].legend()

    # Box plot by condition
    order = (
        df.groupby("medical_condition")["billing_amount"]
        .median()
        .sort_values(ascending=False)
        .index.tolist()
    )
    sns.boxplot(data=df, y="medical_condition", x="billing_amount",
                order=order, palette="Oranges_r", orient="h", ax=axes[1])
    axes[1].set_title("Billing Amount by Condition")
    axes[1].set_xlabel("Billing Amount ($)")
    axes[1].set_ylabel("")
    axes[1].xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    _save(fig, "06_anomaly_high_billing.png")


# ── 7. Anomaly — Abnormal Test Results ───────────────────────────────────────

def plot_abnormal_tests():
    """Bar charts — abnormal results by condition and by admission type."""
    df = _read_spark_csv("abnormal_tests")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Anomaly: Abnormal Test Results",
                 fontsize=14, fontweight="bold")

    # By medical condition
    by_condition = (
        df.groupby("medical_condition")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=True)
    )
    bars = axes[0].barh(by_condition["medical_condition"],
                        by_condition["count"],
                        color="#9b59b6", edgecolor="white", alpha=0.85)

    # ✅ FIXED HERE
    axes[0].bar_label(bars, fmt="{:,.0f}", padding=4, fontsize=10)

    axes[0].set_title("Abnormal Results by Medical Condition")
    axes[0].set_xlabel("Number of Patients")

    # By admission type
    by_admission = (
        df.groupby("admission_type")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    bars2 = axes[1].bar(by_admission["admission_type"],
                        by_admission["count"],
                        color=["#c44e52", "#e07b39", "#9b59b6"],
                        edgecolor="white", linewidth=1.2)

    # ✅ FIXED HERE
    axes[1].bar_label(bars2, fmt="{:,.0f}", padding=4, fontsize=10)

    axes[1].set_title("Abnormal Results by Admission Type")
    axes[1].set_xlabel("Admission Type")
    axes[1].set_ylabel("Number of Patients")

    axes[1].yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda y, _: f"{y:,.0f}"))

    _save(fig, "07_anomaly_abnormal_tests.png")


# ── Run all ───────────────────────────────────────────────────────────────────

def run_all_visualizations():
    """Generate all 7 charts from the Spark pipeline outputs."""
    print("[viz] Starting visualization...\n")

    plot_top_conditions()
    plot_test_results()
    plot_disease_by_gender()
    plot_disease_by_age()
    plot_long_stays()
    plot_high_billing()
    plot_abnormal_tests()

    print(f"\n[viz] All charts saved to: {CHARTS_DIR}")