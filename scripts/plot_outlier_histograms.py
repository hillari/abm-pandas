import pandas as pd
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 9/30/2020
# When finished this code will plot the results output by log_outliers.py
# Currently working code is in the associated notebook

parser = argparse.ArgumentParser()
parser.add_argument('-type', choices=['habitat', 'host'], required=True)
args = parser.parse_args()


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


def plot(csvfile, legend, xlabel, title):
    pass