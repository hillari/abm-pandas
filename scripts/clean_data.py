import pandas as pd
import matplotlib.pyplot as plt
import csv
from datetime import datetime
import numpy as np
import argparse

# Hillari M Denny
# Last update: 10/02/2020
# This file processes Repast file sinks and outputs a dataframe with aggregated results

# TODO
# - Verbosity flag + conditional prints
# - Add logging for outliers (this is currently a separate python file)


parser = argparse.ArgumentParser()
# parser.add_argument('-test', action='store_true')
# parser.add_argument('paramfile')
# parser.add_argument('csvfile')

parser.add_argument('-outliers', action='store_true', help="Remove outliers (runs that didn't make it past 90 days)")
parser.add_argument('-type', choices=['habitat', 'host'], required=True)
parser.add_argument('-first', action='store_true', help="This flag triggers writemode to be ('w'),"
                                                        "otherwise we write in append mode ('a')")
parser.add_argument('-skip', type=int, action='store', help="First n lines to skip in file sink")
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
    # get paramfile and build dictionary that maps the run#  { run#: host_density/habitat_suitability }
    paramfile = paramfile
    param_dict = {}
    with open(paramfile, 'r') as file:
        for line in file:
            result = line.replace("\t", ",").replace('\n', '').split(',')
            try:
                # { run#: host_density/habitat_suitability, host_density/habitat_suitability }
                # { run#: plot_type, constant param }
                param_dict[int(result[0])].append(float(result[dict_index]), float(result[constant_index]))
            except KeyError:
                param_dict[int(result[0])] = (float(result[dict_index]), float(result[constant_index]))
    # print("Initial paramdict:")
    # for k, v in param_dict.items():
    #     print(k, v)
    return param_dict


def get_datafile(csvfile, nlines):
    # read the csv, return resulting df
    colnames = ['run', 'tick', 'lifestate', 'total_ixodes']
    # if args.skip:
    #     nlines = args.skip
    # else:
    #     nlines = 1
    print("Reading csv file...")
    print("Skipping {} lines".format(nlines))
    before = datetime.now()
    df = pd.read_csv(csvfile, skiprows=nlines, names=colnames, error_bad_lines=False, warn_bad_lines=True)
    after = datetime.now()
    print("read_csv() runtime: ", after - before)
    # print(df.head())
    return df


def clean_data(raw_df):
    # filter bad lines
    # returns df
    df = raw_df
    print("Filtering database...")
    before = datetime.now()
    # print("Max before filtering...", df['tick'].max())
    df = df[df['tick'] < 451]
    after = datetime.now()
    print("Filtering runtime: ", after - before)
    # print("Max after filtering...", df['tick'].max())
    return df


def build_df(clean_df, paramfile, dict_index, constant_index, plot_type, constant):
    # aggregate, parse paramfile and map, make final agg df w/std and mean of total ixodes
    param_dict = get_params(paramfile, dict_index, constant_index)
    print("Building df...")
    before = datetime.now()
    n_ticks_df = clean_df.groupby(['run'], as_index=False)
    n_ticks_df = n_ticks_df.agg({'total_ixodes': 'nunique', 'tick': 'max'})

    if args.outliers:
        n_ticks_df = n_ticks_df[n_ticks_df['tick'] > 89]

    # get the parameter mappings and add to df
    for key, value in param_dict.items():
        n_ticks_df.loc[n_ticks_df['run'] == key, plot_type] = float(value[0])

    final_df = n_ticks_df.groupby(plot_type)['total_ixodes'].agg({'mean', 'std'}) # FIXME to_csv swaps these but only sometimes?!
    # add constant param so we can later groupby and plot multiple curves
    final_df[constant] = param_dict[1][1]
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
    # writemode = 'a'
    # header = False

    # TODO add filename as arg eg filename=plot_type+datetime
    final_df.to_csv('/home/hdenny2/plotting-code/data/host/final/agg-host-df', mode=writemode,
                    header=header)


def main():
    dict_index, constant_index, plot_type, constant_str = get_args()

    # # ------ Method to process one file sink at a time ------
    # paramfile = "/home/hdenny2/plotting-code/data/habitat/final/habitat-params_host3"
    # csvfile = "/home/hdenny2/plotting-code/data/habitat/final/habitat-suitability.2020.Sep.08host3"
    #
    # raw_df = get_datafile(csvfile)
    # clean_df = clean_data(raw_df)
    # final_df = build_df(clean_df, paramfile, dict_index, constant_index, plot_type, constant_str)
    # write_df(final_df)
    # # ------

    # Another method of getting results with a conditional on file sink format (Archive this)
    # if args.skip and args.skip > 1:
    #     clean_df = clean_data(raw_df)
    #     final_df = build_df(clean_df, paramfile, dict_index, constant_index, plot_type, constant_str)
    # else:
    #     final_df = build_df(raw_df, paramfile, dict_index, constant_index, plot_type, constant_str)
    # write_df(final_df)
    # # ------

# ---- Method to process a group of file sinks in one run ---
    # {paramfile: (csvfile, skiplines }
    habitat_filedict = {'habitat-params_host1': ('habitat-suitability.2020.Sep.08host1', 1),
                        'habitat-params_host3': ('habitat-suitability.2020.Sep.08host3', 13),
                        'habitat-params_host5': ('habitat-suitability.2020.Sep.08host5', 1),
                        'habitat-params_host7': ('habitat-suitability.2020.Sep.08host7', 1),
                        'habitat-params_host9': ('habitat-suitability.2020.Sep.15host9', 1)
                        }

    host_filedict = {'host-params_hab01': ('host-density.2020.Sep.07hab01', 1),
                     'host-params_hab03': ('host-density.2020.Sep.07hab03', 13),
                     'host-params_hab05': ('host-density.2020.Sep.07hab05', 1),
                     'host-params_hab07': ('host-density.2020.Sep.15hab07', 13),
                     'host-params_hab09': ('host-density.2020.Sep.07hab09', 1)
                     }

    for param, file_sink in habitat_filedict.items():
        abs_csv_path = "/home/hdenny2/plotting-code/data/habitat/final/" + file_sink[0]
        abs_param_path = "/home/hdenny2/plotting-code/data/habitat/final/" + param
        raw_df = get_datafile(abs_csv_path, file_sink[1])
        clean_df = clean_data(raw_df)
        final_df = build_df(clean_df, abs_param_path, dict_index, constant_index, plot_type, constant_str)
        write_df(final_df)
# -------


if __name__ == "__main__":
    main()
