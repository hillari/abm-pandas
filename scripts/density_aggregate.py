import pandas as pd
import matplotlib
#matplotlib.use('Agg') # to run the script on remote server, otherwise it will try to use xwindows backend
import matplotlib.pyplot as plt
import argparse

# This script is intended to create a plot for Density vs. Total Ixodes to visualize the impact of host density
# on Ixodes survival rates. Host density, habitat suitability, and starting lifestate are held constant. For example,
# we do 10 iterations each of varying host density values and take the mean of the # of ixodes per model run for each
# of these individual values.
#
# Some of these functions are dependent on the file format for params and data files. A change in file sinks within
# Repast may require altering some of this code.
#
# TODO
#  - this code needs some logic to check for param/csv formatting errors
#  - process multiple files

parser = argparse.ArgumentParser()
parser.add_argument('-test', action='store_true')
parser.add_argument('-popup', action='store_true')
parser.add_argument('-two', action='store_true')
args = parser.parse_args()

testparam1 = "/media/hill/DATA-LINUX/abm-data/habitat-suitability/testparams"
testdf1 = "/media/hill/DATA-LINUX/abm-data/habitat-suitability/testdf-agg"
testparam2 = "/media/hill/DATA-LINUX/abm-data/habitat-suitability/testparams2"
testdf2 = "/media/hill/DATA-LINUX/abm-data/habitat-suitability/testdf-agg2"

param_file1 = "/home/hdenny2/plotting-code/data/host/new-model-agg/params-Aug2"
csv_file1 = "/home/hdenny2/plotting-code/data/host/new-model-agg/host-density-new.2020.Aug.02.06_06_21"
param_file2 = "/home/hdenny2/plotting-code/data/host/new-model-agg/params-Aug2"
csv_file2 = "/home/hdenny2/plotting-code/data/host/new-model-agg/host-density-new.2020.Aug.02.06_06_21"

# param_file = "/home/hdenny2/plotting-code/data/host-density/new-model-agg/" + args.param_file
# csv_file = "/home/hdenny2/plotting-code/data/host-density/new-model-agg/" + args.csv_file


def build_dictionaries(paramfile, csvfile):
    # Create a dictionary that maps the run# to host_density { run#: host_density }
    paramd = {}
    with open(paramfile, 'r') as file:
        for line in file:
            result = line.replace("\t", ",").split(',')
            # attempt to add the density value to run, if it doesn't exist, create it
            try:
                paramd[int(result[0])].append(float(result[4]))
            except KeyError:
                paramd[int(result[0])] = float(result[4])  # { run#: host_density }
    # Remove after testing
    print("PARAM DICT: ")
    for k, v in paramd.items():
        print(k, v)

    # Now make a dictionary that maps the run# tot total ixodes { run#: cumulative_ixodes }
    ixode_count_dict = {}
    colnames = ['run', 'tick', 'lifestate', 'name']
    df = pd.read_csv(csvfile, names=colnames, header=None, error_bad_lines=False)
    for run in df.groupby('run'):
        current_df = run[1]
        ixode_count_dict[run[0]] = len(current_df['name'].unique())
    # Remove after testing
    print("IXODES COUNT DICT:\n")
    for k, v in ixode_count_dict.items():
        print(k, v)

    return paramd, ixode_count_dict


# We will need: ixode_count_dict, paramd,
def build_dataframe(ixodesdict, paramdict):
    # Creating a data frame from the cumulative_ixodes dict
    df_final = pd.DataFrame(ixodesdict.items(), columns=['run', 'total_ixodes'])
    df_final['host_density'] = 0

    # Iterate through param dictionary and add the host density value to the associated run
    for key, value in paramdict.items():
        for i in range(len(paramdict)):
            df_final.loc[df_final['run'] == key, 'host_density'] = value

    # Now we have a df with | 'run' | 'total_ixode' | 'host_density' |
    # Create a dictionary with { host_density: agg_ixodes }
    agg_ixodes_dict = {}
    for density in df_final.groupby('host_density'):
        tmp_df = density[1]  # density is a tuple, so density[1] is the df we want
        agg_ixodes_dict[density[0]] = tmp_df['total_ixodes'].agg('mean')

    # Create a dataframe from the agg_ixodes_dict which we will use to plot
    df_agg_final = pd.DataFrame(agg_ixodes_dict.items(), columns=['host_density', 'agg_ixodes'])
    print(df_agg_final.head())
    return df_agg_final


def plot_two(df1, df2):
    matplotlib.use('Qt5Agg')
    fig, ax = plt.subplots()
    ax.set_title("Test Agg Host Density")
    ax.set_ylabel("Total Ixodes")
    ax.set_xlabel("Host Density")
    # props = dict(facecolor='wheat', alpha=0.5)
    ax = df1.plot(df1['host_density'], df1['agg_ixodes'])
    df2.plot(df1['host_density'], df1['agg_ixodes'], ax=ax)
    plt.show(block=True)


def plot_df(finaldf):
    # Needs variable name changes, but this is the code we use to add figure text

    # fig, ax = plt.subplots()
    # ax.set_title("Test Agg Host Density")
    # ax.set_ylabel("Total Ixodes")
    # ax.set_xlabel("Host Density")
    # props = dict(facecolor='wheat', alpha=0.5)
    # ax.plot(df_agg_final['host_density'], df_agg_final['agg_ixodes'])
    # plt.figtext(0.5, 0.5, 'Lifestage: adult\nStarting Ixodes: 10\nHabitat Suitability: 0.05', bbox=props)
    # plt.show(block=True)


    matplotlib.use('Qt5Agg')
    plt.ylabel("Cumulative Ixodes")
    plt.xlabel("Large Host Density")
    plt.title("Aggregated Host Density")
    plt.plot(finaldf['host_density'], finaldf['agg_ixodes'], marker='o')

# Either show the plot as a popup or save it to a specified directory
if args.popup:
    plt.show(block=True)
else:
    plt.savefig("/home/hdenny2/plotting-code/data/host/new-model-agg/density_Sept1_.png")


def main():

    if args.test:
        param1 = testparam1
        param2 = testparam1
        csv1 = testdf1
        csv2 = testdf2
    else:
        param1 = param_file1
        param2 = param_file2
        csv1 = csv_file1
        csv2 = csv_file2

    if args.two:
        param_dict1, ixodes_dict1 = build_dictionaries(param1, csv1)
        final_df1 = build_dataframe(ixodes_dict1, param_dict1)
        param_dict2, ixodes_dict2 = build_dictionaries(param2, csv2)
        final_df2 = build_dataframe(ixodes_dict2, param_dict2)
        plot_two(final_df1, final_df2)
    else:
        param_dict, ixodes_dict = build_dictionaries(param1, csv1)
        final_df = build_dataframe(ixodes_dict, param_dict)
        plot_df(final_df)


if __name__ == "__main__":
    main()
