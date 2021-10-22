"""
    Generates queries within a given boundary based on the number of
    rows, columns and category provided.

    Saves results in ./static/auxiliary_files/queries.csv
"""

import pandas as pd
from utilityMethods import queryOSRM, haversine_dist
import numpy as np
import random
import os

travel_by = ['car', 'foot']

output_results_to = 'static/auxiliary_files/queries.csv'

categories = ['Restaurants and Other Eating Places',
              'Building Equipment Contractors', 'Grocery Stores',
              'Automotive Parts, Accessories, and Tire Stores',
              'Health and Personal Care Stores',
              'Nursing Care Facilities (Skilled Nursing Facilities)',
              'Clothing Stores',
              'Lawn and Garden Equipment and Supplies Stores',
              'Home Furnishings Stores', 'Other Personal Services',
              'Accounting, Tax Preparation, Bookkeeping, and Payroll Services',
              'Other Miscellaneous Store Retailers',
              'Offices of Other Health Practitioners', 'Offices of Physicians',
              'General Medical and Surgical Hospitals', 'Spectator Sports',
              'Florists',
              'Hardware, and Plumbing and Heating Equipment and Supplies Merchant Wholesalers',
              'Electronics and Appliance Stores', 'Shoe Stores',
              'Book Stores and News Dealers', 'Offices of Dentists',
              'Sporting Goods, Hobby, and Musical Instrument Stores',
              'Personal Care Services',
              'Printing and Related Support Activities',
              'Offices of Real Estate Agents and Brokers',
              'Jewelry, Luggage, and Leather Goods Stores',
              'Gasoline Stations',
              'Machinery, Equipment, and Supplies Merchant Wholesalers',
              'Automotive Repair and Maintenance', 'Specialty Food Stores',
              'Other Professional, Scientific, and Technical Services',
              'General Merchandise Stores, including Warehouse Clubs and Supercenters',
              'Automobile Dealers', 'Furniture Stores', 'Special Food Services',
              'Personal and Household Goods Repair and Maintenance',
              'Consumer Goods Rental',
              'Religious Organizations',
              'Building Finishing Contractors', 'Beer, Wine, and Liquor Stores',
              'Colleges, Universities, and Professional Schools',
              'Bakeries and Tortilla Manufacturing',
              'Agencies, Brokerages, and Other Insurance Related Activities',
              'Used Merchandise Stores', 'Depository Credit Intermediation',
              'Management, Scientific, and Technical Consulting Services',
              'Architectural, Engineering, and Related Services',
              'Automotive Equipment Rental and Leasing',
              'Advertising, Public Relations, and Related Services',
              'Investigation and Security Services',
              'Support Activities for Air Transportation',
              'Social Advocacy Organizations', 'Department Stores',
              'Legal Services', 'Gambling Industries',
              'Insurance Carriers',
              'Coating, Engraving, Heat Treating, and Allied Activities',
              'RV (Recreational Vehicle) Parks and Recreational Camps',
              'Beverage Manufacturing',
              'Support Activities for Road Transportation',
              'Home Health Care Services', 'Household Appliance Manufacturing',
              'Drycleaning and Laundry Services',
              'Wired and Wireless Telecommunications Carriers',
              'Commercial and Industrial Machinery and Equipment Rental and Leasing',
              'Urban Transit Systems',
              'Child Day Care Services',
              'Waste Collection',
              'Elementary and Secondary Schools']


def get_queries(bounds_1, bounds_2, num_results_per_row, num_rows):
    # GTA_risks.csv was computer from POI_risk_calculator.ipynb
    df_poi = pd.read_csv('GTA_risks.csv')
    # df_poi = df_poi[df_poi['latitude'] >= bounds_1[0]][df_poi['latitude'] <= bounds_2[0]]
    # df_poi = df_poi[df_poi['longitude'] <= bounds_1[1]][df_poi['longitude'] >= bounds_2[1]]

    destinations = random.choices(range(0, len(df_poi) - 1), k=min((num_results_per_row * num_rows), len(df_poi)))

    step_i = (bounds_2[0] - bounds_1[0]) / num_results_per_row
    step_j = (bounds_2[1] - bounds_1[1]) / num_rows

    i = np.arange(bounds_1[0], bounds_2[0], step_i)
    j = np.arange(bounds_1[1], bounds_2[1], step_j)

    if len(i) > num_results_per_row:
        i = i[:-1]

    res = ""
    dest_index = 0

    for index_i in i:
        for index_j in j:
            destination = [df_poi.iloc[destinations[dest_index]]['latitude'],
                           df_poi.iloc[destinations[dest_index]]['longitude']]

            res += queryOSRM(source=[index_i, index_j],
                             destination=destination,
                             mode_of_transit=random.choice(travel_by)) + "\n"
            dest_index += 1

            if dest_index > len(destinations):
                dest_index = 0

    return res


def get_queries_by_category(bounds_1, bounds_2, num_results_per_row, num_rows, category):
    """
    Given a source, a category and a radius, find all possible destinations within these
    restrictions. repeat for num_results_per_row * num_rows times.

    :param bounds_1: a coordinate to indicate initial bound
    :param bounds_2: a coordinate to indicate  a final bound
    :param num_results_per_row: number of columns
    :param num_rows: number of rows
    :param category: search category
    :return: string queries corresponding to these restrictions
    """

    # GTA_risks.csv was computer from POI_risk_calculator.ipynb
    df_poi = pd.read_csv('GTA_risks.csv')
    df_poi = df_poi[df_poi['latitude'] >= bounds_1[0]][df_poi['latitude'] <= bounds_2[0]]
    df_poi = df_poi[df_poi['longitude'] <= bounds_1[1]][df_poi['longitude'] >= bounds_2[1]]
    df_poi = df_poi[df_poi['top_category'] == category]

    step_i = (bounds_2[0] - bounds_1[0]) / num_results_per_row
    step_j = (bounds_2[1] - bounds_1[1]) / num_rows

    i = np.arange(bounds_1[0], bounds_2[0], step_i)
    j = np.arange(bounds_1[1], bounds_2[1], step_j)

    if len(i) > num_results_per_row:
        i = i[:-1]

    res_dict = {}
    radius = 15    # Km
    dict_index = 0
    RISKS_N = []
    RISKS_S = []
    RISKS_U = []


    for index_i in i:
        for index_j in j:
            D = []
            Q = []
            R_N = []
            R_S = []
            R_U = []

            for k in range(168):
                R_S.append([])
                R_N.append([])
                R_U.append([])

            result = ""
            df_poi['haversine_distance'] = haversine_dist(source=[index_i, index_j],
                                                          latitude=df_poi['latitude'],
                                                          longitude=df_poi['longitude'])

            destinations = df_poi[df_poi['haversine_distance'] <= radius]

            if len(destinations) > 0:
                for index, destination in destinations.iterrows():
                    dest = [destination['latitude'],
                            destination['longitude']]

                    D.append(dest)
                    result = queryOSRM(source=[index_i, index_j],
                                       destination=dest,
                                       mode_of_transit=random.choice(travel_by))
                    Q.append(result)

                    for k in range(168):
                        R_N[k].append(destination['normal_risks' + str(k)])
                        R_S[k].append(destination['skewed_risks' + str(k)])
                        R_U[k].append(destination['uniform_risks_' + str(k)])

                res_dict[dict_index] = {'source': [index_i, index_j],
                                        'destinations': D,
                                        'category': category,
                                        'queries': Q}

                for k in range(168):
                    res_dict[dict_index].update({'normal_risks' + str(k): R_N[k]})
                    res_dict[dict_index].update({'skewed_risks' + str(k): R_S[k]})
                    res_dict[dict_index].update({'uniform_risks_' + str(k): R_U[k]})

                dict_index += 1

    res = pd.DataFrame.from_dict(res_dict, "index")

    return res


results = te

# Round 1:
print("\tBegin round 1:")
category_index = random.choices(range(0, len(categories) - 1), k=min(15, len(categories)))

for ind in range(8):
    print(categories[category_index[ind]])
    results = results.append(get_queries_by_category(bounds_1=[43.669871, -79.280689],
                                                     bounds_2=[43.674519, -79.589007],
                                                     num_results_per_row=8,
                                                     num_rows=10,
                                                     category=categories[category_index[ind]]))

# Round 2:
print("\tBegin round 2:")
for ind in range(8,15):
    print(categories[category_index[ind]])
    results = results.append(get_queries_by_category(bounds_1=[43.722694, -79.221234],
                                                     bounds_2=[43.791898, -79.628495],
                                                     num_results_per_row=7,
                                                     num_rows=10,
                                                     category=categories[category_index[ind]]))

print("results length = " + str(len(results)))

print("\tBegin saving files:")
if os.path.isfile(output_results_to):
    os.remove(output_results_to)
results.to_csv(output_results_to, index=False)
