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


def build_habitat_dict(paramfile):
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

