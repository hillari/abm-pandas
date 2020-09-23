# Hillari M Denny
# 9/23/2020

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
from datetime import datetime
import numpy as np
import argparse

# TODO
# - Verbosity flag + conditional prints
# - Modify skiplines in agg_plots.py (~13)


parser = argparse.ArgumentParser()
# parser.add_argument('-test', action='store_true')
# parser.add_argument('paramfile')
# parser.add_argument('csvfile')

# outliers argument, could give it a list of options so user can pass the threshold
parser.add_argument('-outliers', action='store_true', help="Remove outliers (runs that didn't make it past 90 days)")
parser.add_argument('-type', choices=['habitat', 'host'], required=True)
parser.add_argument('-first', action='store_true')
args = parser.parse_args()


def get_args():
    if args.type == 'habitat':
        dict_index = 8
        constant_index = 4
        plot_type = 'habitat_suitability'
        constant = 'host_density'
    else:
        dict_index = 4
        constant_index = 8
        plot_type = 'host_density'
        constant = 'habitat_suitability'
    return dict_index, constant_index, plot_type, constant


def get_params(paramfile, dict_index, constant_index):
    # get paramfile and make dict
    # Create a dictionary that maps the run#  { run#: host_density/habitat_suitability }
    paramfile = paramfile
    param_dict = {}
    with open(paramfile, 'r') as file:
        for line in file:
            result = line.replace("\t", ",").replace('\n', '').split(',')
            # { run#: host_density/habitat_suitability }
            try:
                param_dict[int(result[0])].append(float(result[dict_index]), float(result[constant_index]))
            except KeyError:
                param_dict[int(result[0])] = (float(result[dict_index]), float(result[constant_index]))
    # for k, v in param_dict.items():
    #     print(k, v)
    return param_dict


def get_datafile(csvfile):
    # read the csv, return resulting df
    colnames = ['run', 'tick', 'lifestate', 'total_ixodes']
    csv_file = csvfile
    print("Reading csv file...")
    before = datetime.now()
    df = pd.read_csv(csv_file, skiprows=1, names=colnames, error_bad_lines=False)
    after = datetime.now()
    print("read_csv() runtime: ", after - before)
    print(df.head())
    return df


def clean_data(raw_df):
    # filter bad lines
    # returns df
    df = raw_df  # ...Because if we have arg = df and return = df...? check this
    print("Filtering database...")
    before = datetime.now()
    # print("Max before filtering...", df['tick'].max())
    df = df[df['tick'] < 451]
    after = datetime.now()
    print("Filtering runtime: ", after - before)
    # print("Max after filtering...", df['tick'].max())
    return df


def build_df(clean_df, paramfile, constant, dict_index, constant_index):
    # aggregate, parse paramfile and map, make final agg df w/std
    param_dict = get_params(paramfile, dict_index, constant_index)
    print("Building df...")
    before = datetime.now()
    n_ticks_df = clean_df.groupby(['run'], as_index=False)
    n_ticks_df = n_ticks_df.agg({'total_ixodes': 'nunique', 'tick': 'max'})

    # TODO log params for outlier runs
    if args.outliers:
        n_ticks_df = n_ticks_df[n_ticks_df['tick'] > 90]

    # get the parameter mappings and add to df
    for key, value in param_dict.items():
        n_ticks_df.loc[n_ticks_df['run'] == key, 'host_density'] = float(value[0])

    final_df = n_ticks_df.groupby('host_density')['total_ixodes'].agg({'mean', 'std'})
    final_df[constant] = param_dict[1][1]  # add constant param so we can later groupby and plot multiple curves
    after = datetime.now()
    print("Build df runtime: ", after - before)
    return final_df


def write_df(final_df):
    # writes or appends df to file
    # no return val
    if args.first:
        writemode = 'w'
        header = True
    else:
        writemode = 'a'
        header = False

    # TODO get current dir
    final_df.to_csv('/home/hdenny2/plotting-code/data/host/final/host-aggregated_data_sans_outliers', mode=writemode, header=header)


def main():
    # Specify hard-coded files for testing here
    paramfile = "/home/hdenny2/plotting-code/data/host/final/host-params_hab01"
    csvfile = "/home/hdenny2/plotting-code/data/host/final/host-density.2020.Sep.07hab01"

    dict_index, constant_index, plot_type, constant_str = get_args()

    raw_df = get_datafile(csvfile)
    clean_df = clean_data(raw_df)
    final_df = build_df(clean_df, paramfile, constant_str, dict_index, constant_index)
    write_df(final_df)


if __name__ == "__main__":
    main()




