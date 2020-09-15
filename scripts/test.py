import pandas as pd
from datetime import datetime

# Just some test code to run on tesla. Checking to see runtimes on different db operations

colnames = ['run', 'tick', 'lifestate', 'total_ixodes']
csv_file = "/home/hdenny2/plotting-code/data/host/host-density.2020.Sep.02.hab07"
before = datetime.now()
# df = pd.read_csv(csv_file, names=colnames, error_bad_lines=False, dtype={'run':np.int32, 'tick':np.float, 'lifestate':str, 'total_ixodes':str})
df = pd.read_csv(csv_file, skiprows=8, names=colnames, header=None, error_bad_lines=False)
after = datetime.now()
print("Read_csv runtime: ", after-before)
# Reading csv takes ~15-30s
#

# print("dropping cols...")
# df.drop(['tick', 'lifestate'], axis=1, inplace=True)

print("Max before filtering...", df['tick'].max())

print("Removing bad lines...")
before = datetime.now()
new_df = df[df['tick'] < 451]
after = datetime.now()
print("Filter runtime: ", after-before)

print("Max after filtering...", new_df['tick'].max())

print(new_df.head())

# before = datetime.now()
# new_df = df[df['tick'] > 1000000]
# after = datetime.now()
# print("Filter df runtime: ", after-before)
# print(df.head())