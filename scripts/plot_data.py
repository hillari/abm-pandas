import pandas as pd
import argparse
import matplotlib
# matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from datetime import datetime

# Hillari Denny
# Last update: 9/30/2020
# This builds a lineplot to visualize the results of a param sweep to identify param impact on tick establishment
# Input is the dataframe output by clean_data.py

# TODO
# - reorganize plot(). Do write
# - make groupby a function argument
# - Add path/filename arg

parser = argparse.ArgumentParser()
parser.add_argument('-type', choices=['habitat', 'host'], required=True)
# parser.add_argument('-first', action='store_true')
args = parser.parse_args()


def get_args():
    if args.type == 'habitat':
        plot_type = 'habitat_suitability'
        x_label = 'Habitat Suitability'
        plot_title = 'Aggregated Habitat Suitability'
        plot_legend = 'Host Density: '
    else:
        plot_type = 'host_density'
        x_label = 'Host Density'
        plot_title = 'Aggregated Host Density'
        plot_legend = 'Habitat Suitability: '

    return plot_type, x_label, plot_title, plot_legend


# TODO make groupby an arg (update get_args() )
def plot(plottype, csv, legend, xlabel, title):
    df = pd.read_csv(csv)
    fig, ax = plt.subplots()
    plt.ylabel("Cumulative Ixodes")
    plt.xlabel(xlabel)
    plt.title(title)
    for label, data in df.groupby('host_density'):
        # plt.errorbar(data['host_density'], data['mean'], yerr=1.96*data['std'])
        data.plot(plottype, 'mean', ax=ax, label=label, marker='o', markersize=3)
    plt.legend(title=legend)
    server_path = ""
    # plt.savefig("../data/host/aggplottest.png")
    plt.show()

csvfile = "../data/habitat-suitability/hab-agg-df-directoryloopversion"
plot_type, x_label, plot_title, plot_legend = get_args()
plot(plot_type, csvfile, plot_legend, x_label, plot_title)
