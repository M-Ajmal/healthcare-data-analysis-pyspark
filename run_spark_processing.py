#import sys
#import os

#sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

#from spark_processing.pipeline import run_pipeline

#if __name__ == "__main__":
 #   run_pipeline()
    
import sys
import os

# FIX (cause 2): Add src/ using an absolute path derived from THIS file's
#                location — not the working directory. Survives spark-submit.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from src.spark_processing.pipeline import run_pipeline

if __name__ == "__main__":
    run_pipeline()