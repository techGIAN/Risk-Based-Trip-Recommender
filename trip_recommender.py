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

# map imports
import geopandas
import fiona
import shapely
import rtree
import pyproj
# import polyline
from osgeo import gdal
import asyncio
# import osrm
from geopy.geocoders import Nominatim
import pgeocode
import geocoder

# from ipyleaflet import Map, Marker, CircleMarker
import folium
from branca.element import Figure
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# constants
color_list = [
    # 'red',
    # 'blue',
    'gray',
    'darkred',
    'lightred',
    'orange',
    # 'beige',
    'green',
    'darkgreen',
    # 'lightgreen',
    'darkblue',
    'lightblue',
    'purple',
    'darkpurple',
    # 'pink',
    'cadetblue',
    # 'lightgray'
    # 'black'
]
geoloc = Nominatim(user_agent='TripRecApp')
geolocation = RateLimiter(geoloc.geocode, min_delay_seconds=2, return_value_on_exception=None)

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

parameters['origin'] = geocoder.ip('me').latlng
parameters['specific_poi'] = True if 'yes' else False
parameters['trip_count'] = int(parameters['trip_count'])


# HELPER METHODS

# list of path points of alternative routes
def get_path_points(q, num_of_routes=1):
    urllib.request.urlretrieve(q, "query.json")
    routing_file = open('query.json', )

    # obtain the coordinates of the points along the path as suggested by osrm
    routing_data = json.load(routing_file)

    routes = []
    m_min = min(num_of_routes, len(routing_data['routes']))

    dist_tags = []
    duration_tags = []

    for i in range(m_min):
        path_points = routing_data['routes'][i]['geometry']['coordinates']
        dist_tags.append(round(routing_data['routes'][i]['distance'] / 1000.0,2))
        duration_tags.append(round(routing_data['routes'][i]['duration'] / 60.0,2))

        # swap the coordinates
        for point in path_points:
            temp = point[0]
            point[0] = point[1]
            point[1] = temp
        routes.append(path_points)

    # Close and delete file
    routing_file.close()
    os.remove('query.json')

    return routes, dist_tags, duration_tags


# gets the geocoordinates of a location
# requires either one of postal code or address
# note: postal code takes precedence
def get_coordinates(p_code, ad):
    coords = [0.0, 0.0]
    if p_code != '':
        country_code = pgeocode.Nominatim('ca')
        postal_data = country_code.query_postal_code(p_code)
        lat = postal_data['latitude']
        lon = postal_data['longitude']
    else:
        locale = geoloc(ad)
        lat = locale['latitde']
        lon = locale['longitude']
    coords = [lat, lon]
    return coords


# returns a random color from the list
def rnd_color():
    r = rnd.randint(0, len(color_list))
    return color_list.pop(r)


# retrieve coordinates of user's and desired destination
src_coords = parameters['origin']
tgt_coords = get_coordinates(parameters['postal_code'], parameters['address'])
mid = [(src_coords[0] + tgt_coords[0]) / 2, (src_coords[1] + tgt_coords[1]) / 2]

# note: osrm wants (lon, lat)
src_str = str(src_coords[1]) + ',' + str(src_coords[0])
tgt_str = str(tgt_coords[1]) + ',' + str(tgt_coords[0])

# Retrieve the query and then save onto a json file
# Although 'foot' does not work in demo service. They only have driving options
query = 'http://router.project-osrm.org/route/v1/foot/' + src_str + ';' + tgt_str + '?alternatives=true&geometries=geojson&overview=full'

src_poi = 'Origin'
tgt_poi = 'Destination'

m = folium.Map(location=mid, zoom_start=14)

# markers
folium.Marker(
    location=src_coords,
    popup=src_poi,
    tooltip='<strong>' + src_poi + '</strong>',
    icon=folium.Icon(color='blue', prefix='fa', icon='home')
).add_to(m)
folium.Marker(
    location=tgt_coords,
    popup=tgt_poi,
    tooltip='<strong>' + tgt_poi + '</strong>',
    icon=folium.Icon(color='red', prefix='fa', icon='star')
).add_to(m)

path_list, distances, durations = get_path_points(query, int(parameters['trip_count']))

# for i in range(len(path_list)):
for i in reversed(range(len(path_list))):
    pts = path_list[i]
    trip_name = 'OSRM Trip ' + str(i + 1) + '<br>' + \
                str(distances[i]) + 'Km<br>' + \
                str(durations[i]) + ' min'

    # rand_color = 'red'
    rand_color = 'darkblue'
    opacity_val = 0.3
    if i == 0:
        # rand_color = rnd_color()
        rand_color = 'darkblue'
        opacity_val = 1

    fg = folium.FeatureGroup(trip_name)
    trip = folium.vector_layers.PolyLine(
        pts,
        popup='<b>' + trip_name + '</b>',
        tooltip=trip_name,
        color=rand_color,
        weight=10,
        opacity=opacity_val
    ).add_to(fg)

    fg.add_to(m)
folium.LayerControl().add_to(m)

webname = 'recommender.html'
m.save(webname)
path_to_open = 'file:///' + os.getcwd() + '/' + webname
webbrowser.open_new_tab(path_to_open)
