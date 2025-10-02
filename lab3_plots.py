import matplotlib.pyplot as plt


## Just as rolled
prerolled_thickness = [float(n) for n in "5.67	6.27	7.14	8.49	5.58	6.25	7.12	8.26".split('\t')]
prt = prerolled_thickness
prerolled_hardness = [float(n) for n in  "18.1	16.9	16.6	18.2	14.7	15.6	17.3	15.0".split('\t')]
rolled_thickness = [float(n) for n in "4.78	4.83	4.85	4.97	2.26	2.44	2.36	2.37".split('\t')]
rt = rolled_thickness
rolled_hardness_lines =  """57.4	68.9	76.3	81.7	67.1	60.9	61.2	59.3
                            52.7	69.7	77.6	82.8	64.1	61.6	61.6	61.3
                            54.9	72.0	80.4	83.8	41.3	60.4	60.1	62.6""".split('\n')
rolled_hardness = [[float(n) for n in line.split('\t')] for line in rolled_hardness_lines]
rolled_hardness_mean = [sum([rolled_hardness[l][i] for l in range(3)])/3 for i in range(len(rolled_hardness[0]))]
# %CW = (t0 - tf)/t0 * 100 
cold_work_r = [100*(prt[i] - rt[i]) / prt[i] for i in range(len(prt))]

print("Rolled")
print(rolled_hardness)
print(rolled_hardness_mean)
print(cold_work_r)
print("-"*20)
print("Annealed")
## Then also annealed
preannealed_hardness =  [float(n) for n in "13.2	18.5	19.3	18.6	19.8	26.2	21.9	23.1".split('\t')]
preannealed_thickness = [float(n) for n in "5.97	6.39	7.31	8.48	5.89	6.66	7.78	8.85".split('\t')]
pat = preannealed_thickness

annealed_thickness = [float(n) for n in "4.94	4.95	4.98	5.00	2.35	2.44	2.36	2.37".split('\t')]
at = annealed_thickness
annealed_hardness_lines =    """27.4	28.0	30.4	33.1	56.1	56.8	56.5	58.8
                                28.8	27.6	29.6	34.7	55.1	56.7	58.3	55.2
                                26.9	29.7	29.6	34.5	54.2	56.0	58.4	57.8""".split('\n')
annealed_hardness = [[float(n) for n in line.split('\t')] for line in annealed_hardness_lines]
annealed_hardness_mean = [sum([annealed_hardness[l][i] for l in range(3)])/3 for i in range(len(annealed_hardness[0]))]
cold_work_a = [100*(pat[i] - at[i]) / pat[i] for i in range(len(pat))]

# fig = plt.figure()
# ax = plt.subplot()
# ax.set_xlabel("% Cold Work")
# ax.set_ylabel("Hardness")
# ax.scatter(cold_work_r, rolled_hardness_mean, label="Cold-Rolled")
# ax.scatter(cold_work_a, annealed_hardness_mean, label="Annealed", marker="^")
# fig.legend()
# plt.show()

brass_strains = [0, 0.19, 2, 8]
brass_yields_MPa = [239.15, 239.15, 273.85, 317.82] #So percent increase of 32.55
# fig = plt.figure()
# ax = plt.subplot()
# ax.set_xlabel("% Cold Work")
# ax.set_ylabel("Yield Strength (MPa)")
# ax.scatter(brass_strains, brass_yields_MPa, label="Brass")
# fig.legend()
# plt.show()

## Sections 5-II, 5-IV, 2.5-II, 2.5-IV temperature vs hardness

ahm = annealed_hardness_mean
temp_C = [350, 400, 450, 500, 500] # end is last lab 2025
hard_50_II = [66, 64, 44, 36, ahm[1]]
hard_50_IV = [65, 62, 53, 45, ahm[3]]
hard_25_II = [65, 64, 58, 50, ahm[5]]
hard_25_IV = [67, 67, 60, 52, ahm[7]]

# fig = plt.figure()
# ax = plt.subplot()
# ax.set_xlabel("Annealing Temperature (⁰C)")
# ax.set_ylabel("Rolled-Annealed Hardness (HRB)")
# ax.scatter(temp_C, hard_50_II, label='5.0mm Mark II')
# ax.scatter(temp_C, hard_50_IV, label='5.0mm Mark IV', marker='^')
# ax.scatter(temp_C, hard_25_II, label='2.5mm Mark II', marker='s')
# ax.scatter(temp_C, hard_25_IV, label='2.5mm Mark IV', marker='*')
# fig.legend()
# plt.show()


# Micrograph mechanism map base
a_temps = [350, 400, 450, 500]
cw_percents = [cold_work_a[2], cold_work_a[6]]
categories = [ # 1 = recovery only, 2 = recovery and partial recrystalization, 3 = recovery with 100% recrystallization and potential grain growth
    [1, 2, 2, 3],
    [2, 2, 3, 3]
]

icons = ['o', '^', 's']
names = ["Recovery only", "Recovery and Partial Recrystallization", "Full Recovery and Potential Grain Growth"]

fig = plt.figure()
ax = plt.subplot()
ax.set_xlabel("Annealing Temperature (⁰C)")
ax.set_ylabel("% Cold Work")
for c in range(1,4):
    temps = []
    cws = []
    for i in range(4):
        for j in range(2):
            if categories[j][i] == c:
                temps.append(a_temps[i])
                cws.append(cw_percents[j])
    ax.scatter(temps, cws, marker=icons[c-1], label=names[c-1])
fig.legend()
plt.show()