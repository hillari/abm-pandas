import pandas as pd
import matplotlib.pyplot as plt


#
# This function parses a parameter file and creates a dictionary that maps the habitat_suitability value with the
# corresponding run_number and host_density values
#
# { habitat: [ [run_number], [host_density] ] }
#

def build_habitat_dict(paramfile):
    # paramfile = "../data/host-density/adult-runs/unrolledParamFile-June1.txt"
    param_dict = {}
    with open(paramfile, 'r') as file:
        for line in file:
            result = line.replace("\t",",").split(',')
    # Try to add the values to the key, if that key does not exist, create it
            try:
                param_dict[float(result[8])][0].append(int(result[0])) # add run number
                param_dict[float(result[8])][1].append(float(result[4])) # add host density
            except KeyError:
                param_dict[float(result[8])] = [[int(result[0])], [float(result[4])]]
    return param_dict
                
                
params = "../data/host-density/adult-runs/instances/param_inputi1.txt"
param_mapping = build_habitat_dict(params)

for k, v in param_mapping.items():
    print(k, v)