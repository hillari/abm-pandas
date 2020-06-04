import csv
import os

import pandas as pd
import numpy as np
from matplotlib import pyplot

# TODO iterate through every file in a directory

# for filename in os.listdir("./data/"):
#     with open(filename, 'r') as file:
#         reader = csv.reader(file)

# datafile = "data/batch-data/paramSweep.2020.Feb.21.batch_param_map.09_18_07"
datafile = "/data/failures/instance_4/TickNonAgg.2020.Apr.07.batch_param_map.21_20_27"
with open(datafile, 'r') as file:
    reader = csv.reader(file)
    # mydict = {rows[0]: "Lifestage: {}\n Host Density: {}\n Ixode Count: {}\n Habitat Suitability: {}".format(
    #     rows[2], rows[3], rows[4], rows[5]) for rows in reader}  # create mapping as {int: 'string of params' }
    mydict = {rows[0]: [rows[2], rows[3], rows[4], rows[5]]
              for rows in reader}  # create mapping as {int: [list of params] }

# Iterate over key and value
for x, y in mydict.items():
    print("Run {}:\n {}".format(x, y))

