import pandas as pd
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-type', choices=['habitat', 'host'], required=True)
parser.add_argument('-first', action='store_true')
args = parser.parse_args()

# TODO
# - organize functionality
# - make groupby an arg


def get_args():
    if args.type == 'habitat':
        x_label = 'Habitat Suitability'
        plot_title = ''
        plot_legend = 'Host Density: '
    else:
        x_label = 'Host Density'
        plot_title = ''
        plot_legend = 'Habitat Suitability: '

    return x_label, plot_title, plot_legend


def plot(csvfile, legend):
    df = pd.read_csv(csvfile)
    fig, ax = plt.subplots()
    for label, df in df.groupby('habitat_suitability'):
        df.plot('host_density', 'mean', ax=ax, label=label)
    plt.legend(title=legend)
    # TODO plot labels, CI, legend formatting
    server_path = ""
    plt.savefig("/home/hdenny2/plotting-code/data/host/final/aggplottest.png")


x_label, plot_title, plot_legend = get_args()
