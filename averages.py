import pandas as pd
import numpy as np
import argparse

## Grab the file name
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filepath', help="The txt file to read")
args = parser.parse_args()
fpath:list = args.filepath


group_df = pd.read_table(fpath).replace(0.0, np.nan)
print(group_df)

print('-'*40)
print('mean')
print(group_df.mean())

print('-'*40)
print('median')
print(group_df.median())

print('-'*40)
print('std')
stds = group_df.std()
print(stds)