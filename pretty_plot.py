import pandas as pd
import ast
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

categories = ['Restaurants and Other Eating Places',
              'Grocery Stores',
              'General Medical and Surgical Hospitals']


def get_max_value(file):
    # find max value to set points between -1 and 1
    sk_ar = file['diff_closest_skewed_risk'].values
    uni_ar = file['diff_closest_uniform_risk'].values
    #     nor_ar = file['diff_closest_normal_risk'].values

    max_val = max(max(abs(sk_ar)), max(abs(uni_ar)))

    sk_ar = file['diff_random_skewed_risk'].values
    uni_ar = file['diff_random_uniform_risk'].values
    #     nor_ar = file['diff_random_normal_risk'].values

    max_val = max(max(max(abs(sk_ar)), max(abs(uni_ar))), max_val)

    return max_val


def plot_second_experiment(file, title, max_val, is_plot, plot_name):
    # ============================
    # Closest POI
    # ============================
    sk_ar_1 = file['diff_closest_skewed_risk'].values / max_val
    uni_ar_1 = file['diff_closest_uniform_risk'].values / max_val
    nor_ar_1 = file['diff_closest_normal_risk'].values / max_val

    occup = [x * 10 for x in range(11)]

    if is_plot:
        plt.plot(occup, sk_ar_1, 'ro-', label='skewed distribution')
        plt.plot(occup, uni_ar_1, 'b--', label='uniform distribution')
    else:
        plt.bar(occup, sk_ar_1, color='r', label='skewed distribution')
        plt.bar(occup, uni_ar_1, color='b', label='uniform distribution')
    plt.xlabel('max occupancy %')
    plt.title(title)
    plt.ylabel('rrisk difference [closest risk - minimal risk]')
    plt.yticks([-1, 0, 1])
    plt.legend()
    plt.savefig('vis/experiments/' + plot_name + '_closest.png', bbox_inches='tight')
    plt.show()

    plt.clf()

    # ============================
    # Random POI
    # ============================
    sk_ar = file['diff_random_skewed_risk'].values / max_val
    uni_ar = file['diff_random_uniform_risk'].values / max_val
    nor_ar = file['diff_random_normal_risk'].values / max_val

    if is_plot:
        plt.plot(occup, sk_ar, 'ro-', label='skewed distribution')
        plt.plot(occup, uni_ar, 'b--', label='uniform distribution')
    else:
        plt.bar(occup, sk_ar, color='r', label='skewed distribution')
        plt.bar(occup, uni_ar, color='b', label='uniform distribution')
    plt.xlabel('max occupancy %')
    plt.title(title)
    plt.ylabel('rrisk difference [random risk - smallest risk]')
    plt.yticks([-1, 0, 1])
    plt.legend()
    plt.savefig('vis/experiments/' + plot_name + '_random.png', bbox_inches='tight')
    plt.show()

    plt.clf()

    # ============================
    # Random and Closest POI
    # ============================
    if is_plot:
        plt.plot(occup, sk_ar_1, 'ro-', linewidth=1, label='skewed distribution (closest - safest)')
        plt.plot(occup, sk_ar, 'gv-.', linewidth=1, label='skewed distribution (random - safest)')
        plt.plot(occup, uni_ar, 'b--', linewidth=1, label='uniform distribution')

        plt.xlabel('max occupancy %')
        plt.title(title)
        plt.ylabel('rrisk difference')
        plt.yticks([-1, 0, 1])
        plt.legend()
        plt.savefig('vis/experiments/' + plot_name + '_random_and_closest.png', bbox_inches='tight')
        plt.show()

        plt.clf()


def get_max_value_from_row(row):
    # find max value to set points between -1 and 1
    sk_ar = np.array(ast.literal_eval(row['skewed_risk_(closest_vs_least_riskiest)']))
    uni_ar = np.array(ast.literal_eval(row['normal_risk_(closest_vs_least_riskiest)']))
    #     nor_ar = np.array(ast.literal_eval(row['uniform_risk_(closest_vs_least_riskiest)']))

    max_val = max(max(abs(sk_ar)) ,max(abs(uni_ar)))

    sk_ar = np.array(ast.literal_eval(row['skewed_risk_(random_vs_least_riskiest)']))
    uni_ar = np.array(ast.literal_eval(row['uniform_risk_(random_vs_least_riskiest)']))
    #     nor_ar = np.array(ast.literal_eval(row['normal_risk_(random_vs_least_riskiest)']))

    max_val = max(max(max(abs(sk_ar)) ,max(abs(uni_ar))),max_val)
    return max_val


def plot_third_experiment(file, title, max_val,plot_name,is_plot):

    colors = cm.rainbow(np.linspace(0, 1, 11))
    markers = ['*-','--','-v','-.','+:','o-','x--','<-', '>--', 's-', 'P--']
    occup = [x*10 for x in range(11)]

    for index, row in file.iterrows():
        # find max value to set points between -1 and 1
        sk_ar = np.array(ast.literal_eval(row['skewed_risk_(closest_vs_least_riskiest)'])) / max_val
        uni_ar = np.array(ast.literal_eval(row['uniform_risk_(closest_vs_least_riskiest)'])) / max_val
        nor_ar = np.array(ast.literal_eval(row['normal_risk_(closest_vs_least_riskiest)'])) / max_val

        # Show all three distributions on one graph

        if is_plot:
            plt.plot(occup, sk_ar, markers[index], color=colors[index], label='follow '+str(index*10)+"% of recommendations")
        else:
            plt.bar(occup, sk_ar, color=colors[index], label='follow '+str(index*10)+"% of recommendations")

    plt.xlabel('max occupancy %')
    plt.title(title)
    plt.ylabel('rrisk [x% safest, (100-x)% closest]')
    plt.yticks([0, 0.5, 1])
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig('vis/experiments/'+plot_name+'_closest.png', bbox_inches='tight')
    plt.show()

    plt.clf()

    for index, row in file.iterrows():
        # find max value to set points between -1 and 1
        sk_ar = np.array(ast.literal_eval(row['skewed_risk_(random_vs_least_riskiest)'])) / max_val
        uni_ar = np.array(ast.literal_eval(row['uniform_risk_(random_vs_least_riskiest)'])) / max_val
        nor_ar = np.array(ast.literal_eval(row['normal_risk_(random_vs_least_riskiest)'])) / max_val

        # Show all three distributions on one graph

        if is_plot:
            plt.plot(occup, sk_ar, markers[index], color=colors[index], label='follow '+str(index*10)+"% of recommendations")
        else:
            plt.bar(occup, sk_ar, color=colors[index], label='follow '+str(index*10)+"% of recommendations")

    plt.xlabel('max occupancy %')
    plt.title(title)
    plt.ylabel('rrisk [x% safest, (100-x)% random]')
    plt.yticks([0, 0.5, 1])
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig('vis/experiments/'+plot_name+'_random.png', bbox_inches='tight')
    plt.show()

max_val = 0

for i in range(2):
    file = pd.read_csv('static/auxiliary_files/risk_diff_of_computed_queries_'+str(i)+'.csv')
    max_val = max(get_max_value(file), max_val)

for i in range(2):
    file = pd.read_csv('static/auxiliary_files/risk_diff_of_computed_queries_'+str(i)+'.csv')
    title = 'Risk Differenccee between our recommendation and null model\nin '+categories[i]
    plot_name = '2nd_exp_plot_'+str(i)
    plot_second_experiment(file, title, max_val, True, plot_name)

for i in range(2):
    file = pd.read_csv('static/auxiliary_files/risk_diff_of_computed_queries_'+str(i)+'.csv')
    title = 'Risk Differenccee between our recommendation and null model\nin '+categories[i]
    plot_name = '2nd_exp_bar_'+str(i)
    plot_second_experiment(file, title, max_val, False, plot_name)

max_val = 0

for i in range(2):
    file = pd.read_csv('static/auxiliary_files/risk_of_varying_policies_'+str(i)+'.csv')

    for index, row in file.iterrows():
        max_val = max(get_max_value_from_row(row), max_val)
print(max_val)
for i in range(2):
    file = pd.read_csv('static/auxiliary_files/risk_of_varying_policies_'+str(i)+'.csv')
    title = 'Risk at different occupancies \nin '+categories[i]
    plot_name = '3rd_exp_plot_'+str(i)
    plot_third_experiment(file, title, max_val, plot_name, True)

# for i in range(2):
#     file = pd.read_csv('static/auxiliary_files/risk_of_varying_policies_'+str(i)+'.csv')
#     title = 'Risk at different occupancies \nin '+categories[i]
#     plot_name = '3rd_exp_bar_'+str(i)
#     plot_third_experiment(file, title, max_val, plot_name, False)