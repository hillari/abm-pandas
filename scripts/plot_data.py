import pandas as pd
import argparse
import matplotlib
# matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from datetime import datetime

# This code is intended to handle plotting a dataframe output by clean_data.py

parser = argparse.ArgumentParser()
parser.add_argument('-type', choices=['habitat', 'host'], required=True)
# parser.add_argument('-first', action='store_true')
args = parser.parse_args()

# TODO
# - organize functionality
# - make groupby an arg
# - add code to do histograms for outlier runs


def get_args():
    if args.type == 'habitat':
        x_label = 'Habitat Suitability'
        plot_title = 'Aggregated Habitat Suitability'
        plot_legend = 'Host Density: '
    else:
        x_label = 'Host Density'
        plot_title = 'Aggregated Host Density'
        plot_legend = 'Habitat Suitability: '

    return x_label, plot_title, plot_legend


# TODO plot error bars/ CI
def plot(csvfile, legend, xlabel, title):
    df = pd.read_csv(csvfile)
    fig, ax = plt.subplots()
    plt.ylabel("Cumulative Ixodes")
    plt.xlabel(xlabel)
    plt.title(title)
    for label, data in df.groupby('habitat_suitability'):
        # plt.errorbar(data['host_density'], data['mean'], yerr=1.96*data['std'])
        data.plot('host_density', 'mean', ax=ax, label=label, marker='o', markersize=3)
    plt.legend(title=legend)
    server_path = ""
    # plt.savefig("../data/host/aggplottest.png")
    plt.show()

csvfile = "../data/host/host_agg_df"
x_label, plot_title, plot_legend = get_args()
plot(csvfile, plot_legend, x_label, plot_title)
