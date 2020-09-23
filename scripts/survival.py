import csv
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


# Hillari Denny
# Original Date: 2/18/2020
# Last update: 9/3/2020 - This code is deprecated. See clean_data.py and plot_data.py for current version
# This code still serves as a good reference so I'll let it stay for now.

# This script creates parameter mappings, groups the data frames appropriately, handles categoricals, and creates
# the plots that represent Ixode habitat-suitability

# TODO
# - Clean up, archive, and remove from repo
# - refactor the directory looping functionality
# -


# -- parameter mapping -- #
# The following two functions use dictionary comprehension + lambdas to create a mapping with value as lists or strings
def map_params_as_string(paramfile):
    with open(paramfile, 'r') as file:
        reader = csv.reader(file)
        param_str = {rows[0]: "Lifestage: {}\nHost Density: {}\nIxode Count: {}\nHabitat Suitability: {}".format(
            rows[2], rows[3], rows[4], rows[5]) for rows in reader}
    return param_str


def map_params_as_list(paramfile):
    with open(paramfile, 'r') as file:
        reader = csv.reader(file)
        param_list = {rows[0]: [rows[2], rows[3], rows[4], rows[5]] for rows in reader}
    return param_list


def plot_runs(paramsfile, datafile):
    paramdict = map_params_as_string(paramsfile)
    data = pd.read_csv(datafile)
    postfix = 1
    for run in data.groupby('run'):
        params = paramdict[str(run[0])]  # gets the parameters of the current run we're iterating over
        df = run[1]
        df = df[df.Lifestate != "egg"]  # we don't want to plot 'egg' lifestate
        newdf = df.drop(["Lat", "Long", "habitat_sample", "run"], axis=1)
        matplotlib.use('Qt5Agg')  # force matplotlib specified backend (may need to change depending on OS)

        # -- handling categorical lifestates -- #
        dummies_df = pd.get_dummies(newdf, columns=['Lifestate'])
        grouped = dummies_df.groupby('tick')

        # -- Creating plots -- #
        fig, ax = plt.subplots(figsize=(12, 7))
        grouped.sum().plot(logy=False, ax=ax)
        ax.set_title("Survivability", fontsize=16, fontweight='bold')
        # ax.set_title(params, fontsize=10, horizontal alignment='left', loc='left')
        ax.set_xlabel("Days", fontsize=12)
        ax.set_ylabel("Lifestate count", fontsize=12)
        props = dict(facecolor='wheat', alpha=0.5)
        # ax.text(0.05, 0.95, params, fontsize=10, bbox=props, transform=ax.transAxes)
        plt.figtext(0.76, 0.9, params, horizontalalignment='left', bbox=props)
        plt.show()
        fig.savefig('data/plots/testplot' + str(postfix) + '.png')
        postfix += 1

# -- Loop thorough directory and look for batch param map files -- #
# for file in os.listdir("data/param-files/"):
#     if "map" in file:
#         # print("FILE: ", file)
#         param_dict = map_params("data/param-files/" + file)
#         #TODO get postfix and look for corresponding run file, pass dict and file to plot_runs()


def plot_survivability(directory):
    for paramfile in os.listdir(directory): # file is a str
        postfix = paramfile[-2:]
        if "map" in paramfile: # we have a parameter mapping
            for datafile in os.listdir(directory):
                if postfix in datafile and "map" not in datafile: # we have corresponding batch file
                    plot_runs(paramfile, datafile)
        else:
            print("Fix this function. Do try/catch and maybe don't double loop.")


paramfile = "data/failures/instance_4/TickNonAgg.2020.Apr.07.batch_param_map.21_20_27"
runfile = "data/failures/instance_4/TickNonAgg.2020.Apr.07.21_20_27"

plot_runs(paramfile, runfile)
