import pandas as pd
import csv
# Hillari M Denny
# 4/12/2020

# -----------------------------------------------
# This script is intended to help debug failed batch runs for the tick ABM.
# It gets the parameter mapping, finds the last run in the batch file, and prints
# the parameters for each run to a file.
# NOTE: this script makes the assumption that the last run is the one that failed.
# -----------------------------------------------

# Get the parameter mapping
instance = 8
datafile = "server-dump/instance_8/paramSweep.2020.Feb.21.batch_param_map.09_18_06"
with open(datafile, 'r') as file:
    reader = csv.reader(file)
    mydict = {rows[0]: "Lifestage: {}\n Host Density: {}\n Ixode Count: {}\n Habitat Suitability: {}".format(
        rows[1], rows[2], rows[3], rows[4], rows[5]) for rows in reader}

data = pd.read_csv("server-dump/instance_8/paramSweep.2020.Feb.21.09_18_06")
byrun = data.groupby('run')


# Iterate over key and value, write to a file
with open('server-dump/FEB24-failures-out.txt', 'a') as f:
    print("------------------------------------------", file=f)
    print("INSTANCE " + str(instance), file=f)
    print("FAILURE ON RUN {}\n{}".format(data['run'].max(), mydict.get(str(data['run'].max()))), file=f)
    print("------------------------------------------", file=f)
    for k, v in mydict.items():
        print("********\nRun {}:\n {}".format(k, v), file=f)
        for group in byrun:
            # parameters = mydict[str(group[0])]

            if int(k) == group[0]:
                df = group[1]
                print("Run {} made it {} 'days'".format(group[0], df['tick'].max()), file=f)
                print(df['Lifestate'].value_counts().to_dict(), file=f)
