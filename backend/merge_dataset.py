import pandas as pd
import os

# --------------------------------------------------
# DATASET LOCATION
# --------------------------------------------------

DATASET_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "dataset"
)

# --------------------------------------------------
# LOAD CSV FILES
# --------------------------------------------------

print("Loading datasets...")

demo = pd.read_csv(os.path.join(DATASET_FOLDER, "DEMO_L.csv"))
bmx = pd.read_csv(os.path.join(DATASET_FOLDER, "BMX_L.csv"))
bpx = pd.read_csv(os.path.join(DATASET_FOLDER, "BPXO_L.csv"))
diq = pd.read_csv(os.path.join(DATASET_FOLDER, "DIQ_L.csv"))
mcq = pd.read_csv(os.path.join(DATASET_FOLDER, "MCQ_L.csv"))
ghb = pd.read_csv(os.path.join(DATASET_FOLDER, "GHB_L.csv"))
glu = pd.read_csv(os.path.join(DATASET_FOLDER, "GLU_L.csv"))
tchol = pd.read_csv(os.path.join(DATASET_FOLDER, "TCHOL_L.csv"))
hdl = pd.read_csv(os.path.join(DATASET_FOLDER, "HDL_L.csv"))
trigly = pd.read_csv(os.path.join(DATASET_FOLDER, "TRIGLY_L.csv"))
smq = pd.read_csv(os.path.join(DATASET_FOLDER, "SMQ_L.csv"))

print("All CSV files loaded successfully.")


# --------------------------------------------------
# SELECT REQUIRED COLUMNS
# --------------------------------------------------

demo = demo[
    [
        "SEQN",
        "RIDAGEYR",
        "RIAGENDR"
    ]
]

bmx = bmx[
    [
        "SEQN",
        "BMXBMI"
    ]
]

bpx = bpx[
    [
        "SEQN",
        "BPXOSY1",
        "BPXODI1",
        "BPXOSY2",
        "BPXODI2",
        "BPXOSY3",
        "BPXODI3"
    ]
]

diq = diq[
    [
        "SEQN",
        "DIQ010"
    ]
]

mcq = mcq[
    [
        "SEQN",
        "MCQ160C"
    ]
]

ghb = ghb[
    [
        "SEQN",
        "LBXGH"
    ]
]

glu = glu[
    [
        "SEQN",
        "LBXGLU"
    ]
]

tchol = tchol[
    [
        "SEQN",
        "LBXTC"
    ]
]

hdl = hdl[
    [
        "SEQN",
        "LBDHDD"
    ]
]

trigly = trigly[
    [
        "SEQN",
        "LBXTLG"
    ]
]

smq = smq[
    [
        "SEQN",
        "SMQ020",
        "SMQ040"
    ]
]


# --------------------------------------------------
# RENAME COLUMNS
# --------------------------------------------------

demo = demo.rename(columns={
    "RIDAGEYR": "age",
    "RIAGENDR": "gender"
})

bmx = bmx.rename(columns={
    "BMXBMI": "bmi"
})

diq = diq.rename(columns={
    "DIQ010": "diabetes"
})

mcq = mcq.rename(columns={
    "MCQ160C": "heart_disease"
})

ghb = ghb.rename(columns={
    "LBXGH": "hba1c"
})

glu = glu.rename(columns={
    "LBXGLU": "glucose"
})

tchol = tchol.rename(columns={
    "LBXTC": "cholesterol"
})

hdl = hdl.rename(columns={
    "LBDHDD": "hdl"
})

trigly = trigly.rename(columns={
    "LBXTLG": "triglycerides"
})


# --------------------------------------------------
# MERGE USING SEQN
# --------------------------------------------------

print("Merging datasets...")

df = demo.merge(bmx, on="SEQN", how="left")

df = df.merge(bpx, on="SEQN", how="left")
df = df.merge(diq, on="SEQN", how="left")
df = df.merge(mcq, on="SEQN", how="left")
df = df.merge(ghb, on="SEQN", how="left")
df = df.merge(glu, on="SEQN", how="left")
df = df.merge(tchol, on="SEQN", how="left")
df = df.merge(hdl, on="SEQN", how="left")
df = df.merge(trigly, on="SEQN", how="left")
df = df.merge(smq, on="SEQN", how="left")


# --------------------------------------------------
# CALCULATE AVERAGE BLOOD PRESSURE
# --------------------------------------------------

systolic_columns = [
    "BPXOSY1",
    "BPXOSY2",
    "BPXOSY3"
]

diastolic_columns = [
    "BPXODI1",
    "BPXODI2",
    "BPXODI3"
]

df["systolic_bp"] = df[systolic_columns].mean(axis=1)
df["diastolic_bp"] = df[diastolic_columns].mean(axis=1)


# --------------------------------------------------
# CREATE HYPERTENSION TARGET
# --------------------------------------------------

# This is a project-defined target based on measured
# systolic/diastolic blood pressure.
#
# >= 130 systolic OR >= 80 diastolic = hypertension.

df["hypertension"] = (
    (df["systolic_bp"] >= 130) |
    (df["diastolic_bp"] >= 80)
).astype(int)


# --------------------------------------------------
# CREATE SMOKING VARIABLE
# --------------------------------------------------

# SMQ020:
# 1 = Yes
# 2 = No
#
# We create:
# 1 = Has smoked at least 100 cigarettes
# 0 = No

df["smoking"] = df["SMQ020"].map({
    1: 1,
    2: 0
})


# --------------------------------------------------
# REMOVE UNNECESSARY BP COLUMNS
# --------------------------------------------------

df = df.drop(
    columns=[
        "BPXOSY1",
        "BPXOSY2",
        "BPXOSY3",
        "BPXODI1",
        "BPXODI2",
        "BPXODI3",
        "SMQ020",
        "SMQ040"
    ]
)


# --------------------------------------------------
# KEEP ADULT PARTICIPANTS
# --------------------------------------------------

df = df[df["age"] >= 20]


# --------------------------------------------------
# REPLACE COMMON MISSING VALUES
# --------------------------------------------------

df = df.replace(
    [
        7,
        9,
        77,
        99,
        777,
        999
    ],
    pd.NA
)


# --------------------------------------------------
# SAVE FINAL DATASET
# --------------------------------------------------

output_path = os.path.join(
    DATASET_FOLDER,
    "patient_health_dataset.csv"
)

df.to_csv(
    output_path,
    index=False
)

print("\n==============================================")
print("DATASET CREATED SUCCESSFULLY")
print("==============================================")

print("File:")
print(output_path)

print("\nRows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
for column in df.columns:
    print(column)

print("\nFirst 5 rows:")
print(df.head())