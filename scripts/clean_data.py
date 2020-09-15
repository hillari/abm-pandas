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
# - specify write directory


parser = argparse.ArgumentParser()
# parser.add_argument('-test', action='store_true')
# parser.add_argument('paramfile')
# parser.add_argument('csvfile')
parser.add_argument('-type', choices=['habitat', 'host'], required=True)
parser.add_argument('-first', action='store_true')
args = parser.parse_args()


def get_args():
    # FIXME don't need plot stuff. Could do constant here
    if args.type == 'habitat':
        dict_index = 8
        constant = 4
        plot_type = 'habitat_suitability'
        # x_label = "Habitat Suitability "
        # plot_title = "Aggregated Habitat Suitability"
        # plot_legend = "Host Density: "
    else:
        dict_index = 4
        plot_type = 'host_density'
        constant = 8
        # x_label = "Host Density "
        # plot_title = "Aggregated Host Density"
        # plot_legend = "Habitat Suitability: "
    return dict_index, plot_type, constant


def get_params(paramfile):
    # get paramfile and make dict
    # Create a dictionary that maps the run# to host_density { run#: host_density }
    dict_index, _, constant = get_args()
    # paramfile = "/media/hill/DATA-LINUX/abm-data/host-density/testparams1hab7"
    paramfile = paramfile
    param_dict = {}
    with open(paramfile, 'r') as file:
        for line in file:
            result = line.replace("\t", ",").replace('\n', '').split(',')

            # # hacky b/c we need to pass the index as an arg but lets try...
            # constant_param = result[8]

            # attempt to add the density value to run, if it doesn't exist, create it
            try:
                param_dict[int(result[0])].append((float(result[4])))
            except KeyError:
                param_dict[int(result[0])] = (float(result[4]))  # { run#: host_density }

    # for k, v in paramd.items():
    #     print(k, v)
    return param_dict, constant


def get_datafile(csvfile):
    # read the csv, return resulting df
    colnames = ['run', 'tick', 'lifestate', 'total_ixodes']
    # csv_file = "/media/hill/DATA-LINUX/abm-data/host-density/testdf3-badlines"
    csv_file = csvfile
    before = datetime.now()
    df = pd.read_csv(csv_file, skiprows=8, names=colnames, error_bad_lines=False)
    after = datetime.now()
    print("read_csv() runtime: ", after - before)

    return df


def clean_data(data):
    # filter bad lines
    # drop if necessary (prob not)
    # returns df
    df = data # ? Because if we have arg = df and return df...?
    print("Filtering database...")
    before = datetime.now()
    print("Max before filtering...", df['tick'].max())
    df = df[df['tick'] < 451]
    after = datetime.now()
    print("Filtering runtime: ", after - before)
    print("Max after filtering...", df['tick'].max())

    return df


def build_df(data, paramfile):
    # aggregate, parse paramfile and map, make final agg df w/std
    # returns df
    # TODO ? make this call get_params instead of passing it? since we need so much from args anyway

    param_dict, constant = get_params(paramfile)

    print("Building df...")
    before = datetime.now()
    n_ticks_df = data.groupby(['run'], as_index=False)
    n_ticks_df = n_ticks_df.agg({'total_ixodes': 'nunique'})

    # get the parameter mappings and add to df
    for key, value in param_dict.items():
        n_ticks_df.loc[n_ticks_df['run'] == key, 'host_density'] = float(value)
        # n_ticks_df[]

    print("n_ticks_db ")
    print(n_ticks_df.head())

    final_df = n_ticks_df.groupby('host_density')['total_ixodes'].agg({'mean', 'std'})

    after = datetime.now()
    print("Build df runtime: ", after - before)

    return final_df


def write_df(final_df):
    # writes or appends df to file
    # no return val
    if args.first:
        writemode = 'w'
    else:
        writemode = 'a'

    # TODO get current dir, chagne filename
    final_df.to_csv('/media/hill/DATA-LINUX/abm-data/host-density-olderruns/new-model/aggregate-runs/adddf', mode=writemode)


def main():
    # Specify hard-coded files for testing here
    paramfile = "/media/hill/DATA-LINUX/abm-data/host-density-olderruns/new-model/aggregate-runs/params_05habitat"
    csvfile = "/media/hill/DATA-LINUX/abm-data/host-density-olderruns/new-model/aggregate-runs/density-new.2020.Jul.11_hab05"

    df = get_datafile(csvfile)
    clean_df = clean_data(df)
    final_df = build_df(clean_df, paramfile)
    write_df(final_df)


if __name__ == "__main__":
    main()




