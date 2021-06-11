# basic imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlb
import time
import xml.etree.ElementTree as et
import webbrowser
import os
import urllib.request  
from IPython.display import display
import json
import random as rnd
import sys

import geocoder
import folium

curr_loc = geocoder.ip('me').latlng
# curr_loc = [43.7869439,-79.4366317]

# import SafeGraph data containing core-poi
df_poi = pd.read_csv('Safegraph-Canada-Core-Free-10-Attributes.csv')

def haversine_dist(lat1, lon1, lat2, lon2):
	R = 6373.0
	lat1 = np.deg2rad(lat1)
	lon1 = np.deg2rad(lon1)
	lat2 = np.deg2rad(lat2)
	lon2 = np.deg2rad(lon2)
	d_lon = lon2 - lon1
	d_lat = lat2 - lat1
	d = np.sin(d_lat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(d_lon / 2)**2
	cons = 2 * np.arctan2(np.sqrt(d), np.sqrt(1-d))
	return R * cons

# grab query/parameters
# query_file = sys.argv[1]
query_file = 'query.txt'
parameters = dict()
with open(query_file) as qf:
	for line in qf:
		line = line.strip()
		if line == '' or line[0] == '#':
			continue
		parameter = line.split('=')
		parameter[0] = parameter[0].strip()
		parameter[1] = parameter[1].strip()
		parameter[1] = '' if parameter[1] == 'None' else parameter[1]
		parameters[parameter[0]] = parameter[1]

parameters['origin'] = curr_loc
parameters['specific_poi'] = True if 'yes' else False
parameters['trip_count'] = int(parameters['trip_count'])
parameters['radius'] = int(parameters['radius'])
parameters['K_poi'] = int(parameters['K_poi'])

latitude1 = curr_loc[0]
longitude1 = curr_loc[1]
df_poi['haversine_distance'] = haversine_dist(latitude1, longitude1, df_poi['latitude'], df_poi['longitude'])

if parameters['poi'] != '':
    df_poi = df_poi[df_poi['location_name'] == parameters['poi']]
else:
    df_poi = df_poi[df_poi['top_category'] == parameters['poi_category']]

df_poi = df_poi[df_poi['haversine_distance'] < parameters['radius']]

df_poi = df_poi.sort_values('haversine_distance')
df_poi = df_poi.head(parameters['K_poi']).reset_index()

m = folium.Map(location=curr_loc, zoom_start=14)

folium.Marker(
	location=curr_loc,
	popup='Source',
	tooltip='<strong>Source</strong>',
	icon=folium.Icon(color='red', prefix='fa', icon='home')
).add_to(m)


for i in range(parameters['K_poi']):
    point_of_interest = df_poi.iloc[i]
    poi_coords = [point_of_interest['latitude'], point_of_interest['longitude']]
    poi_name = point_of_interest['location_name']
    folium.Marker(
        location=poi_coords,
        popup=poi_name,
        tooltip='<strong>' + poi_name + '</strong>',
        icon=folium.Icon(color='blue', prefix='fa', icon='shopping-cart')
    ).add_to(m)

webname = 'templates/poi_near_me.html'
m.save(webname)
path_to_open = 'file:///' + os.getcwd() + '/' + webname
webbrowser.open_new_tab(path_to_open)