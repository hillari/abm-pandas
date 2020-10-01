import pandas as pd
import matplotlib
matplotlib.use('Agg')  # to run the script on remote server, otherwise it will try to use xwindows backend
import matplotlib.pyplot as plt
import argparse
from datetime import datetime

# Hillari Denny
# Last update: 9/30/2020
# This code is a deprecated version of clean_data.py and plot_data.py
#
# Usage: python3 ./aggregate_plots.py <paramfile> <csvfile> -plot <plot type> [-popup] [-root <directory>]
#
# The -popup option is for local use and allows a plot to be shown without automatically saving it. If this option
# is ommitted, the plot is saved to a hard-coded location
#

# TODO: cleanup, archive

# --- Argparse ---

parser = argparse.ArgumentParser()
parser.add_argument('-test', action='store_true')
parser.add_argument('-two', action='store_true')
parser.add_argument('-popup', action='store_true')
parser.add_argument('-plot', choices=['habitat', 'host'], required=True)
args = parser.parse_args()

# FOR REMOTE:
# single plot
param_file = ""
csv_file = ""

# double plot
param_file1 = "/home/hdenny2/plotting-code/data/host/params-Sept2-hab05"
csv_file1 = "/home/hdenny2/plotting-code/data/host/host-density.2020.Sep.02.hab05"
param_file2 = "/home/hdenny2/plotting-code/data/host/params-Sept2-hab07"
csv_file2 = "/home/hdenny2/plotting-code/data/host/host-density.2020.Sep.02.hab07"

# FOR LOCAL:
# #TODO update these
# testparam1 = "/media/hill/DATA-LINUX/abm-data/host-density/testparams"
# testdf1 = "/media/hill/DATA-LINUX/abm-data/host-density/testdf-agg"
# testparam2 = "/media/hill/DATA-LINUX/abm-data/host-density/testparams2"
# testdf2 = "/media/hill/DATA-LINUX/abm-data/host-density/testdf-agg2"


def get_args():
    # This function uses argparse to tell help generalize plot creation

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


def build_dictionaries(paramfile, csvfile):
    """
    Parses param file to create a dictionary that maps the run# to <plot_type> like so - { run#: <plot_type> }
    :param paramfile: the parameter file to be parsed
    :param csvfile: the repast file sink
    :return paramd, ixodes_count_dict: parameter dictionary and cumulative ixodes dictionary
    """
    dict_index, _, _, _, _ = get_args()
    print("Creating dictionaries...")
    print("THE DICTIONARY INDEX IS: ", dict_index)
    paramd = {}
    with open(paramfile, 'r') as file:
        for line in file:
            result = line.replace("\t", ",").replace('\n', '').split(',')
            constant = str(result[8])  # for habitat plots, use 4. For host density, 8
            # print("result is ", result)
            # attempt to add the value to run, if it doesn't exist, create it
            try:
                paramd[int(result[0])].append(float(result[dict_index]))
            except KeyError:
                paramd[int(result[0])] = float(result[dict_index])  # { run#: <plot_type> }
    # print("PARAM dictionary: ")
    # for k, v in paramd.items():
    #     print(k, v)

    # Make a dictionary that maps the run# to total ixodes { run#: cumulative_ixodes }
    ixodes_count_dict = {}
    # TODO ideally, we add a check for column names at top of file due to Repast file sink inconsistencies
    colnames = ['run', 'tick', 'lifestate', 'name']
    print("Creating initial data frame...")
    df = pd.read_csv(csvfile, names=colnames, error_bad_lines=False)
    print("DONE creating initial data frame.")
    print(df.head())
    for run in df.groupby('run'):
        current_df = run[1]
        ixodes_count_dict[run[0]] = len(current_df['name'].unique())

    # print("ixodes count dict:\n")
    # for k, v in ixodes_count_dict.items():
    #     print(k, v)
    return paramd, ixodes_count_dict, constant


# This function builds the dataframes we need for plotting and returns the final df
def build_dataframe(ixodesdict, paramdict):

    _, plot_type, _, _, _ = get_args()
    print("Building additional dataframes...")
    # Creating a data frame from the ixodes_count dict
    df_final = pd.DataFrame(ixodesdict.items(), columns=['run', 'total_ixodes'])
    df_final[plot_type] = 0

    # Iterate through param dictionary and add the value to associated run
    for key, value in paramdict.items():
        for i in range(len(paramdict)):
            df_final.loc[df_final['run'] == key, plot_type] = value

    # Now we have a df with | 'run' | 'total_ixode' | '<plot_type>' |
    # Create a dictionary with { <plot_type>: agg_ixodes }
    agg_ixodes_dict = {}
    for density in df_final.groupby(plot_type):
        tmp_df = density[1]  # density is a tuple, so density[1] holds the df we want
        agg_ixodes_dict[density[0]] = tmp_df['total_ixodes'].agg('mean')

    print("AGG_IXODES dict:")
    for k, v in agg_ixodes_dict.items():
        print(k, "-", v)

    # Create a dataframe from the agg_ixodes_dict which we will use to plot
    df_agg_final = pd.DataFrame(agg_ixodes_dict.items(), columns=[plot_type, 'agg_ixodes'])
    print(df_agg_final.head())
    print("DONE building dataframe.")
    return df_agg_final


def plot_two(df1, df2, constant1, constant2):
    _, plot_type, x_label, plot_title, legend = get_args()
    # matplotlib.use('Qt5Agg')
    ax = df1.plot(x=plot_type, y='agg_ixodes', label=legend + constant1)
    ax.set_title(plot_title)
    ax.set_ylabel("Total Ixodes")
    ax.set_xlabel(x_label)
    # Options to add text to the plot

    # props = dict(facecolor='wheat', alpha=0.5)
    # params = 'Lifestage: adult\nStarting Ixodes: 10\nHabitat Suitability: 0.05'
    # ax.text(0.05, 21, s=params, bbox=props)
    df2.plot(ax=ax, x=plot_type, y='agg_ixodes', label=legend + constant2)
    # plt.show(block=True)
    dt = datetime.now()
    plot_filename = plot_type + dt.strftime("_%d-%b-%y-%H-%M") + ".png"
    server_path = "/home/hdenny2/plotting-code/data/"
    plt.savefig(server_path + plot_filename)


def plot_df(finaldf):

    _, plot_type, x_label, plot_title, legend = get_args()
    print("Plotting data...")
    plt.ylabel("Cumulative Ixodes")
    plt.xlabel(x_label)
    plt.title(plot_title)
    plt.plot(finaldf[plot_type], finaldf['agg_ixodes'], marker='o')
    # plt.show(block=True)
    dt = datetime.now()
    plot_filename = plot_type + dt.strftime("_%d-%b-%y-%H-%M") + ".png"
    server_path = "/home/hdenny2/plotting-code/data/"
    plt.savefig(server_path + plot_filename)

    # FIXME this conditional won't work on tesla server, we have to hard-code it under the import statement
# Either show the plot as a popup or save it to a specified directory
#     if args.popup:
#         matplotlib.use('Qt5Agg')
#         plt.show()
#     else:
#         matplotlib.use('Agg')  # to run the script on remote server, otherwise it will try to use xwindows backend
#         dt = datetime.now()
#         plot_filename = plot_type + dt.strftime("%d-%b-%y-H-%M") + ".png"
#         server_path = "/home/hdenny2/plotting-code/data/"
#         plt.savefig(server_path + plot_filename)




def main():

    if args.test:
        param1 = testparam1
        param2 = testparam2
        csv1 = testdf1
        csv2 = testdf2
    else:
        param1 = param_file1
        param2 = param_file2
        csv1 = csv_file1
        csv2 = csv_file2

    if args.two:
        param_dict1, ixodes_dict1, constant1 = build_dictionaries(param1, csv1)
        final_df1 = build_dataframe(ixodes_dict1, param_dict1)

        param_dict2, ixodes_dict2, constant2 = build_dictionaries(param2, csv2)
        final_df2 = build_dataframe(ixodes_dict2, param_dict2)

        plot_two(final_df1, final_df2, constant1, constant2)
    else:
        param_dict, ixodes_dict, constant = build_dictionaries(param1, csv1)
        final_df = build_dataframe(ixodes_dict, param_dict)
        plot_df(final_df)


if __name__ == "__main__":
    main()

