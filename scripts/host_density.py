import pandas as pd
import matplotlib
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


# TODO make the dataframe file an argument
def build_df(param_dict):
    ixodes_count_dict = {}
    df = pd.read_csv("../data/host-density/adult-runs/instances/data-survival.i1.2020.May.27.03_06_35")
    for run in df.groupby('run'):
        current_df = run[1]
        ixodes_count_dict[run[0]] = len(current_df['name'].unique())

    df_final = pd.DataFrame(ixodes_count_dict.items(), columns=['run', 'total_ixode'])
    df_final['host_density'] = 0

    for key, value in param_dict.items():
        for i in range(len(value[0])):
            # Both of these techniques work, but loc is preferred over chained indexing
            # df_final['host_density'][df_final['run'] == value[0][i]] = value[1][i]
            df_final.loc[df_final['run'] == value[0][i], 'host_density'] = value[1][i]
            df_final.loc[df_final['run'] == value[0][i], 'habitat_suitability'] = key
    return df_final


def plot_df(df):
    matplotlib.use('Qt5Agg')
    # fig = plt.figure()
    for hab in df.groupby('habitat_suitability'):
        dat = hab[1]
        plt.plot('host_density', 'total_ixode', data=dat, marker='o')
        plt.ylabel('Cumulative Ixodes')
        plt.xlabel('Large host density')
        plt.title("Title")
        # plt.legend() # FIX to show values not just label
    # plt.show()
    plt.savefig("../data/host-density/plots/host-densityi1.png")


params = "../data/host-density/adult-runs/instances/param_inputi1.txt"
param_mapping = build_habitat_dict(params)
host_density_df = build_df(param_mapping)
plot_df(host_density_df)

# for k, v in param_mapping.items():
#     print(k, v)
