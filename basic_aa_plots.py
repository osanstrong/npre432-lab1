import matplotlib.pyplot as plt
import numpy as np
import scipy.stats


fig = plt.figure()
ax = plt.subplot()

mats = ['1018CR', '1045NM', '2024AL', '304SS', '7075AL']
hardness = [97.1, 91.1, 79.7, 103.0, 92.6]

el_mod = [198.67, 198.44, 68.97, 155.91, 66.7]
yd_str = [661.2, 487.3, 369.39, 477.65, 501.7]
ut_str = [688, 731.1, 485.3, 729.36, 550.3]
pc_eln = [17.15, 30.57, 22.23, 60.95, 16.83]
rs_mod = [1100.3, 598.3, 989.2, 731.7, 1882.3]


chosen = rs_mod 
m, b, r, p, std_err = scipy.stats.linregress(hardness, chosen)
# m, b, r, p, std_err = scipy.stats.linregress(np.log(hardness) - 80, np.log(chosen) - 10)

ax.set_xlabel("Hardness (HRB)")
# stat_name = "Elastic Modulus (GPa)"
# stat_name = "0.2% Yield Strength (MPa)"
# stat_name = "Ultimate Tensile Strength (MPa)"
# stat_name = "% Elongation"
stat_name = "Modulus of Resistance (kPa)"
ax.set_ylabel(stat_name)
ax.scatter(hardness, chosen)
fig.legend()
plt.title(f"Correlation r²: {r*r}")
# plt.title(f"Correlation r²: {r*r}, k={np.e**b}, n={m}")
plt.show()