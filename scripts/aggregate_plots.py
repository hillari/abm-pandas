import pandas as pd
import matplotlib
matplotlib.use('Agg')  # to run the script on remote server, otherwise it will try to use xwindows backend
import matplotlib.pyplot as plt
import argparse
from datetime import datetime


# This script is intended to create a plot for habitat suitability & Total Ixodes to visualize the impact of
# habitat suitability on Ixodes survival rates.
#
# Usage: python3 ./aggregate_plots.py <paramfile> <csvfile> -plot <plot type> [-popup] [-root <directory>]
#
# The -popup option is for local use and allows a plot to be shown without automatically saving it. If this option
# is ommitted, the plot is saved to a hard-coded location
#

# TODO better plot labeling

# --- Argparse ---

parser = argparse.ArgumentParser()
# parser.add_argument('param_file')
# parser.add_argument('csv_file')
parser.add_argument('-popup', action='store_true')
parser.add_argument('-plot', choices=['habitat', 'host'], required=True)
args = parser.parse_args()

# FOR REMOTE:
param_file = "/home/hdenny2/plotting-code/data/host/new-model-agg/host-density-new.2020.Aug.01.22_57_29"
csv_file = "/home/hdenny2/plotting-code/data/host/new-model-agg/params-Aug1"
# param_file = root_dir + args.plot + "/" + args.param_file
# csv_file = root_dir + args.plot + "/" + args.csv_file

# FOR LOCAL:
# param_file = "/media/hill/DATA-LINUX/abm-data/habitat-suitability/testparams"
# csv_file = "/media/hill/DATA-LINUX/abm-data/habitat-suitability/testdf-agg"


def get_args():
    # This function uses argparse to tell the code which plots we are creating

    if args.plot == 'habitat':
        dict_index = 8
        plot_type = 'habitat_suitability'
        x_label = "Habitat Suitability"
        plot_title = "Aggregated Habitat Suitability"
    else:
        dict_index = 4
        plot_type = 'host_density'
        x_label = "Host Density"
        plot_title = "Aggregated Host Density"
    return dict_index, plot_type, x_label, plot_title


def build_dictionaries(paramfile, csvfile):
    """
    Parses param file to create a dictionary that maps the run# to <plot_type> like so - { run#: <plot_type> }
    :param paramfile: the parameter file to be parsed
    :param csvfile: the repast file sink
    :return paramd, ixodes_count_dict: parameter dictionary and cumulative ixodes dictionary
    """
    dict_index, _, _, _ = get_args()
    print("Creating dictionaries...")
    print("THE DICT INDEX IS: ", dict_index)
    paramd = {}
    with open(paramfile, 'r') as file:
        for line in file:
            result = line.replace("\t", ",").replace('\n', '').split(',')
            print("result is ", result)
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
    print(df.head())
    for run in df.groupby('run'):
        current_df = run[1]
        ixodes_count_dict[run[0]] = len(current_df['name'].unique())
    print("DONE creating initial data frame.")
    # print("ixodes count dict:\n")
    # for k, v in ixodes_count_dict.items():
    #     print(k, v)
    return paramd, ixodes_count_dict


# This function builds the dataframes we need for plotting and returns the final df
def build_dataframe(ixodesdict, paramdict):

    _, plot_type, _, _ = get_args()
    print("Building dataframes...")
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
        tmp_df = density[1]  # density is a tuple, so density[1] is the df we want
        agg_ixodes_dict[density[0]] = tmp_df['total_ixodes'].agg('mean')

    # print("AGG_IXODES dict:")
    # for k, v in agg_ixodes_dict.items():
    #     print(k, "-", v)

    # Create a dataframe from the agg_ixodes_dict which we will use to plot
    df_agg_final = pd.DataFrame(agg_ixodes_dict.items(), columns=[plot_type, 'agg_ixodes'])
    print(df_agg_final.head())
    print("DONE building dataframes.")
    return df_agg_final


def plot_df(finaldf):

    _, plot_type, x_label, plot_title = get_args()
    print("Plotting data...")
    plt.ylabel("Cumulative Ixodes")
    plt.xlabel(x_label)
    plt.title(plot_title)
    plt.plot(finaldf[plot_type], finaldf['agg_ixodes'], marker='o')

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

    dt = datetime.now()
    plot_filename = plot_type + dt.strftime("%d-%b-%y-%H-%M") + ".png"
    server_path = "/home/hdenny2/plotting-code/data/"
    plt.savefig(server_path + plot_filename)


param_dict, ixodes_dict = build_dictionaries(param_file, csv_file)
final_df = build_dataframe(ixodes_dict, param_dict)
plot_df(final_df)
