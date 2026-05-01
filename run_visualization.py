# run_visualization.py
#
# Entry point for Phase 3 — Visualization.
# Run from the project root with:
#
#     python run_visualization.py
#
# Requires: pandas, matplotlib, seaborn
# The Spark pipeline (Phase 2) must have been completed first so that
# all CSV part files exist under data/output/<dataset>/.

import os
import sys

# Add src/ to the Python path so that the spark_processing package is importable
# regardless of which directory the user launches the script from.
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), "src"))

from spark_processing.visualize import run_all_visualizations  # noqa: E402

if __name__ == "__main__":
    run_all_visualizations()