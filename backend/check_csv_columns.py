import pandas as pd
import os

DATASET_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "dataset"
)

files = [
    "DEMO_L.csv",
    "BMX_L.csv",
    "BPXO_L.csv",
    "BPQ_L.csv",
    "DIQ_L.csv",
    "MCQ_L.csv",
    "GHB_L.csv",
    "GLU_L.csv",
    "TCHOL_L.csv",
    "HDL_L.csv",
    "TRIGLY_L.csv",
    "SMQ_L.csv"
]

for filename in files:

    path = os.path.join(DATASET_FOLDER, filename)

    print("\n" + "=" * 70)
    print(filename)
    print("=" * 70)

    if not os.path.exists(path):
        print("FILE NOT FOUND")
        continue

    df = pd.read_csv(path)

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\nColumn names:")

    for column in df.columns:
        print(column)