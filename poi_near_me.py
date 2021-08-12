import time
import pandas as pd
import numpy as np
import webbrowser
import os
import json

from folium.plugins import MarkerCluster
import folium
from Location import Location
from POI import POI
from utilityMethods import SORT_BY, ROUTE_FROM, haversine_dist
from termcolor import colored

from datetime import datetime as dt
from optimizer import Optimizer
from IconMapper import IconMapper

IS_DEBUG_MODE = True
IS_FULL_DEBUG_MODE = False

from folium.utilities import validate_location

WEBNAME = 'templates/poi_near_me.html'
pd.options.mode.chained_assignment = None


class POINearMe(Location):
    # df_poi = pd.read_csv('Safegraph-Canada-Core-Free-10-Attributes.csv')
    # df_poi = pd.read_csv('ca_poi_rrisks_2021-04-19-one-week.csv')  # treat it as a constant
    df_poi = pd.read_csv('GTA_risks.csv')  # treat it as a constant
    df_past_queries = None
    radius = 25  # in Km
    max_trip_duration = 60  # in minutes
    K_poi = 20  # number of POIs to offer
    poi_category = None
    poi_list = []
    sortBy = SORT_BY.haversine_distance
    ROUTE_FROM = ROUTE_FROM.OSRM
    travel_by = 'car'
    poi_results = None
    map_val = {
        'center_marker': None,
        'markers': None
    }

    # ct = dt.now()
    # hr = ct.weekday()*24 + ct.hour
    # # hr = 159 # tester for Nofrills at Yonge/Steeles
    # risk_attribute = 'poiRisk_' + str(hr)
    ct = None
    hr = None
    # risk_attribute = ''

    risk_attribute_normal = ''
    risk_attribute_skewed = ''
    risk_attribute_uniform = ''

    def __init__(self,
                 origin,
                 radius: int,
                 K_poi: int,
                 category: str,
                 duration: int = None,
                 sortBy: SORT_BY = SORT_BY.haversine_distance,
                 ROUTE_FROM=ROUTE_FROM.OSRM,
                 travel_by='car',
                 IS_DEBUG_MODE=False,
                 IS_FULL_DEBUG_MODE=False,
                 is_time_now=True,
                 time_later_val=None):

        self.update_request(origin,
                            radius=radius,
                            K_poi=K_poi,
                            category=category,
                            duration=duration,
                            sortBy=sortBy,
                            ROUTE_FROM=ROUTE_FROM,
                            travel_by=travel_by,
                            IS_DEBUG_MODE=IS_DEBUG_MODE,
                            IS_FULL_DEBUG_MODE=IS_FULL_DEBUG_MODE,
                            is_time_now=is_time_now,
                            time_later_val=time_later_val)

    def update_request(self,
                       origin,
                       radius: int,
                       K_poi: int,
                       category: str,
                       duration: int = None,
                       sortBy: SORT_BY = SORT_BY.haversine_distance,
                       ROUTE_FROM=ROUTE_FROM.OSRM,
                       travel_by='car',
                       IS_DEBUG_MODE=False,
                       IS_FULL_DEBUG_MODE=False,
                       is_time_now=True,
                       time_later_val=None):

        if IS_DEBUG_MODE:
            print(colored('================>\nBegin initialization ', color='magenta'))

        self.travel_by = travel_by
        self.ROUTE_FROM = ROUTE_FROM
        self.radius = radius
        self.K_poi = K_poi
        self.poi_category = category
        self.source = super().get_coordinates(origin)
        self.poi_list = []
        self.sortBy = sortBy
        self.IS_DEBUG_MODE = IS_DEBUG_MODE
        self.IS_FULL_DEBUG_MODE = IS_FULL_DEBUG_MODE
        self.time_now = is_time_now
        self.time_later_value = time_later_val

        self.ct = dt.now()
        if not self.time_now:
            frmt = '%Y-%m-%d %H:%M'
            arry = str(self.time_later_value).split('T')
            mod_str_dt = arry[0] + ' ' + arry[1]
            self.ct = dt.strptime(mod_str_dt, frmt)

        self.hr = self.ct.weekday() * 24 + self.ct.hour
        # hr = 159 # tester for Nofrills at Yonge/Steeles
        # self.risk_attribute = 'poiRisk_' + str(self.hr)
        self.risk_attribute_normal = 'normal_risks' + str(self.hr)
        self.risk_attribute_skewed = 'skewed_risks' + str(self.hr)
        self.risk_attribute_uniform = 'uniform_risks_' + str(self.hr)

        if duration is not None:
            self.max_trip_duration = duration

        if self.IS_DEBUG_MODE:
            print(colored('\tBegin filter application', color='magenta'))

        start = time.time()

        self.df_poi['haversine_distance'] = haversine_dist(source=self.source,
                                                           latitude=self.df_poi['latitude'],
                                                           longitude=self.df_poi['longitude'])

        # No need to use __update_pois as the trip is saved in trip_recommender
        # and the subsections are saved in utilityMethods
        # self.__update_pois()

        self.__filter_by_criteria()

        self.__filter()

        end = time.time()
        print(colored("time took to process request: " + str(round((end - start) / 60, 2)) + " min", color='red'))

        if self.IS_DEBUG_MODE:
            print(colored('\tFinish filter application ', color='magenta'))
            print(colored('Finish initialization\n<================', color='magenta'))

    # Make sure to keep self.df_poi unchanged as it takes time to reload the file
    # The program saves the initial results in self.poi_results
    def __filter_by_criteria(self):
        self.poi_results = self.df_poi.copy()
        self.poi_results = self.poi_results[self.poi_results['top_category'] == self.poi_category]

        print(colored("len(self.df_poi) = " + str(len(self.df_poi[self.df_poi['top_category'] == self.poi_category])), "red"))
        print(colored(self.df_poi[self.df_poi['top_category'] == self.poi_category]['haversine_distance'], 'red'))

        # add a general filter of haversine_distance distance from origin
        self.poi_results = self.poi_results[self.poi_results['haversine_distance'] <= self.radius]
        self.poi_results = self.poi_results.reset_index()

        print(colored("\tnumber of results to consider: " + str(len(self.poi_results)), "cyan"))
        if len(self.poi_results) == 0:
            raise Exception("Sorry, no results where found!")

        duration = []
        distance = []
        path_risk = []
        normal, skewed, uniform , avg_risk= [], [], [], []

        # Cannot remove duplicates because the
        # Remove duplicates
        # if current_pois is not None:
        #     self.poi_results = self.poi_results[~self.poi_results['placekey'].isin(current_pois['placekey'])]
        #     print(colored("\tnumber of results to consider after reduction: " + str(len(self.poi_results)), "cyan"))

        for index, row in self.poi_results.iterrows():
            while True:
                try:
                    poi = POI(coordinate=[row['latitude'],
                                          row['longitude']],
                              origin=self.source,
                              ROUTE_FROM=self.ROUTE_FROM,
                              IS_DEBUG_MODE=self.IS_DEBUG_MODE,
                              IS_FULL_DEBUG_MODE=self.IS_FULL_DEBUG_MODE,
                              mode_of_transit=self.travel_by,
                              is_time_now=self.time_now,
                              time_later_val=self.time_later_value,
                              hour=self.hr,
                              row=row,
                              sort_by=self.sortBy)

                    duration.append(poi.getTime())
                    distance.append(poi.getDistance())
                    path_risk.append(poi.risk_of_paths)
                    normal.append(poi.get_normal_risk())
                    skewed.append(poi.get_skewed_risk())
                    uniform.append(poi.get_uniform_risk())
                    avg_risk.append((poi.get_normal_risk()+poi.get_skewed_risk()+poi.get_uniform_risk())/3)

                    if not poi.isEmpty():
                        self.poi_list.append(poi)
                    break
                except Exception as e:
                    print(colored("\t\tAn ERROR occured: " + str(e), "red"))
                    time.sleep(1)

        self.poi_results['travel_time'] = duration
        self.poi_results['distance'] = distance
        self.poi_results['path_risk'] = path_risk
        self.poi_results['normal_poi_risk'] = normal
        self.poi_results['skewed_poi_risk'] = skewed
        self.poi_results['uniform_poi_risk'] = uniform
        self.poi_results['average_poi_risk'] = avg_risk

        # if current_pois is not None:
        #     current_pois = pd.merge(current_pois, self.df_poi, on='placekey')
        #     self.poi_results = self.poi_results.append(current_pois, ignore_index=True)
        #     self.poi_results.reset_index
        #     print(colored("\tagain total number of resuls: " + str(len(self.poi_results)), "cyan"))

    # Filter based on distance, time, or risk
    def __filter(self):
        print(colored("\t\tAbout to filter results: ", "magenta"))

        self.poi_results = self.poi_results[self.poi_results['distance'] <= self.radius]
        self.poi_results = self.poi_results[self.poi_results['travel_time'] <= self.max_trip_duration]

        if self.sortBy == SORT_BY.Distance:
            self.poi_results.sort_values(by=['distance'], ignore_index=True, inplace=True, ascending=True)

        elif self.sortBy == SORT_BY.Time:
            self.poi_results.sort_values(by=['travel_time'], ignore_index=True, inplace=True, ascending=True)

        elif self.sortBy == SORT_BY.POIScore:
            df_sub = pd.DataFrame(columns=['travel_time', 'distance', 'path_risk', 'average_poi_risk'])
            df_sub[['travel_time', 'distance', 'path_risk', 'average_poi_risk']] = self.poi_results[
                ['travel_time', 'distance', 'path_risk', 'average_poi_risk']]
            op = Optimizer()
            v = op.opt(np_array=df_sub.to_numpy())
            self.poi_results['poi_score'] = v[0] * self.poi_results['travel_time'] + \
                                            v[1] * self.poi_results['distance'] + \
                                            v[2] * self.poi_results['path_risk'] + \
                                            v[3] * self.poi_results['average_poi_risk']

            self.poi_results.sort_values(by=['poi_score'], ignore_index=True, inplace=True, ascending=True)
        else:
            # sort by risk
            df_sub = pd.DataFrame(columns=['path_risk', 'average_poi_risk'])
            df_sub[['path_risk', 'average_poi_risk']] = self.poi_results[
                ['path_risk', 'average_poi_risk']]
            op = Optimizer()
            v = op.opt(np_array=df_sub.to_numpy())
            self.poi_results['total_trip_risk'] = v[0] * self.poi_results['path_risk'] + \
                                                  v[1] * self.poi_results['average_poi_risk']

            self.poi_results.sort_values(by=['total_trip_risk'], ignore_index=True, inplace=True, ascending=True)

        self.poi_results = self.poi_results.head(self.K_poi).reset_index()
        print(colored("\t\tnumber of results after filtering: " + str(len(self.poi_results)), "magenta"))
        # print(colored("1. poi results after filtering: \n" + str(self.poi_results) , "cyan"))

    # # Pull out an existing query if it exists, update it if necessary.
    # # Add query and its results otherwise
    # # columns: Source [longitude, latitude] not None,
    # #          category [from sg] not None,
    # #          modeOfTransit [car/foot/bike] not None,
    # #          route_from not None,
    # #               // pois filtered by haversine distance
    # #          search radius not None,
    # #          poi [{poi:{placekey, distance, time, risk}}...] not None,
    # #          primary key(Source, category, modeOfTransit, route_from)
    # def __update_pois(self):
    #     self.poi_results = None
    #     add_new_row = False
    #
    #     if os.path.isfile('df_past_queries.csv'):
    #         self.df_past_queries = pd.read_csv('df_past_queries.csv')
    #
    #         row = self.df_past_queries[(self.df_past_queries['source'] == str(self.source)) &
    #                                    (self.df_past_queries['top_category'] == self.poi_category) &
    #                                    (self.df_past_queries['modeOfTransit'] == self.travel_by) &
    #                                    (self.df_past_queries['route_from'] == "ROUTE_FROM." + str(
    #                                        self.ROUTE_FROM.name))]
    #
    #         # A past query already exists - either fetch results or update it
    #         if len(row) > 0:
    #             index = row.index.values[0]
    #
    #             # need to increase search radius to account for additional information
    #             if self.radius > row.iloc[0]['search_radius']:
    #                 print("\tNEED TO INCREASE RADIUS SEARCH")
    #                 current_pois = pd.read_json(row['poi'][index])
    #                 try:
    #                     self.__filter_by_criteria(current_pois=current_pois)
    #                 except Exception as e:
    #                     if str(e) != "Location based indexing can only have [integer, integer slice (START point is " \
    #                                  "INCLUDED, END point is EXCLUDED), listlike of integers, boolean array] types":
    #                         print(colored("\t\tERROR! " + str(e), "red"))
    #                         print(colored("\t\t" + str(self.poi_results), "red"))
    #
    #                 df = self.poi_results[['placekey', 'travel_time', 'distance']]
    #
    #                 # update existing row
    #                 self.df_past_queries['search_radius'][index] = self.radius
    #                 self.df_past_queries['poi'][index] = df.to_json()
    #
    #             # fetch pois from the row and store it in the class instance as a dataframe
    #             self.poi_results = pd.read_json(row['poi'][index])
    #
    #         # there is no entry - need to compute and add an new entry
    #         else:
    #             self.__filter_by_criteria()
    #             add_new_row = True
    #
    #     # Need to create a file
    #     else:
    #         self.df_past_queries = pd.DataFrame(columns=['source', 'top_category', 'modeOfTransit', 'route_from',
    #                                                      'search_radius', 'poi'])
    #         self.__filter_by_criteria()
    #         add_new_row = True
    #
    #     # add query file:
    #     if add_new_row:
    #         df = self.poi_results[['placekey', 'travel_time', 'distance']]
    #         row = pd.DataFrame({'source': [self.source], 'top_category': [self.poi_category],
    #                             'modeOfTransit': [self.travel_by], 'route_from': [self.ROUTE_FROM],
    #                             'search_radius': [self.radius], 'poi': [df.to_json()]})
    #
    #         self.df_past_queries = self.df_past_queries.append(row)
    #
    #     # save file:
    #     self.df_past_queries.to_csv('df_past_queries.csv', index=False)
    #
    #     # apply filtering based on Distance, Time, or Risk
    #     self.__filter()

    def graphPOIs(self):
        self.results_html = ''
        m = folium.Map(location=self.source, zoom_start=14)

        self.map_val['center_marker'] = folium.Marker(
            location=self.source,
            popup='Source',
            tooltip='<strong>Source</strong>',
            icon=folium.Icon(color='red', prefix='fa', icon='home')
        )
        self.map_val['center_marker'].add_to(m)

        im = IconMapper()

        coords = []
        popups = []
        tooltip_strings = []
        icons = []

        # for i in range(self.K_poi):
        for index, point_of_interest in self.poi_results.iterrows():
            poi_coords = [
                self.df_poi[self.df_poi['placekey'] == point_of_interest['placekey']].loc[:, 'latitude'].values[0],
                self.df_poi[self.df_poi['placekey'] == point_of_interest['placekey']].loc[:, 'longitude'].values[0]]

            poi_name = \
                self.df_poi[self.df_poi['placekey'] == point_of_interest['placekey']].loc[:, 'location_name'].values[0]

            self.results_html += "<button id='recenter_poi' onclick='recenter_poi(" + str(poi_coords) + ")' >" + \
                                 str(index + 1) + ". " + poi_name + ":" \
                                 '<div style="padding-left:20px;">normal poi risk:' + \
                                 str(round(point_of_interest['normal_poi_risk'], 2)) + '</div>' \
                                '<div style="padding-left:20px;">skewed poi risk:' + \
                                 str(round(point_of_interest['skewed_poi_risk'], 2)) + '</div>' \
                                '<div style="padding-left:20px;">uniform poi risk:' + \
                                 str(round(point_of_interest['uniform_poi_risk'], 2)) + '</div>' \
                                '<div style="padding-left:20px;">time:' + \
                                 str(round(point_of_interest['travel_time'], 2)) + ' min</div>' \
                                 '<div style="padding-left:20px;">distance: ' + \
                                 str(round(point_of_interest['distance'], 2)) + 'Km</div></button>'

            query = None
            if self.time_now:
                query = "mode_of_transit=" + str(self.travel_by) + "&origin=" + str(
                    self.source) + "&destination=" + str(poi_coords) + \
                        "&time=time_now&date_time=&submit_paths=Submit#"
            else:
                query = "mode_of_transit=" + str(self.travel_by) + "&origin=" + str(
                    self.source) + "&destination=" + str(poi_coords) + \
                        "&time=time_later&date_time=" + str(self.time_later_value) + "&submit_paths=Submit#"

            popup = f"""<p> {poi_name}</p> 
                     <p><button type='button' id='poi_button' onclick="create_trip('{query}');" >go there</button></p>
                  """

            if self.sortBy == SORT_BY.Distance:
                tooltip_string = '<br><strong> DDist: </strong>' + str(round(point_of_interest['distance'], 2)) + ' km'
            elif self.sortBy == SORT_BY.Time:
                tooltip_string = '<br><strong> Time: </strong>' + str(
                    round(point_of_interest['travel_time'], 2)) + ' min'
            elif self.sortBy == SORT_BY.haversine_distance:
                tooltip_string = '<br><strong> HDist: </strong>' + str(
                    round(self.df_poi[self.df_poi['placekey'] == point_of_interest['placekey'].values[0]][
                              'haversine_distance'], 2)) + ' km'
            elif self.sortBy == SORT_BY.Risk:
                tooltip_string = '<br><strong> RRisk: </strong> [nda]'

            elif self.sortBy == SORT_BY.POIScore:
                tooltip_string = '<br><strong> POI Score: </strong>' + str(point_of_interest['poi_score'])

            categ = self.df_poi[self.df_poi['placekey'] == point_of_interest['placekey']]
            categ = categ['top_category'].values[0]
            pre, ic = im.getLogo(cat=categ)

            coords.append(poi_coords)
            popups.append(popup)
            tooltip_strings.append('<strong>' + str(index + 1) + '. ' + poi_name + '</strong>' + tooltip_string)
            icons.append(folium.Icon(color='blue', prefix=pre, icon=ic))

        self.map_val['merkers'] = folium.plugins.MarkerCluster(
            locations=coords,
            popups=popups,
            tooltip_strings=tooltip_strings,
            icons=icons)

        self.map_val['merkers'].add_to(m)

        m.get_root().html.add_child(folium.JavascriptLink('../static/js/interactive_poi.js'))
        my_js = '''
        console.log('working perfectly')
        '''
        m.get_root().script.add_child(folium.Element(my_js))

        m.save(WEBNAME)
        path_to_open = 'file:///' + os.getcwd() + '/' + WEBNAME
        print(colored("Done updating html file!", 'yellow'))
        # webbrowser.open_new_tab(path_to_open)

    def updateLocation(self, center):
        loc = super().get_coordinates(center)
        m = folium.Map(location=loc, zoom_start=15)
        self.map_val['center_marker'].add_to(m)
        self.map_val['merkers'].add_to(m)
        m.get_root().html.add_child(folium.JavascriptLink('../static/js/interactive_poi.js'))
        my_js = '''
        console.log('working perfectly')
        '''
        m.get_root().script.add_child(folium.Element(my_js))
        m.save(WEBNAME)
