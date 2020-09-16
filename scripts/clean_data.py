import pandas as pd
import matplotlib
# matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import csv
from datetime import datetime
import numpy as np
import argparse

# TODO
# - remove outliers for cumulative ixodes (make OPTIONAL argparse for this, threshold argument?)


parser = argparse.ArgumentParser()
# parser.add_argument('-test', action='store_true')
# parser.add_argument('paramfile')
# parser.add_argument('csvfile')
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
    # Create a dictionary that maps the run# to host_density { run#: host_density }
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
    before = datetime.now()
    df = pd.read_csv(csv_file, skiprows=8, names=colnames, error_bad_lines=False)
    after = datetime.now()
    print("read_csv() runtime: ", after - before)
    return df


def clean_data(raw_df):
    # TODO option to remove outliers here
    # filter bad lines
    # returns df
    df = raw_df  # ? Because if we have arg = df and return df...?
    print("Filtering database...")
    before = datetime.now()
    print("Max before filtering...", df['tick'].max())
    df = df[df['tick'] < 451]
    after = datetime.now()
    print("Filtering runtime: ", after - before)
    print("Max after filtering...", df['tick'].max())
    return df


def build_df(clean_df, paramfile, constant, dict_index, constant_index):
    # aggregate, parse paramfile and map, make final agg df w/std

    param_dict = get_params(paramfile, dict_index, constant_index)
    print("Building df...")
    before = datetime.now()
    n_ticks_df = clean_df.groupby(['run'], as_index=False)
    n_ticks_df = n_ticks_df.agg({'total_ixodes': 'nunique'})

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

    # TODO get current dir, change filename
    final_df.to_csv('/media/hill/DATA-LINUX/abm-data/host-density-olderruns/new-model/aggregate-runs/adddf', mode=writemode, header=header)


def main():
    # Specify hard-coded files for testing here
    paramfile = "/media/hill/DATA-LINUX/abm-data/host-density-olderruns/new-model/aggregate-runs/params_09habitat"
    csvfile = "/media/hill/DATA-LINUX/abm-data/host-density-olderruns/new-model/aggregate-runs/density-new.2020.Jul.11hab_09"

    dict_index, constant_index, plot_type, constant_str = get_args()

    raw_df = get_datafile(csvfile)
    clean_df = clean_data(raw_df)
    final_df = build_df(clean_df, paramfile, constant_str, dict_index, constant_index)
    write_df(final_df)


if __name__ == "__main__":
    main()



