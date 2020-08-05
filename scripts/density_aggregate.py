import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# This script is intended to create a plot for Density vs. Total Ixodes to visualize the impact of host density
# on Ixodes survival rates. Host density, habitat suitability, and starting lifestate are held constant. For example,
# we do 10 iterations each of varying host density values and take the mean of the # of ixodes per model run for each
# of these individual values.
#
# Some of these functions are dependent on the file format for params and data files. A change in file sinks within
# Repast may require altering some of this code.
#
# TODO
#  - optimise and add args
#  - ?create helper file/move functions

paramfile = ""
csv_file = "/home/hill/PyCharmProjects/tickABM/data/host-density/new-model-agg/density-agg-newest.2020.Jul.31"


def build_habitat_dict(paramfile, csvfile):
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
                for k, v in paramd.items():
                    print(k, v)

    # Now make a dictionary that maps the run# tot total ixodes { run#: cumulative_ixodes }
    ixode_count_dict = {}
    df = pd.read_csv(csvfile, error_bad_lines=False)
    for run in df.groupby('run'):
        current_df = run[1]
        ixode_count_dict[run[0]] = len(current_df['name'].unique())
    return paramd, ixode_count_dict


# We will need: ixode_count_dict, paramd,
def build_df(ixodes_dict, param_dict):
    # Creating a data frame from the cumulative_ixodes dict
    df_final = pd.DataFrame(ixodes_dict.items(), columns=['run', 'total_ixodes'])
    df_final['host_density'] = 0

    # Iterate through param dictionary and add the host density value to the associated run
    for key, value in param_dict.items():
        for i in range(len(param_dict)):
            df_final.loc[df_final['run'] == key, 'host_density'] = value

    # Now we have a df with | 'run' | 'total_ixode' | 'host_density' |
    # Create a dictionary with { host_density: agg_ixodes }
    agg_ixodes_dict = {}
    for density in df_final.groupby('host_density'):
        tmp_df = density[1]  # density is a tuple, so density[1] is the df we want
        print(density[0])
        agg_ixodes_dict[density[0]] = tmp_df['total_ixodes'].agg('mean')

    # Create a dataframe from the agg_ixodes_dict which we will use to plot
    df_agg_final = pd.DataFrame(agg_ixodes_dict.items(), columns=['host_density', 'agg_ixodes'])

    return df_agg_final


