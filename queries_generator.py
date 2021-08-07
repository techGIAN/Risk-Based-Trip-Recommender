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
categories = ['Specialized Freight Trucking',
              'Restaurants and Other Eating Places',
              'Building Equipment Contractors', 'Grocery Stores',
              'Promoters of Performing Arts, Sports, and Similar Events',
              'Automotive Parts, Accessories, and Tire Stores',
              'Motion Picture and Video Industries',
              'Health and Personal Care Stores', 'Amusement Parks and Arcades',
              'Nursing Care Facilities (Skilled Nursing Facilities)',
              'Other Amusement and Recreation Industries', 'Clothing Stores',
              'Traveler Accommodation',
              'Lawn and Garden Equipment and Supplies Stores',
              'Home Furnishings Stores', 'Other Personal Services',
              'Accounting, Tax Preparation, Bookkeeping, and Payroll Services',
              'Other Miscellaneous Store Retailers',
              'Offices of Other Health Practitioners', 'Offices of Physicians',
              'Museums, Historical Sites, and Similar Institutions',
              'Lessors of Real Estate', 'Drinking Places (Alcoholic Beverages)',
              'Specialty (except Psychiatric and Substance Abuse) Hospitals',
              'Building Material and Supplies Dealers',
              'Activities Related to Real Estate',
              'General Medical and Surgical Hospitals', 'Spectator Sports',
              'Florists',
              'Hardware, and Plumbing and Heating Equipment and Supplies Merchant Wholesalers',
              'Electronics and Appliance Stores', 'Shoe Stores',
              'Book Stores and News Dealers', 'Offices of Dentists',
              'Sporting Goods, Hobby, and Musical Instrument Stores',
              'Personal Care Services', 'Other Financial Investment Activities',
              'Other Schools and Instruction',
              'Printing and Related Support Activities',
              'Offices of Real Estate Agents and Brokers',
              'Jewelry, Luggage, and Leather Goods Stores',
              'Couriers and Express Delivery Services', 'Death Care Services',
              'Activities Related to Credit Intermediation',
              'Foundation, Structure, and Building Exterior Contractors',
              'Gasoline Stations',
              'Machinery, Equipment, and Supplies Merchant Wholesalers',
              'Automotive Repair and Maintenance', 'Specialty Food Stores',
              'Other Professional, Scientific, and Technical Services',
              'General Merchandise Stores, including Warehouse Clubs and Supercenters',
              'Automobile Dealers', 'Furniture Stores', 'Special Food Services',
              'Personal and Household Goods Repair and Maintenance',
              'Consumer Goods Rental', 'Other Ambulatory Health Care Services',
              'Postal Service', 'Religious Organizations',
              'Office Supplies, Stationery, and Gift Stores',
              'Building Finishing Contractors', 'Beer, Wine, and Liquor Stores',
              'Colleges, Universities, and Professional Schools',
              "Drugs and Druggists' Sundries Merchant Wholesalers",
              'Travel Arrangement and Reservation Services',
              'Electronic and Precision Equipment Repair and Maintenance',
              'Continuing Care Retirement Communities and Assisted Living Facilities for the Elderly',
              'Bakeries and Tortilla Manufacturing',
              'Agencies, Brokerages, and Other Insurance Related Activities',
              'Used Merchandise Stores', 'Depository Credit Intermediation',
              'Warehousing and Storage',
              'Management, Scientific, and Technical Consulting Services',
              'Architectural, Engineering, and Related Services',
              'Miscellaneous Durable Goods Merchant Wholesalers',
              'Automotive Equipment Rental and Leasing',
              'Other Motor Vehicle Dealers',
              'Advertising, Public Relations, and Related Services',
              'Investigation and Security Services',
              'Support Activities for Air Transportation',
              'Social Advocacy Organizations', 'Department Stores',
              'Legal Services', 'Gambling Industries',
              'Remediation and Other Waste Management Services',
              'Insurance Carriers',
              'Coating, Engraving, Heat Treating, and Allied Activities',
              'RV (Recreational Vehicle) Parks and Recreational Camps',
              'Beverage Manufacturing',
              'Support Activities for Road Transportation',
              'Home Health Care Services', 'Household Appliance Manufacturing',
              'Drycleaning and Laundry Services',
              'Other Miscellaneous Manufacturing', 'Rail Transportation',
              'Wired and Wireless Telecommunications Carriers',
              'Utility System Construction', 'Individual and Family Services',
              'Sound Recording Industries',
              'Lumber and Other Construction Materials Merchant Wholesalers',
              'Household Appliances and Electrical and Electronic Goods Merchant Wholesalers',
              'Other Information Services',
              'Commercial and Industrial Machinery and Equipment Rental and Leasing',
              'Urban Transit Systems', 'Outpatient Care Centers',
              'Child Day Care Services', 'Residential Building Construction',
              'Business Schools and Computer and Management Training',
              'Other Transit and Ground Passenger Transportation',
              'Glass and Glass Product Manufacturing',
              'Waste Treatment and Disposal',
              'Justice, Public Order, and Safety Activities',
              'Miscellaneous Nondurable Goods Merchant Wholesalers',
              'Nondepository Credit Intermediation',
              'Motor Vehicle Manufacturing',
              'Motor Vehicle and Motor Vehicle Parts and Supplies Merchant Wholesalers',
              'Medical and Diagnostic Laboratories', 'Performing Arts Companies',
              'Waste Collection', 'Employment Services',
              'Apparel Accessories and Other Apparel Manufacturing',
              'Management of Companies and Enterprises',
              'Elementary and Secondary Schools',
              'Greenhouse, Nursery, and Floriculture Production',
              'Services to Buildings and Dwellings',
              'Executive, Legislative, and Other General Government Support',
              'Petroleum and Petroleum Products Merchant Wholesalers',
              'National Security and International Affairs',
              'Grantmaking and Giving Services', 'Inland Water Transportation',
              'Administration of Economic Programs',
              'Data Processing, Hosting, and Related Services',
              'Scenic and Sightseeing Transportation, Land',
              'Metal and Mineral (except Petroleum) Merchant Wholesalers',
              'Clay Product and Refractory Manufacturing',
              'Other Specialty Trade Contractors',
              'Freight Transportation Arrangement',
              'Grocery and Related Product Merchant Wholesalers',
              'Taxi and Limousine Service',
              'Interurban and Rural Bus Transportation']


def get_queries(bounds_1, bounds_2, num_results_per_row, num_rows):
    # GTA_risks.csv was computer from POI_risk_calculator.ipynb
    df_poi = pd.read_csv('GTA_risks.csv')
    df_poi = df_poi[df_poi['latitude'] >= bounds_1[0]][df_poi['latitude'] <= bounds_2[0]]
    df_poi = df_poi[df_poi['longitude'] <= bounds_1[1]][df_poi['longitude'] >= bounds_2[1]]

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

    res = pd.DataFrame(columns=['source', 'destination', 'category', 'query'])
    res_dict = {}
    radius = 25    # Km
    dict_index = 0

    for index_i in i:
        for index_j in j:
            result = ""
            df_poi['haversine_distance'] = haversine_dist(source=[index_i, index_j],
                                                          latitude=df_poi['latitude'],
                                                          longitude=df_poi['longitude'])

            destinations = df_poi[df_poi['haversine_distance'] <= radius]

            for index, destination in destinations.iterrows():
                dest = [destination['latitude'],
                        destination['longitude']]

                result = queryOSRM(source=[index_i, index_j],
                                   destination=dest,
                                   mode_of_transit=random.choice(travel_by))
                res_dict[dict_index] = {'source': [index_i, index_j],
                                        'destination': dest,
                                        'category': category,
                                        'query': result}
                dict_index += 1

    res = pd.DataFrame.from_dict(res_dict, "index")

    return res


results = pd.DataFrame(columns=['source', 'destination', 'category', 'query'])

# Round 1:
print("\tBegin round 1:")
category_index = random.choices(range(0, len(categories) - 1), k=min(15, len(categories)))

for ind in range(10):
    results = results.append(get_queries_by_category(bounds_1=[43.722694, -79.221234],
                                                     bounds_2=[43.791898, -79.628495],
                                                     num_results_per_row=15,
                                                     num_rows=5,
                                                     category=categories[category_index[ind]]))

# Round 2:
print("\tBegin round 2:")

for ind in range(10,15):
    results = results.append(get_queries_by_category(bounds_1=[43.669871, -79.280689],
                                                     bounds_2=[43.674519, -79.589007],
                                                     num_results_per_row=5,
                                                     num_rows=5,
                                                     category=categories[category_index[ind]]))
print("results length = " + str(len(results)))

print("\tBegin saving files:")
if os.path.isfile(output_results_to):
    os.remove(output_results_to)
results.to_csv(output_results_to, index=False)
