import pandas as pd
import argparse
from datetime import datetime


parser = argparse.ArgumentParser()
# parser.add_argument('-test', action='store_true')
# parser.add_argument('paramfile')
# parser.add_argument('csvfile')

# outliers argument, could give it a list of options so user can pass the threshold
parser.add_argument('-outliers', action='store_true', help="Remove outliers (runs that didn't make it past 90 days)")
parser.add_argument('-type', choices=['habitat', 'host'], required=True)
parser.add_argument('-first', action='store_true')
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
    for k, v in param_dict.items():
        print(k, v)
        return param_dict


def get_datafile(csvfile):
    # read the csv, return resulting df
    colnames = ['run', 'tick', 'lifestate', 'total_ixodes']
    csv_file = csvfile
    if args.skip:
        nlines = args.skip
    else:
        nlines = 1
    print("Reading csv file...")
    print("Skipping {} lines".format(nlines))
    before = datetime.now()
    df = pd.read_csv(csv_file, skiprows=nlines, names=colnames, error_bad_lines=False)
    after = datetime.now()
    print("read_csv() runtime: ", after - before)
    # print(df.head())
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


# NEW CODE --
# TODO rename functions and vars
def group_df(clean_df):
    agg_df = clean_df.groupby(['run'], as_index=False)
    agg_df = agg_df.agg({'total_ixodes': 'nunique', 'tick': 'max'})
    return agg_df


def filter_outliers(agg_df):
    # If we are handling outliers, we need two separate data frames
    agg_df = agg_df[agg_df['tick'] > 89]
    histogram_df = agg_df[agg_df['tick'] < 91]
    return agg_df, histogram_df


# Pass the filtered/cleaned df
# Can we pass a list of dfs so we don't need to call this twice when we're doing outliters?
def map_params(dataframe, paramfile, dict_index, constant_index, constant, plot_type):
    param_dict = get_params(paramfile, dict_index, constant_index)
    # get the parameter mappings and add to df
    for key, value in param_dict.items():
        dataframe.loc[dataframe['run'] == key, plot_type] = float(value[0])
    dataframe[constant] = param_dict[1][1]
    print(dataframe.head())


# def build_lineplot_df(agg_df, paramfile, constant, dict_index, constant_index):
#
#
#
#


def write_df(final_df):
    if args.first:
        writemode = 'w'
        header = True
    else:
        writemode = 'a'
        header = False
    final_df.to_csv('/media/hill/DATA-LINUX/abm-data/host-density-olderruns/new-model/aggregate-runs/test_hist_df')


def main():
    paramfile = '/media/hill/DATA-LINUX/abm-data/host-density-olderruns/new-model/aggregate-runs/params_05habitat'
    csvfile = '/media/hill/DATA-LINUX/abm-data/host-density-olderruns/new-model/aggregate-runs/density-new.2020.Jul.11_hab05'
    dict_index, constant_index, plot_type, constant_str = get_args()
    # get_params(paramfile, dict_index, constant_index)

    raw_df = get_datafile(csvfile)
    clean_df = clean_data(raw_df)
    df = group_df(clean_df)

    if args.outliers:
        agg_df, histogram_df = filter_outliers(df)
        map_params(agg_df, paramfile, dict_index, constant_index, plot_type, constant_str)
    else:
        map_params(df, paramfile, dict_index, constant_index, plot_type, constant_str)


if __name__ == "__main__":
    main()

