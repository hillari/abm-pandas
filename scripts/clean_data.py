import pandas as pd
import matplotlib
# matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import csv
from datetime import datetime
import numpy as np
import argparse

# TODO
# - get the constant and add to final_df


parser = argparse.ArgumentParser()
# parser.add_argument('-test', action='store_true')
parser.add_argument('paramfile')
parser.add_argument('csvfile')
parser.add_argument('-type', choices=['habitat', 'host'], required=True)
parser.add_argument('-first', action='store_true')
args = parser.parse_args()


def get_args():
    if args.plot == 'habitat':
        dict_index = 8
        plot_type = 'habitat_suitability'
        x_label = "Habitat Suitability "
        plot_title = "Aggregated Habitat Suitability"
        plot_legend = "Host Density: "
    else:
        dict_index = 4
        plot_type = 'host_density'
        x_label = "Host Density "
        plot_title = "Aggregated Host Density"
        plot_legend = "Habitat Suitability: "
    return dict_index, plot_type, x_label, plot_title, plot_legend


def get_params(paramfile):
    # get paramfile and make dict
    # Create a dictionary that maps the run# to host_density { run#: host_density }
    dict_index, _, _, _, _ = get_args()
    # paramfile = "/media/hill/DATA-LINUX/abm-data/host-density/testparams1hab7"
    paramfile = paramfile
    param_dict = {}
    with open(paramfile, 'r') as file:
        for line in file:
            result = line.replace("\t", ",").replace('\n', '').split(',')

            # attempt to add the density value to run, if it doesn't exist, create it
            try:
                param_dict[int(result[0])].append((float(result[4])))
            except KeyError:
                param_dict[int(result[0])] = (float(result[4]))  # { run#: host_density }

    # for k, v in paramd.items():
    #     print(k, v)
    return param_dict


def get_datafile(csvfile):
    # read the csv
    colnames = ['run', 'tick', 'lifestate', 'total_ixodes']
    # csv_file = "/media/hill/DATA-LINUX/abm-data/host-density/testdf3-badlines"
    csv_file = csvfile
    before = datetime.now()
    df = pd.read_csv(csv_file, skiprows=8, names=colnames, error_bad_lines=False)
    after = datetime.now()
    print("Run time: ", after - before)

    return df


def clean_data(data):
    # filter bad lines
    # drop if necessary (prob not)
    # returns df
    df = data # ? does this use resources
    print("Filtering database...")
    before = datetime.now()
    print("Max before filtering...", df['tick'].max())
    df = df[df['tick'] < 451]
    after = datetime.now()
    print("Filtering runtime: ", after - before)
    print("Max after filtering...", df['tick'].max())

    return df


def build_df(data, paramd):
    # aggregate, parse paramfile and map, make final agg df w/std
    #  returns df

    print("Groupby and agg...")
    before = datetime.now()
    n_ticks_df = data.groupby(['run'], as_index=False)
    n_ticks_df = n_ticks_df.agg({'total_ixodes': 'nunique'})
    after = datetime.now()
    print("Groupby runtime: ", after - before)

    for key, value in paramd.items():
        n_ticks_df.loc[n_ticks_df['run'] == key, 'host_density'] = float(value)

    final_df = n_ticks_df.groupby('host_density')['total_ixodes'].agg({'mean', 'std'})

    return final_df


def write_df(df):
    # writes or appends df to file
    # no return val
    if args.first:
        writemode='w'
    else:
        writemode='a'

    df.to_csv('/media/hill/DATA-LINUX/abm-data/host-density-olderruns/new-model/aggregate-runs/dfagg', mode=writemode)


def main():
    param_file = get_params(args.paramfile)




if __name__ == "__main__":
    main()




