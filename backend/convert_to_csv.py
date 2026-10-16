import pandas as pd
import os

# Location of the dataset folder
DATASET_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "dataset"
)

# XPT files to convert
files = [
    "DEMO_L.xpt",
    "BMX_L.xpt",
    "BPXO_L.xpt",
    "BPQ_L.xpt",
    "DIQ_L.xpt",
    "MCQ_L.xpt",
    "GHB_L.xpt",
    "GLU_L.xpt",
    "TCHOL_L.xpt",
    "HDL_L.xpt",
    "TRIGLY_L.xpt",
    "SMQ_L.xpt"
]

for filename in files:

    xpt_path = os.path.join(DATASET_FOLDER, filename)

    if not os.path.exists(xpt_path):
        print(f"❌ File not found: {filename}")
        continue

    print(f"Converting {filename}...")

    # Read XPT file
    data = pd.read_sas(xpt_path)

    # Create CSV filename
    csv_filename = filename.replace(".xpt", ".csv")
    csv_path = os.path.join(DATASET_FOLDER, csv_filename)

    # Save as CSV
    data.to_csv(csv_path, index=False)

    print(f"✅ Created: {csv_filename}")
    print(f"   Rows: {len(data)}")
    print(f"   Columns: {len(data.columns)}")
    print()

print("🎉 All possible files have been converted to CSV!")