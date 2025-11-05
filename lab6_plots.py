import glob
import pprint
import matplotlib.pyplot as plt

files = glob.glob("L6D/N01-*.csv")
raw_files = glob.glob("L6D/N01-*Ch_1.csv")
nice_files = []
for file in files:
    if not file in raw_files:
        nice_files.append(file)
nice_files:list[str] = sorted(nice_files)

print(f"nice files: ")
pprint.pprint(nice_files)

temps_C = {
    "0C":0,
    "RT":22,
    "BW":100
} # and also 100c directly for some godforsaken reason

mats = [
    "1045HR",
    "2024-T4",
    "ABS",
    "PMMA"
    ]

# Arrange into individual data sets?
for nice_file in nice_files:
    trim = nice_file.removeprefix("L6D/N01-").removesuffix(".csv")

    print(trim)
