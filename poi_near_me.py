# basic imports
import pandas as pd
import numpy as np
import webbrowser
import os

import geocoder
import folium

from Location import Location

WEBNAME = 'templates/poi_near_me.html'


class POINearMe(Location):
    df_poi = pd.read_csv('Safegraph-Canada-Core-Free-10-Attributes.csv')
    radius = 25
    unit = 'km'
    K_poi = 20
    poi = None
    poi_category = None

    def __init__(self, radius, unit, K_poi, poi, category):

        self.radius = radius
        self.unit = unit
        self.K_poi = K_poi
        self.poi = poi
        self.poi_category = category
        self.source = geocoder.ip('me').latlng

        latitude1 = self.source[0]
        longitude1 = self.source[1]

        self.df_poi['haversine_distance'] = self.haversine_dist()

        if self.poi is not None:
            self.df_poi = self.df_poi[self.df_poi['location_name'] == self.poi]
        else:
            self.df_poi = self.df_poi[self.df_poi['top_category'] == self.poi_category]

        self.df_poi = self.df_poi[self.df_poi['haversine_distance'] < self.radius]

        self.df_poi = self.df_poi.sort_values('haversine_distance')
        self.df_poi = self.df_poi.head(self.K_poi).reset_index()

    def haversine_dist(self):
        R = 6373.0
        lat1 = np.deg2rad(self.source[0])
        lon1 = np.deg2rad(self.source[1])
        lat2 = np.deg2rad(self.df_poi['latitude'])
        lon2 = np.deg2rad(self.df_poi['longitude'])
        d_lon = lon2 - lon1
        d_lat = lat2 - lat1
        d = np.sin(d_lat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(d_lon / 2) ** 2
        cons = 2 * np.arctan2(np.sqrt(d), np.sqrt(1 - d))
        return R * cons

    def graphPOIs(self):
        m = folium.Map(location=self.source, zoom_start=14)

        folium.Marker(
            location=self.source,
            popup='Source',
            tooltip='<strong>Source</strong>',
            icon=folium.Icon(color='red', prefix='fa', icon='home')
        ).add_to(m)

        for i in range(self.K_poi):
            point_of_interest = self.df_poi.iloc[i]
            poi_coords = [point_of_interest['latitude'], point_of_interest['longitude']]
            poi_name = point_of_interest['location_name']
            folium.Marker(
                location=poi_coords,
                popup=poi_name,
                tooltip='<strong>' + poi_name + '</strong>',
                icon=folium.Icon(color='blue', prefix='fa', icon='shopping-cart')
            ).add_to(m)

        m.save(WEBNAME)
        path_to_open = 'file:///' + os.getcwd() + '/' + WEBNAME
    # webbrowser.open_new_tab(path_to_open)

# p = POINearMe(radius=30, unit="km", K_poi=20, poi=None, category="Grocery Stores")
# p.graphPOIs()
