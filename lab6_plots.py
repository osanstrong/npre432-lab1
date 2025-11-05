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

# print(f"nice files: ")
# pprint.pprint(nice_files)

temps_C = {
    "0C":0,
    "RT":22,
    "BW":100
} # and also 100c directly for some godforsaken reason

mats = [
    "1045HR",
    "2024T4",
    "ABS",
    "PMMA"
    ]

sec_marks = {
    'A':'o',
    'B':'*',
    'C':'s',
    'D':'^'
}

# Arrange into individual data sets?
sets = {}

for nice_file in nice_files:
    trim = nice_file.removeprefix("L6D/N01-").removesuffix(".csv").replace("2024-T4", '2024T4')
    temp = trim.split('-')[-1]
    if temp == '100C':
        temp_C = 100
    elif temp in temps_C:
        temp_C = temps_C[temp]
    else:
        continue
    g_mat = "-".join(trim.split('-')[0:2])
    # print(f"{g_mat}: {temp_C}")

    if not g_mat in sets:
        sets[g_mat] = {
            "temp":[],
            "energy":[],
            "max_load":[],
            "time_to_fail":[],
        }
    

    with open(nice_file, 'r') as dat_file:
        lines = dat_file.read().splitlines()
        for line in lines:
            points = line.split(',')
            if "Total Energy" in points[0]:
                ener = float(points[1])
            elif "Peak Force" in points[0]:
                mload = float(points[1])
            elif "Start Time" in points[0]:
                start = float(points[1])
            elif "Total Time" in points[0]:
                total = float(points[1])
        ttf = total-start    
        
        sets[g_mat]["temp"].append(temp_C)
        sets[g_mat]['energy'].append(ener)
        sets[g_mat]['max_load'].append(mload)
        sets[g_mat]['time_to_fail'].append(ttf)

pprint.pprint(sets)

fig, ax = plt.subplots()
ax.set_xlabel("Temperature (C)")
# ax.set_ylabel("Energy absorbed (J)")
ax.set_ylabel("Time to Failure (ms)")
for g_mat in sets:
    x_dat = sets[g_mat]['temp']
    # y_dat = sets[g_mat]['energy']
    y_dat = sets[g_mat]['time_to_fail']
    sec:str = g_mat.split('-')[0]
    mat:str = g_mat.split('-')[1]
    mat_col = f"C{mats.index(mat)}"
    sec_mrk = sec_marks[sec]

    ax.scatter(x_dat, y_dat, label=f"{mat} (Section {sec})", c=mat_col, marker=sec_mrk)
ax.legend()
plt.show()
    
