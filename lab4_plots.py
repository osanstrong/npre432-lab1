import matplotlib.pyplot as plt
import argparse
import glob
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--concentration', help="The concentration (of bismuth) to find information for, % [0,100], e.g. 5 for 5% Bismuth")
args = parser.parse_args()

# cooling curve data file
c = float(args.concentration)
cc_path = f'./L4D/NPRE432/d_Bi{args.concentration}.txt'
cc_df = pd.read_csv(cc_path, sep='\t', skiprows=[0])
hot_temp = cc_df['Temp1 deg C']
times = cc_df['Time (sec)']
print(cc_df)

# All the identified 


fig = plt.figure()
ax = fig.subplots()
ax.set_xlabel('Time (s)')
ax.set_ylabel('Temperature (⁰C)')
ax.plot(times, hot_temp, label=f"{c}% Bismuth")
fig.legend()
plt.show()