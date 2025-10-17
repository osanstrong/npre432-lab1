import matplotlib.pyplot as plt
import argparse
import glob
import pandas as pd
import numpy as np
import pprint

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--concentration', help="The concentration (of bismuth) to find information for, % [0,100], e.g. 5 for 5% Bismuth")
parser.add_argument('-s', '--section', help='Section whose data to use, e.g. "NPRE432" or "ME330_S2". Defaults to NPRE432')
args = parser.parse_args()

# cooling curve data file
c = int(args.concentration)
if not args.section is None:
    chosen_section = args.section
else:
    chosen_section = "NPRE432"
cc_path = f'./L4D/{chosen_section}/d_Bi{args.concentration}.txt'
cc_df = pd.read_csv(cc_path, sep='\t', skiprows=[0])
temp_0 = cc_df['Temp0 deg C']
temp_1 = cc_df['Temp1 deg C']
range_0 = max(temp_0) - min(temp_0)
range_1 = max(temp_1) - min(temp_1)
if range_0 > range_1:
    hot_temp = temp_0
else:
    hot_temp = temp_1
# hot_temp = cc_df['Temp1 deg C']
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
                int(conc): transes
            })
    transitions.update({
        section: section_data
    })
pprint.pprint(transitions)

fig = plt.figure()
ax = fig.subplots()
ax.set_xlabel('Time (s)')
ax.set_ylabel('Temperature (⁰C)')
xmin = min(times)
xmax = max(times)
print(chosen_section)
# melts = transitions[chosen_section][c]
# ax.hlines(melts[0], xmin, xmax, label=f"Liquidus/Solidus (melting point): {melts[0]}⁰C", colors='C1')
# ax.hlines(melts[0], xmin, xmax, label=f"Liquidus: {melts[0]}⁰C", colors=f'C1')
# ax.hlines(melts[1], xmin, xmax, label=f"Solidus: {melts[1]}⁰C", colors=f'C1')
ax.plot(times, hot_temp, label=f"{c}% Bismuth, {100-c}% Tin")
# i = 0
# for section in transitions:
#     dat = transitions[section]
#     i+=1
#     for conc in dat:
#         if int(c) == int(conc):
#             ax.hlines(dat[c], xmin, xmax, label=section, colors=f'C{i}')
fig.legend()
plt.show()
# m_Sn = 118.71
# m_Bi = 208.98
# def pBi_to_xSn(pBi):
#     '''
#     Convert mass percentage bismuth to atom fraction tin
#     '''
#     uxBi = pBi / m_Bi
#     uxSn = (100-pBi) / m_Sn
#     return uxSn / (uxSn + uxBi)
# img_path = "L4D/xSn_phase-dia_cropped.png"
# img = plt.imread(img_path)
# fig, ax = plt.subplots()
# ax.imshow(img, extent=[0,1,0,300])
# plt.gca().set_aspect(1/300)
# ax.set_xlabel("Atomic fraction xSn")
# ax.set_ylabel("Temperature (⁰C)")
# i = 0
# shapes=['o', 's', '*','^','v','<','>']
# for section in sorted(transitions.keys()):
#     if not section in ['NPRE432', 'ME330_S1', 'ME330_S2', 'ME330_S3', 'ME330_S4', 'ME330_S5']:
#         continue
#     dat = transitions[section]
#     concs = []
#     temps = []
#     for conc in dat:
#         transes = dat[conc]
#         for trans in transes:
#             concs.append(pBi_to_xSn(conc)) #ATOM fraction of TIN not MASS percent BISMUTH
#             temps.append(trans)
#     ax.scatter(concs, temps, label=section, marker=shapes[i], facecolors='none', edgecolors=f'C{i}', linewidths=1.5)
#     i+=1
# fig.legend()
# plt.show()