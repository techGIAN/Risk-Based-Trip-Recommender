import pandas as pd
import ast
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

categories = ['Restaurants and Other Eating Places',
              'Grocery Stores',
              'General Medical and Surgical Hospitals']


# ---------------------------------
#   First Experiment methods
# ---------------------------------
def get_max_value(file):
    # find max value to set points between -1 and 1
    #     sk_ar = file['diff_closest_skewed_risk'].values
    uni_ar = file['diff_closest_uniform_risk'].values
    nor_ar = file['diff_closest_normal_risk'].values

    max_val = max(max(abs(nor_ar)), max(abs(uni_ar)))

    #     sk_ar = file['diff_random_skewed_risk'].values
    uni_ar = file['diff_random_uniform_risk'].values
    nor_ar = file['diff_random_normal_risk'].values

    max_val = max(max(max(abs(nor_ar)), max(abs(uni_ar))), max_val)

    return max_val


def plot_second_experiment(file, title, max_val, is_plot, plot_name):
    # ============================
    # Closest POI
    # ============================
    #     sk_ar_1 = file['diff_closest_skewed_risk'].values / max_val
    uni_ar_1 = file['diff_closest_uniform_risk'].values / max_val
    nor_ar_1 = file['diff_closest_normal_risk'].values / max_val

    occup = [x * 10 for x in range(11)]

    if is_plot:
        plt.plot(occup, nor_ar_1, 'ro-', label='SD=1')
        plt.plot(occup, uni_ar_1, 'b--', label='uniform distribution')
    else:
        plt.bar(occup, nor_ar_1, color='r', label='SD=1')
        plt.bar(occup, uni_ar_1, color='b', label='uniform distribution')
    plt.xlabel('max occupancy %')
    plt.title(title)
    plt.ylabel('rrisk difference [smallest risk - closest risk]')
    plt.yticks([-1, 0, 1])
    plt.legend()
    plt.savefig('vis/experiments/' + plot_name + '_closest.png', bbox_inches='tight')
    plt.show()

    plt.clf()

    # ============================
    # Random POI
    # ============================
    #     sk_ar = file['diff_random_skewed_risk'].values / max_val
    uni_ar = file['diff_random_uniform_risk'].values / max_val
    nor_ar = file['diff_random_normal_risk'].values / max_val

    tmp_nor_ar = np.polyfit(occup, nor_ar, 2)
    nor_ar_trendline = np.poly1d(tmp_nor_ar)

    if is_plot:
        plt.plot(occup, nor_ar_trendline(occup), 'ro-', label='SD=1')
        plt.plot(occup, uni_ar, 'b--', label='uniform distribution')
    else:
        plt.bar(occup, nor_ar, color='r', label='SD=1')
        plt.bar(occup, uni_ar, color='b', label='uniform distribution')
    plt.xlabel('max occupancy %')
    plt.title(title)
    plt.ylabel('rrisk difference [smallest risk - random risk]')
    plt.yticks([-1, 0, 1])
    plt.legend()
    plt.savefig('vis/experiments/' + plot_name + '_random.png', bbox_inches='tight')
    plt.show()

    plt.clf()

    # ============================
    # Random and Closest POI
    # ============================
    if is_plot:
        plt.plot(occup, nor_ar_1, 'ro-', linewidth=1, label='SD=1 (safest - closest)')
        plt.plot(occup, nor_ar_trendline(occup), 'gv-.', linewidth=1, label='SD=1 (safest - random)')
        plt.plot(occup, uni_ar, 'b--', linewidth=1, label='uniform distribution (safest - random)')

        plt.xlabel('max occupancy %')
        plt.title(title)
        plt.ylabel('rrisk difference')
        plt.yticks([-1, 0, 1])
        plt.legend()
        plt.savefig('vis/experiments/' + plot_name + '_random_and_closest.png', bbox_inches='tight')
        plt.show()

        plt.clf()


# ---------------------------------
#   Second Experiment methods
# ---------------------------------
def get_max_value_from_row(row):
    # find max value to set points between -1 and 1
    #     sk_ar = np.array(ast.literal_eval(row['skewed_risk_(closest_vs_least_riskiest)']))
    uni_ar = np.array(ast.literal_eval(row['normal_risk_(closest_vs_least_riskiest)']))
    nor_ar = np.array(ast.literal_eval(row['uniform_risk_(closest_vs_least_riskiest)']))

    max_val = max(max(abs(nor_ar)) ,max(abs(uni_ar)))

    #     sk_ar = np.array(ast.literal_eval(row['skewed_risk_(random_vs_least_riskiest)']))
    uni_ar = np.array(ast.literal_eval(row['uniform_risk_(random_vs_least_riskiest)']))
    nor_ar = np.array(ast.literal_eval(row['normal_risk_(random_vs_least_riskiest)']))

    max_val = max(max(max(abs(nor_ar)) ,max(abs(uni_ar))),max_val)
    return max_val


def plot_third_experiment(file, title, max_val,plot_name,is_plot):

    colors = cm.rainbow(np.linspace(0, 1, 11))
    markers = ['*-','--','-v','-.','+:','o-','x--','<-', '>--', 's-', 'P--']
    occup = [x*10 for x in range(11)]

    for index, row in file.iterrows():
        # find max value to set points between -1 and 1
        #         sk_ar = np.array(ast.literal_eval(row['skewed_risk_(closest_vs_least_riskiest)'])) / max_val
        uni_ar = np.array(ast.literal_eval(row['uniform_risk_(closest_vs_least_riskiest)'])) / max_val
        nor_ar = np.array(ast.literal_eval(row['normal_risk_(closest_vs_least_riskiest)'])) / max_val

        # Show all three distributions on one graph
        if is_plot:
            plt.plot(occup, nor_ar, markers[index], color=colors[index], label='\u03BE='+str(index*10)+"%")
        else:
            plt.bar(occup, nor_ar, color=colors[index], label='\u03BE='+str(index*10)+"%")

    plt.xlabel('max occupancy %')
    plt.title(title)
    plt.ylabel('rrisk [x% safest, (100-x)% closest]')
    plt.yticks([0, 0.5, 1])
    plt.legend()#(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig('vis/experiments/'+plot_name+'_closest.png', bbox_inches='tight')
    plt.show()

    plt.clf()

    for index, row in file.iterrows():
        # find max value to set points between -1 and 1
        #         sk_ar = np.array(ast.literal_eval(row['skewed_risk_(random_vs_least_riskiest)'])) / max_val
        uni_ar = np.array(ast.literal_eval(row['uniform_risk_(random_vs_least_riskiest)'])) / max_val
        nor_ar = np.array(ast.literal_eval(row['normal_risk_(random_vs_least_riskiest)'])) / max_val

        tmp_nor_ar = np.polyfit(occup, nor_ar, 2)
        nor_ar_trendline = np.poly1d(tmp_nor_ar)

        # Show all three distributions on one graph
        if is_plot:
            plt.plot(occup, nor_ar_trendline(occup), markers[index], color=colors[index], label='\u03BE='+str(index*10)+"%")
        else:
            plt.bar(occup, nor_ar_trendline(occup), color=colors[index], label='\u03BE='+str(index*10)+"%")

    plt.xlabel('max occupancy %')
    plt.title(title)
    plt.ylabel('rrisk [x% safest, (100-x)% random]')
    plt.yticks([0, 0.5, 1])
    plt.legend()#(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig('vis/experiments/'+plot_name+'_random.png', bbox_inches='tight')
    plt.show()


# ---------------------------------
#   Third Experiment methods
# ---------------------------------
def get_max_value_from_2_files(file1, file2):
    max_val = 10

    # get max value
    #     for index, row in file1.iterrows():
    row = 0
    #         sk_ar1 = np.array(ast.literal_eval(file1.loc[index]['skewed_risk_(closest_vs_least_riskiest)'])) #/ max_val
    uni_ar1 = np.array(ast.literal_eval(file1.loc[index]['uniform_risk_(closest_vs_least_riskiest)'])) #/ max_val
    nor_ar1 = np.array(ast.literal_eval(file1.loc[index]['normal_risk_(closest_vs_least_riskiest)'])) #/ max_val

    #         sk_ar2 = np.array(ast.literal_eval(file2.loc[index]['skewed_risk_(closest_vs_least_riskiest)'])) #/ max_val
    uni_ar2 = np.array(ast.literal_eval(file2.loc[index]['uniform_risk_(closest_vs_least_riskiest)'])) #/ max_val
    nor_ar2 = np.array(ast.literal_eval(file2.loc[index]['normal_risk_(closest_vs_least_riskiest)'])) #/ max_val

    #         sk_ar3 = np.array(ast.literal_eval(file1.loc[index]['skewed_risk_(random_vs_least_riskiest)'])) #/ max_val
    uni_ar3 = np.array(ast.literal_eval(file1.loc[index]['uniform_risk_(random_vs_least_riskiest)'])) #/ max_val
    nor_ar3 = np.array(ast.literal_eval(file1.loc[index]['normal_risk_(random_vs_least_riskiest)'])) #/ max_val

    #         sk_ar4 = np.array(ast.literal_eval(file2.loc[index]['skewed_risk_(random_vs_least_riskiest)'])) #/ max_val
    uni_ar4 = np.array(ast.literal_eval(file2.loc[index]['uniform_risk_(random_vs_least_riskiest)'])) #/ max_val
    nor_ar4 = np.array(ast.literal_eval(file2.loc[index]['normal_risk_(random_vs_least_riskiest)'])) #/ max_val
    U1 = abs(uni_ar1- uni_ar2)
    U2 = abs(uni_ar3 - uni_ar4)
    N1 = abs(nor_ar1 - nor_ar2)
    N2 = abs(nor_ar3 - nor_ar4)
    max_val = max(max(max(abs(N1)),max(abs(N2))), max_val)

    return max_val

def plot_third_enhanced_experiment(file1, file2, title, max_val, plot_name, is_plot, is_normal):
    colors = cm.rainbow(np.linspace(0, 1, 11))
    markers = ['*-','--','-v','-.','+:','o-','x--','<-', '>--', 's-', 'P--']
    occup = [x*10 for x in range(11)]

    #     for index, row in file1.iterrows():
    index = 10

    # CLOSEST
    #         sk_ar1 = np.array(ast.literal_eval(file1.loc[index]['skewed_risk_(closest_vs_least_riskiest)'])) #/ max_val
    uni_ar1 = np.array(ast.literal_eval(file1.loc[index]['uniform_risk_(closest_vs_least_riskiest)'])) #/ max_val
    nor_ar1 = np.array(ast.literal_eval(file1.loc[index]['normal_risk_(closest_vs_least_riskiest)'])) #/ max_val
    #         sk_ar2 = np.array(ast.literal_eval(file2.loc[index]['skewed_risk_(closest_vs_least_riskiest)'])) #/ max_val
    uni_ar2 = np.array(ast.literal_eval(file2.loc[index]['uniform_risk_(closest_vs_least_riskiest)'])) #/ max_val
    nor_ar2 = np.array(ast.literal_eval(file2.loc[index]['normal_risk_(closest_vs_least_riskiest)'])) #/ max_val

    # RANDOM
    #         sk_ar3 = np.array(ast.literal_eval(file1.loc[index]['skewed_risk_(random_vs_least_riskiest)'])) #/ max_val
    uni_ar3 = np.array(ast.literal_eval(file1.loc[index]['uniform_risk_(random_vs_least_riskiest)'])) #/ max_val
    nor_ar3 = np.array(ast.literal_eval(file1.loc[index]['normal_risk_(random_vs_least_riskiest)'])) #/ max_val
    #         sk_ar4 = np.array(ast.literal_eval(file2.loc[index]['skewed_risk_(random_vs_least_riskiest)'])) #/ max_val
    uni_ar4 = np.array(ast.literal_eval(file2.loc[index]['uniform_risk_(random_vs_least_riskiest)'])) #/ max_val
    nor_ar4 = np.array(ast.literal_eval(file2.loc[index]['normal_risk_(random_vs_least_riskiest)'])) #/ max_val

    nor_ar_a = (nor_ar1 - nor_ar2) / max_val
    uni_ar_a = (uni_ar1 - uni_ar2) / max_val

    nor_ar_b = (nor_ar3 - nor_ar4) / max_val
    uni_ar_b = (uni_ar3 - uni_ar4) / max_val

    tmp_nor_ar = np.polyfit(occup, nor_ar_b, 2)
    nor_ar_trendline = np.poly1d(tmp_nor_ar)

    # Show all three distributions on one graph
    if is_normal:
        plt.plot(occup, nor_ar_a, 'ro-', linewidth=1, label="normal difference (SD=1)")
        #         plt.plot(occup, nor_ar_trendline(occup), 'gv-.', linewidth=1, label="random difference (SD=1)")
        plt.plot(occup, uni_ar_a, 'b--', linewidth=1, label="uniform difference")
    else:
        plt.plot(occup, uni_ar_a, 'ro-', linewidth=1, label="normal difference")
    #         plt.plot(occup, uni_ar_b, 'gv-.', linewidth=1, label="random selection difference")

    plt.xlabel('max occupancy % ')
    plt.title("Risk difference: post Covid - pre Covid "+title)
    plt.ylabel('relative risk')
    if is_normal:
        plt.yticks([-1, 0, 1])

    #     plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.legend()
    if is_normal:
        plt.savefig('vis/experiments/'+plot_name+'_normal_before_after.png', bbox_inches='tight')
    else:
        plt.savefig('vis/experiments/'+plot_name+'_uniform_before_after.png', bbox_inches='tight')

    plt.show()

    plt.clf()


# ---------------------------------------------
#   First set of plots
# ---------------------------------------------
max_val = 0

for i in range(2):
    file1 = pd.read_csv('static/auxiliary_files/risk_diff_of_computed_queries_' + str(i) + '_max_occup_4.csv')
    #     file2 = pd.read_csv('static/auxiliary_files/risk_diff_of_computed_queries_'+str(i)+'_max_occup_2.csv')
    #     max_val = max(max(get_max_value(file1), get_max_value(file2)), max_val)
    max_val = max(get_max_value(file1), max_val)

# for k in [2,4]:
# print("\n\t\t-------------------------\n\t\tMAX OCCUPANCY = "+str(k)+"m^2:\n\n")

for i in range(2):
    file = pd.read_csv('static/auxiliary_files/risk_diff_of_computed_queries_' + str(i) + '_max_occup_4.csv')
    title = 'Risk Differenccee between our recommendation and null model\nin ' + categories[i]
    plot_name = '2nd_exp_plot_' + str(i)
    plot_second_experiment(file, title, max_val, True, plot_name)

# ---------------------------------------------
#   Second set of plots
# ---------------------------------------------
max_val = 0

for i in range(2):
    file = pd.read_csv('static/auxiliary_files/risk_of_varying_policies_' + str(i) + '_max_occup_4.csv')

    for index, row in file.iterrows():
        max_val = max(get_max_value_from_row(row), max_val)
print(max_val)
for i in range(2):
    file = pd.read_csv('static/auxiliary_files/risk_of_varying_policies_' + str(i) + '_max_occup_4.csv')
    title = 'Risk at different occupancies \nin ' + categories[i]
    plot_name = '3rd_exp_plot_' + str(i)
    plot_third_experiment(file, title, max_val, plot_name, True)

# ---------------------------------------------
#   Third set of plots
# ---------------------------------------------
max_val = 0

for i in range(2):
    file1 = pd.read_csv('static/auxiliary_files/risk_of_varying_policies_' + str(i) + "_max_occup_" + str(4) + '.csv')
    file2 = pd.read_csv('static/auxiliary_files/risk_of_varying_policies_' + str(i) + "_max_occup_" + str(2) + '.csv')

    max_val = max(get_max_value_from_2_files(file1, file2), max_val)

for is_normal in [True, False]:
    for i in range(2):
        file1 = pd.read_csv(
            'static/auxiliary_files/risk_of_varying_policies_' + str(i) + "_max_occup_" + str(4) + '.csv')
        file2 = pd.read_csv(
            'static/auxiliary_files/risk_of_varying_policies_' + str(i) + "_max_occup_" + str(2) + '.csv')

        title = '\nin ' + categories[i]
        plot_name = 'Enhanced_3nd_exp_' + str(i) + '_precovid_and_postcovid'
        plot_third_enhanced_experiment(file1, file2, title, max_val, plot_name, True, is_normal)
