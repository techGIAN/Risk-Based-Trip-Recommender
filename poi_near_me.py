import time

import pandas as pd
import numpy as np
import webbrowser
import os

import geocoder
import folium
from Location import Location
from POI import POI
from utilityMethods import SORT_BY, ROUTE_FROM
from termcolor import colored


WEBNAME = 'templates/poi_near_me.html'
IS_DEBUG_MODE = True
IS_FULL_DEBUG_MODE = False


class POINearMe(Location):
    df_poi = pd.read_csv('Safegraph-Canada-Core-Free-10-Attributes.csv')
    radius = 25                 # in Km
    max_trip_duration = 60      # in minutes
    K_poi = 20                  # number of POIs to offer
    poi = None
    poi_category = None
    poi_list = []
    sortBy = 'haversine_distance'
    ROUTE_FROM = ROUTE_FROM.OSRM

    def __init__(self,
                 radius: int,
                 K_poi: int,
                 category: str,
                 poi=None,
                 duration:int = None,
                 sortBy: SORT_BY = SORT_BY.haversine_distance,
                 ROUTE_FROM = ROUTE_FROM.OSRM):

        if IS_DEBUG_MODE:
            print(colored('================>\nBegin initialization ', color='magenta'))

        self.ROUTE_FROM = ROUTE_FROM
        self.radius = radius
        self.K_poi = K_poi
        self.poi = poi
        self.poi_category = category
        self.source = geocoder.ip('me').latlng
        self.poi_list = []
        self.sortBy = sortBy

        if duration is not None:
            self.max_trip_duration = duration

        if IS_DEBUG_MODE:
            print(colored('\tBegin filter application', color='magenta'))

        start = time.time()
        self.__filter_by_criteria()
        end = time.time()
        print(colored("time took to process request: "+str(end-start), color='red'))

        if IS_DEBUG_MODE:
            print(colored('\tFinish filter application ', color='magenta'))
            print(colored('Finish initialization\n<================', color='magenta'))

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

    # apply distance and time filter
    def __filter_by_criteria(self):
        self.df_poi['haversine_distance'] = self.haversine_dist()

        if self.poi is not None:
            self.df_poi = self.df_poi[self.df_poi['location_name'] == self.poi]
        else:
            self.df_poi = self.df_poi[self.df_poi['top_category'] == self.poi_category]

        self.df_poi = self.df_poi[self.df_poi['haversine_distance'] <= self.radius]

        # initial filter based on haversine distance
        self.df_poi.sort_values(by=['haversine_distance'], inplace=True, ascending=True)
        self.df_poi = self.df_poi.head(self.K_poi*3).reset_index()

        # print(self.df_poi.head(self.K_poi*3))

        time = []
        distance = []

        for index, row in self.df_poi.iterrows():
            poi = POI(coordinate=[row['latitude'],
                                  row['longitude']],
                      origin=self.source,
                      isCurrentLocation=False,
                      ROUTE_FROM=self.ROUTE_FROM)
            time.append(poi.getTime())
            distance.append(poi.getDistance())
            poi.filter(dist_filter= self.radius,
                       time_filter=self.max_trip_duration)

            if not poi.isEmpty():
                self.poi_list.append(poi)

        self.df_poi['travel_time'] = time
        self.df_poi['distance'] = distance

        self.df_poi = self.df_poi[self.df_poi['distance'] <= self.radius]
        self.df_poi = self.df_poi[self.df_poi['travel_time'] <= self.max_trip_duration]

        # print(self.df_poi[['travel_time', 'distance', 'haversine_distance']])

        if IS_DEBUG_MODE and IS_FULL_DEBUG_MODE:
            print(self.df_poi[['latitude','longitude','travel_time', 'distance', 'haversine_distance']])

        if self.sortBy == SORT_BY.Distance:
            self.df_poi.sort_values(by=['distance'], inplace=True, ascending=True)
        elif self.sortBy == SORT_BY.Time:
            self.df_poi.sort_values(by=['travel_time'], inplace=True, ascending=True)
        elif self.sortBy == SORT_BY.haversine_distance:
            self.df_poi.sort_values(by=['haversine_distance'], inplace=True, ascending=True)

        self.df_poi = self.df_poi.head(self.K_poi).reset_index()
        print(self.df_poi[['travel_time', 'distance', 'haversine_distance']])
        if IS_DEBUG_MODE and IS_FULL_DEBUG_MODE:
            print(self.df_poi[['travel_time', 'distance', 'haversine_distance']])

    def graphPOIs(self):
        m = folium.Map(location=self.source, zoom_start=14)

        folium.Marker(
            location=self.source,
            popup='Source',
            tooltip='<strong>Source</strong>',
            icon=folium.Icon(color='red', prefix='fa', icon='home')
        ).add_to(m)

        # for i in range(self.K_poi):
        for index, point_of_interest in self.df_poi.iterrows():
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
        webbrowser.open_new_tab(path_to_open)


p = POINearMe(radius=20,
              K_poi=5,
              poi=None,
              duration=60,
              category="Grocery Stores",
              sortBy=SORT_BY.Distance,
              ROUTE_FROM=ROUTE_FROM.OSRM)
p.graphPOIs()
time.sleep(5)
p = POINearMe(radius=20,
              K_poi=5,
              poi=None,
              duration=60,
              category="Grocery Stores",
              sortBy=SORT_BY.Distance,
              ROUTE_FROM=ROUTE_FROM.GRASS_HOPPER)
p.graphPOIs()
p = POINearMe(radius=20,
              K_poi=5,
              poi=None,
              duration=60,
              category="Grocery Stores",
              sortBy=SORT_BY.haversine_distance,
              ROUTE_FROM=ROUTE_FROM.GRASS_HOPPER)
p.graphPOIs()