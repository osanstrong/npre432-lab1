import matplotlib.pyplot as plt
import pandas as pd
import argparse
from io import StringIO
import numpy as np
from scipy.optimize import curve_fit

## Constants
PI = 3.141592653589
YIELD_OFFSET = 0.002 # 0.2%

## Grab the file name
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filepath', help="The csv file to read")
parser.add_argument('-c', '--curve-threshold', help="The curvature/second derivative threshold for finding the linear region of the stress strain plot", type=float, default=0.05)
parser.add_argument('-t','--true-stress', help="If given, also plots the true stress (compared to engineering stress)", action='store_true')
parser.add_argument('-m','--modulus-range', help="The range of the dataset (where [0:1] is full range) to average slope over to calculate elastic modulus")
parser.add_argument('-r', '--range-estimation', help="If specified, graphs just the strain and stress of each vs timestamp, to get ranges for slope estimation" ,action='store_true')
parser.add_argument('--tensile', help="If the strain is tensile rather than compressive, for calculating true strain", action='store_true' )
parser.add_argument('-p', '--power-law', help="Plot a power law relationship (sig_t = K(eps_t)^n) for the given range assumed to be plastic. Include 'ng' to skip graphing, include 'nl' to graph in normal axes instead of log-log")

args = parser.parse_args()

fpaths:list = args.filepath.split(';')
mat_dfs:dict = {}
mod_range:tuple = None
mat_mods:dict = {}
mat_bs:dict = {} #Intercept offset to get it to line up with the straight region of the graph
mat_yields:dict = {} #Yield Strengths of materials
mat_ultimates:dict = {} #Ultimate Strengths of materials
mat_k:dict = {} #K values of power law
mat_n:dict = {} #n values of power law
if not args.modulus_range is None:
    bounds = args.modulus_range.split("-")
    mod_range = (float(bounds[0]), float(bounds[1]))
power_law = False
graph_pl = False
if not args.power_law is None:
    power_law = True
    if not 'ng' in args.power_law:
        graph_pl = True
        pl_loglog = True
    if 'nl' in args.power_law:
        pl_loglog = False
    bounds = args.power_law.replace('nl', '').replace('ng','').split('-')
    pl_range = (float(bounds[0]), float(bounds[1]))

for fpath in fpaths:
    ## Get file text, and process the curve data out
    with open(fpath) as file: raw_text = file.read()
    lines = raw_text.splitlines()
    for i in range(len(lines)):
        line = lines[i]
        if line.startswith('Time,Disp'):
            header_idx = i
        elif line.startswith('Diameter') or line.startswith('Gage Diameter'):
            dia_mm = float(line.split(',')[-1].replace('"', ''))
        elif line.startswith('Material'):
            mat_name = line.split(',')[-1].replace('"','')
        elif line.startswith('Rockwell Hardness'):
            rockwell_hardness = line.split(',')[-1].replace('"', '')
        elif line.startswith('Rockwell Scale'):
            rockwell_scale = line.split(',')[-1].replace('"', '')

    # unit_line = lines.pop(header_idx+1) #It also includes a line about units 
    graph_lines = lines[header_idx:]
    graph_str = "\n".join(graph_lines)

    graph_df = pd.read_csv(StringIO(graph_str))
    cols = graph_df.columns

    # Confirm we're working with the units we know about
    assert graph_df['Force'][0] == '(kN)' 


    print(f"Diameter: {dia_mm} mm")

    area_m2 = (dia_mm*0.001*0.5)**2 * PI
    print(f"Area: {area_m2} m²")

    if not mod_range is None: print(f"Modulus range: {mod_range}")

    print(f"Rockwell Hardness: {rockwell_hardness} {rockwell_scale}")

    graph_df.loc[:,'Stress'] = None
    graph_df.loc[0, 'Stress'] = '(kPa)'
    graph_df.loc[1:, 'Stress'] = graph_df.loc[1:, 'Force'].astype(float) / area_m2

    if "Composite strain" in cols:
        strain_col = graph_df['Composite strain']
    elif "Compressive strain (Displacement)" in cols:
        strain_col = graph_df['Compressive strain (Displacement)']
    elif "Strain 1" in cols:
        strain_col = graph_df['Strain 1']
    
    graph_df.loc[:, 'Strain'] = strain_col

    # Record true stress and strain
    stress_col = graph_df['Stress']
    graph_df.loc[0, 'Stress (True)'] = stress_col[0]
    if args.tensile:
        graph_df.loc[1:, 'Stress (True)'] = stress_col[1:].astype(float) * (1 + strain_col[1:].astype(float))
    else:
        graph_df.loc[1:, 'Stress (True)'] = stress_col[1:].astype(float) * (1 - strain_col[1:].astype(float))
    graph_df.loc[0, 'Strain (True)'] = strain_col[0]
    graph_df.loc[1:, 'Strain (True)'] = np.log(strain_col[1:].astype(float) + 1)

    # Modulus calculation
    if not mod_range is None:
        num_idxs = len(stress_col)
        min_idx = max(int(mod_range[0] * num_idxs), 1)
        max_idx = int(mod_range[1] * num_idxs)

        stress_range = stress_col[min_idx:max_idx].astype(float)
        strain_range = strain_col[min_idx:max_idx].astype(float)
        
        m, b = np.polyfit(strain_range, stress_range, 1)

        mat_mods[mat_name] = m # Average slope over the range
        mat_bs[mat_name] = b
        print(f"Elastic Modulus: {mat_mods[mat_name]} {stress_col[0]}")

        # Make straight line slightly offset from elastic region and find where it intersects eng stress to get yield strength
        elastic_offset = (strain_col[1:].astype(float) - YIELD_OFFSET) * mat_mods[mat_name] + mat_bs[mat_name]
        graph_df['Offset'] = np.nan
        graph_df.loc[1:,'Offset'] = elastic_offset
        first_below = (graph_df['Stress'][1:].astype(float) - elastic_offset).lt(0.0).idxmax()
        yield_str = float(graph_df["Stress"][first_below-1])
        mat_yields[mat_name] = yield_str
        print(f"Yield Strength: {yield_str} {stress_col[0]}")

        num_strain = strain_col[1:].astype(float)
        num_stress = stress_col[1:].astype(float)
        integ_modresil = np.trapz(num_strain[:first_below-1], num_stress[:first_below-1])
        simple_modresil = (yield_str * num_strain[first_below-1]) / 2
        print(f"Modulus of Resilience (Integrated): {integ_modresil} {stress_col[0]}")
        print(f"Modulus of Resilience (Simple Triangle): {simple_modresil} {stress_col[0]}")

        mat_ultimates[mat_name] = max(graph_df['Stress'][1:].astype(float))
        print(f"Ultimate Strength: {mat_ultimates[mat_name]} {stress_col[0]}")

    # Power Law calculation
    if power_law:
        df = graph_df
        true_strain = df['Strain (True)'][1:].astype(float)
        true_stress = df['Stress (True)'][1:].astype(float)
        min_idx = int(pl_range[0] * len(true_strain))
        max_idx = int(pl_range[1] * len(true_strain))
        tstrain_log = np.log(true_strain)
        tstress_log = np.log(true_stress)
        n, log_k = np.polyfit(tstrain_log[min_idx:max_idx], tstress_log[min_idx:max_idx], 1)
        k = np.e**log_k
        print(f"Power law: K={k}, n={n}")
        mat_k[mat_name] = k
        mat_n[mat_name] = n

    # Greatest strain value:
    print(f"Maxmimum strain: {max(strain_col[1:].astype(float))} {strain_col[0]}")


    print(mat_name)
    print(graph_df)

    mat_dfs[mat_name] = graph_df
        





fig = plt.figure()
ax = plt.subplot()



strain_data = strain_col[1:].astype(float)
min_str = min([min(mat_dfs[mat_name].loc[1:,'Strain'].astype(float)) for mat_name in mat_dfs])
min_str = 0
max_str = max([max(mat_dfs[mat_name].loc[1:,'Strain'].astype(float)) for mat_name in mat_dfs])
str_range = max_str - min_str
num_labels = 4
label_freq = str_range / (num_labels)

for mat_name in mat_dfs:
    df = mat_dfs[mat_name]
    if args.range_estimation:
        strain = df['Strain'][1:].astype(float)
        stress = df['Stress'][1:].astype(float)
        stress_normalized = stress.copy()# / max(stress) * max(strain)
        timestamps = np.array([float(n)/float(len(strain)) for n in range(len(strain))])
        ax.plot(timestamps, strain, label=mat_name+" strain")
        ax.plot(timestamps, stress_normalized, label=mat_name+" strain")
    elif args.true_stress:
        strain = df['Strain'][1:].astype(float)
        stress = df['Stress'][1:].astype(float)
        ax.plot(strain, stress, label=mat_name+" (Eng)")
        ax.plot(df['Strain (True)'][1:].astype(float), df['Stress (True)'][1:].astype(float), label=mat_name+" (True)")
        #num_idxs = len(strain)
        #min_idx = int(mod_range[0] * num_idxs)
        #max_idx = int(mod_range[1] * num_idxs)
        # ax.plot(df['Strain'][min_idx:max_idx].astype(float), df['Strain'][min_idx:max_idx].astype(float) * mat_mods[mat_name], label=mat_name+" Slope")
        if not (mod_range is None): ax.plot(strain, df['Offset'][1:].astype(float), label=mat_name+" 2% offset yiel")
        # ax.plot([df['Strain'][max_idx]]*2, [0, max(df['Strain'][1:].astype(float) * mat_mods[mat_name])])
    elif graph_pl:
        true_strain = df['Strain (True)'][1:].astype(float)
        true_stress = df['Stress (True)'][1:].astype(float)
        min_idx = int(pl_range[0] * len(true_strain))
        max_idx = int(pl_range[1] * len(true_strain))
        # ax.loglog(true_strain[min_idx:max_idx], true_stress[min_idx:max_idx], label=mat_name)
        if pl_loglog:
            ax.set_xscale('log')
            ax.set_yscale('log')
        ax.plot(true_strain, true_stress, label=mat_name+" (True)")
        k = mat_k[mat_name]
        n = mat_n[mat_name]
        ax.plot(true_strain, k*np.float_power(true_strain, n), label=mat_name+" (power law approx)")
        ax.axis('tight')
    else:
        ax.plot(df['Strain'][1:].astype(float), df['Stress'][1:].astype(float), label=mat_name)

if not power_law:
    ax.set_xticks(np.append(np.arange(min_str, max_str, label_freq*1.01), max_str))
ax.set_xlabel("Strain (mm/mm)")
ax.set_ylabel("Stress (kPa)")

fig.legend()
fig.set_label("Stress vs strain of uh idk actually")
plt.show()

