import matplotlib.pyplot as plt
import argparse
import glob
import pandas as pd
import numpy as np
import pprint

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--concentration', help="The concentration (of bismuth) to find information for, % [0,100], e.g. 5 for 5% Bismuth")
args = parser.parse_args()

# cooling curve data file
c = int(args.concentration)
cc_path = f'./L4D/NPRE432/d_Bi{args.concentration}.txt'
cc_df = pd.read_csv(cc_path, sep='\t', skiprows=[0])
hot_temp = cc_df['Temp1 deg C']
times = cc_df['Time (sec)']
print(cc_df)

transitions = {}
# All the identified transition points
trans_paths = glob.glob("./L4D/*/d_trans.txt")
print(f"Searching for transition data at: {trans_paths}")
# for path in trans_paths:
#     trans_df = pd.read_csv(path, sep='\t', skiprows=[0])
#     concs = trans_df['%Bi']
#     for i in range(len(concs)):
#         conc = concs[i]

#         transitions.update()
#     # print(trans_df)
for path in trans_paths:
    section = path.removeprefix("./L4D/").removesuffix("/d_trans.txt")
    print(f"Section: {section}")
    trans_df = pd.read_csv(path, sep='\t', skiprows=[0])
    print(trans_df)
    concs = trans_df['%Bi']
    section_data = {}
    for i in range(len(concs)):
        conc = concs[i]
        transes = []
        for id in ["1st", "2nd", "3rd"]:
            col = f'{id} transition'
            if not np.isnan(trans_df[col][i]):
                transes.append(trans_df[col][i])
        if transes:
            section_data.update({
                conc: transes
            })
    transitions.update({
        section: section_data
    })
pprint.pprint(transitions)

fig = plt.figure()
ax = fig.subplots()
ax.set_xlabel('Time (s)')
ax.set_ylabel('Temperature (⁰C)')
ax.plot(times, hot_temp, label=f"{c}% Bismuth")
xmin, xmax = ax.get_xlim()
i = 0
for section in transitions:
    dat = transitions[section]
    i+=1
    for conc in dat:
        print(f"Concentration: {conc}")
        if int(c) == int(conc):
            ax.hlines(dat[c], xmin, xmax, label=section, colors=f'C{i}')
fig.legend()
plt.show()