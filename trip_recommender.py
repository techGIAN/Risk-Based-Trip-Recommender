import copy
import webbrowser
import os
import ast
import folium
import time
import itertools
import pandas as pd
import geopandas as gpd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from Location import Location
from Path import Path, hex_of_path
from RiskMap import RiskMap
from utilityMethods import query, ROUTE_FROM

from shapely import wkt
import branca.colormap as cm

from optimizer import Optimizer

# uncomment this line
# from RiskMap import RiskMap

geoloc = Nominatim(user_agent='TripRecApp')
geolocation = RateLimiter(geoloc.geocode, min_delay_seconds=2, return_value_on_exception=None)
WEBNAME = 'templates/recommender.html'
# df_trip_path = 'df_trips.csv'
GDF_FILE = 'hex_gdf.csv'
df = pd.read_csv(GDF_FILE)
df['geometry'] = df['geometry'].apply(wkt.loads)
grid_gdf = gpd.GeoDataFrame(df, crs='epsg:4326')


class Trip_Recommender(Location):
    trip_count = 3
    destination = None
    paths = []
    ROUTE_FROM = ROUTE_FROM.OSRM
    mode_of_transit = 'car'
    map_val = {
        'origin': None,
        'destination': None,
        'pts': [],
        'popup': [],
        'tooltip': [],
        'color': [],
        'risk_map': None
    }
    total_risk = 0

    # df_paths = pd.DataFrame(columns=['path_id', 'path_distance', 'path_duration', 'path_risk'])
    df_trip = None

    #  Initializes parameters
    def __init__(self, source, destination, trip_count,
                 IS_DEBUG_MODE=False, IS_FULL_DEBUG_MODE=False,
                 ROUTE_FROM=ROUTE_FROM.OSRM,
                 mode_of_transit='car', is_time_now=True, time_later_val=None):

        self.setNewTrip(source, destination, trip_count, ROUTE_FROM,
                        IS_DEBUG_MODE=IS_DEBUG_MODE, IS_FULL_DEBUG_MODE=IS_FULL_DEBUG_MODE,
                        mode_of_transit=mode_of_transit, is_time_now=is_time_now, time_later_val=time_later_val)

    def setNewTrip(self, source, destination, trip_count, ROUTE_FROM,
                   IS_DEBUG_MODE=False, IS_FULL_DEBUG_MODE=False, mode_of_transit='car',
                   is_time_now=True, time_later_val=None):

        self.time_now = is_time_now
        self.time_later_value = time_later_val
        self.source = super().get_coordinates(source)
        self.ROUTE_FROM = ROUTE_FROM
        self.trip_count = trip_count
        self.paths = []
        self.mode_of_transit = mode_of_transit

        # retrieve coordinates of user's and desired destination
        self.destination = super().get_coordinates(destination)

        # create a risk map if it does not exist
        if not os.path.exists(GDF_FILE):
            rm = RiskMap(w=1000)

        self.__set_trips_and_paths(ROUTE_FROM, IS_DEBUG_MODE, IS_FULL_DEBUG_MODE)
        # self.__rank_paths()

    def __rank_paths(self):
        # Use the optimizer to rank the paths according to score
        df_path_sub = pd.DataFrame(columns=['path_distance', 'path_duration', 'path_risk'])
        df_path_sub[['path_distance', 'path_duration', 'path_risk']] = self.df_paths[
            ['path_distance', 'path_duration', 'path_risk']]
        op = Optimizer()
        v = op.opt(np_array=df_path_sub.to_numpy())
        self.df_paths['path_score'] = v[0] * self.df_paths['path_distance'] + v[1] * self.df_paths['path_duration'] + v[
            2] * self.df_paths['path_risk']
        self.df_paths.sort_values(by=['path_score'], inplace=True, ascending=True)

        # and sort by ranking
        rank = 1
        for idx, row in self.df_paths.iterrows():
            for i in range(len(self.paths)):
                if self.paths[i].id == row['path_id']:
                    self.paths[i].rank = rank
                    self.paths[i].score = row['path_score']
            rank += 1

        self.paths = sorted(self.paths, key=lambda p: p.rank, reverse=True)

    def __set_trips_and_paths(self, ROUTE_FROM, IS_DEBUG_MODE=False, IS_FULL_DEBUG_MODE=False):
        # distances, durations, path_list = None, None, None
        # paths_discretized_points, paths_discretized_linestrings = None, None
        # notFound = True

        # # Path exists
        # if os.path.exists(df_trip_path):
        #     self.df_trip = pd.read_csv(df_trip_path)
        #
        #     # Doesn't include mode of transit as there is no distinction in OSRM
        #     row = self.df_trip[(self.df_trip['source'] == str(self.source)) &
        #                        (self.df_trip['destination'] == str(self.destination))]
        #
        #     # Take into account a reverse trip with the assumption that the distance and
        #     # duration remains the same
        #     if len(row) == 0:
        #         row = self.df_trip[(self.df_trip['source'] == str(self.destination)) &
        #                            (self.df_trip['destination'] == str(self.source))]
        #
        #     # Entry exists! retrive and use it
        #     if len(row) > 0:
        #         print("\t\t\tTrip Exists!")
        #
        #         distances = ast.literal_eval(row['distance'].values[0])
        #         durations = ast.literal_eval(row['duration'].values[0])
        #         path_list = ast.literal_eval(row['routes'].values[0])
        #
        #         paths_discretized_points = ast.literal_eval(row['discretized_points'].values[0])
        #
        #         notFound = False
        #
        # # Either file doesn't exist or trip doesn't exist
        # if notFound:
        #     self.df_trip = pd.DataFrame(columns=['source',
        #                                          'destination',
        #                                          'distance',
        #                                          'duration',
        #                                          'routes',
        #                                          'discretized_points'])

        path_list, distances, durations = query(source=self.source,
                                                destination=self.destination,
                                                trip_count=self.trip_count,
                                                IS_DEBUG_MODE=IS_DEBUG_MODE,
                                                IS_FULL_DEBUG_MODE=IS_FULL_DEBUG_MODE,
                                                ROUTE_FROM=self.ROUTE_FROM,
                                                mode_of_transit=self.mode_of_transit)

        # hexagons, discretized_points, discretized_linestrings = [], [], []

        for i in range(len(path_list)):
            # if notFound:
            new_path = Path(i, path_list[i], distances[i], durations[i], grid_gdf, ROUTE_FROM=ROUTE_FROM.OSRM,
                            hexagons=None, discretized_points=None)
            # else:
            #     new_path = Path(i, coordinates=path_list[i], distance=distances[i], time=durations[i],
            #                     ROUTE_FROM=ROUTE_FROM.OSRM,
            #                     discretized_points=paths_discretized_points[i])

            # set and retrieve risk of path
            # new_path.set_risk_of_path()
            new_path.set_general_risk_of_path()
            # new_path_risk = copy.deepcopy(new_path.get_risk_of_path())
            self.total_risk += new_path.get_risk_of_path()
            # desct_points = copy.deepcopy(new_path.discretized_points)

            # add the path to the list of current paths
            # discretized_points.append(desct_points)
            # hexagons.append(new_path.get_hexagons())

            self.paths.append(new_path)

            # building the df of the paths with attributes [path_id, path_distance, path_duration, path_risk]
            # path_dict = {'path_id': i, 'path_distance': distances[i], 'path_duration': durations[i],
            #              'path_risk': new_path_risk}
            # self.df_paths = self.df_paths.append(path_dict, ignore_index=True)

        # if notFound:
        #     row = pd.DataFrame({'source': [self.source], 'destination': [self.destination], 'distance': [distances],
        #                         'duration': [durations], 'routes': [path_list],'hexagons': [hexagons],
        #                         'discretized_points': [discretized_points]})
        #
        #     self.df_trip = self.df_trip.append(row)
        #     row.to_csv(df_trip_path, mode='a', index=False, header=False)

    def hex_layer(self, m, grid_gdf):
        # Add hexagon layer
        print('init hex layer')

        try:
            pth = [path.coordinates for path in self.paths]
            points = [self.source, self.destination]
            for i in range(len(pth)):
                for j in range(len(pth[i])):
                    points.append([pth[i][j][1],pth[i][j][0]])

            ind = hex_of_path(grid_gdf, points)
            grid = grid_gdf.loc[ind]

        except Exception as e:
            print("ERROR in trip_rec: "+str(e))

        # risk at 0 only
        grid['hex_risk'] = grid['hex_risk'].apply(eval)
        grid['risk_val'] = [l[0] for l in grid['hex_risk']]

        colormap = cm.LinearColormap(colors=[(255,0,0,0), 'red'])
        colormap.caption = 'Risk Level'
        colormap.add_to(m)
        style_func = lambda x: {
            'color': 'black',
            'fillColor': colormap(x['properties']['risk_val']),
            'stroke':True,
            'weight':1,
            'fillOpacity': 0.7
        }
        highlight_func = lambda x: {
            'fillColor': '#000000',
            'color': '#000000',
            'fillOpacity': 0.8
        }
        folium.features.GeoJson(
            grid,
            style_function=style_func,
            highlight_function=highlight_func,
            control=False,
            tooltip=folium.features.GeoJsonTooltip(
                fields=['cellID', 'risk_val'],
                aliases=['Hex ID', 'Risk Level'],
                style=('background-color: white; color: #333333; font-family: arial; font-sizeL 12px; padding: 10px;'),
                sticky=True
            )
        ).add_to(m)

    #  Get paths from source to destination
    def plot(self):
        start = time.time()
        self.results_html = ''

        mid = [(self.source[0] + self.destination[0]) / 2, (self.source[1] + self.destination[1]) / 2]
        src_poi = 'Origin'
        tgt_poi = 'Destination'
        m = folium.Map(location=mid, zoom_start=14)

        # # Add hexagon layer
        # print('init hex layer')
        # df = pd.read_csv(self.GDF_FILE)
        # df['geometry'] = df['geometry'].apply(wkt.loads)
        # grid_gdf = gpd.GeoDataFrame(df, crs='epsg:4326')
        self.hex_layer(m, grid_gdf)


        # markers
        self.map_val['origin'] = folium.Marker(
            location=self.source,
            popup=src_poi,
            tooltip='<strong>' + src_poi + '</strong>',
            icon=folium.Icon(color='blue', prefix='fa', icon='home')
        )
        self.map_val['origin'].add_to(m)

        self.map_val['destination'] = folium.Marker(
            location=self.destination,
            popup=tgt_poi,
            tooltip='<strong>' + tgt_poi + '</strong>',
            icon=folium.Icon(color='red', prefix='fa', icon='star')
        )
        self.map_val['destination'].add_to(m)
        self.map_val['pts'] = []
        self.map_val['popup'] = []
        self.map_val['tooltip'] = []
        self.map_val['color'] = []

        i = len(self.paths) - 1
        for path in self.paths:
            # No need to double swap. It is being taken cared of in queryOSRM
            # pts = [[pt[1],pt[0]] for pt in path.coordinates]

            pts = path.coordinates

            this_distance = str(round(path.total_distance, 2)) + 'Km'
            this_duration = str(round(path.total_duration, 2)) + ' min'
            risk_val = str(round(path.risk, 2))
            rrisk_val = str(round(path.risk / self.total_risk, 2)) if self.total_risk != 0 else "0"

            if path.total_duration >= 60:
                this_duration = str(round(path.total_duration / 60, 2)) + " h"

            # trip_name = '<strong>Trip ' + str(i + 1) + ':</strong><br>' + \
            #             'risk: ' + risk_val + '<br>' + \
            #             'rrisk: ' + rrisk_val + '<br> ' #'Rank: ' +\
                        # this_duration + '<br>' + \
                        # str(path.rank)  # + '<br> Score: ' + str(round(path.score,2))
            trip_name = str(i + 1)
            self.results_html = "<button id='path_selector' onclick='selectRoute(" + str(i) + ")' >Trip " + str(i + 1) + \
                                ': <div style="padding-left:10px;">time:' + this_duration + '</div>' + \
                                '<div style="padding-left:10px;">distance: ' + this_distance + '</div>' + \
                                '<div style="padding-left:10px;">risk: ' + rrisk_val + '</div>' + \
                                '<div style="padding-left:10px;"rank: ' + str(path.rank) + '</div>' + \
                                '</button>\n' + self.results_html
            # '<div style="padding-left:10px;"score: ' + str(round(path.score,2)) + '</div>' \

            rand_color = 'darkblue'
            opacity_val = 0.3

            if i == 0:
                opacity_val = 1

            fg = folium.FeatureGroup(trip_name)

            folium.vector_layers.PolyLine(
                pts,
                popup='<b>' + trip_name + '</b>',
                tooltip=folium.Tooltip(trip_name, permanent=True),
                color=rand_color,
                weight=8,
                opacity=opacity_val
            ).add_to(fg)

            self.map_val['pts'].insert(0, pts)
            self.map_val['popup'].insert(0, trip_name)
            self.map_val['tooltip'].insert(0, trip_name)
            self.map_val['color'].insert(0, rand_color)

            fg.add_to(m)
            i -= 1

        folium.LayerControl().add_to(m)
        m.get_root().html.add_child(folium.JavascriptLink('../static/js/interactive_routes.js'))
        my_js = '''
        console.log('working perfectly')
        '''
        m.get_root().script.add_child(folium.Element(my_js))
        m.save(WEBNAME)
        path_to_open = 'file:///' + os.getcwd() + '/' + WEBNAME
        # webbrowser.open_new_tab(path_to_open)
        # end = time.time()
        # print("time took to process request: " + str(round((end - start) / 60, 2)) + " min")

    # Prints the number of points per kilometer to get a sense of the resolution
    def get_resolution_data(self):
        for p in self.paths:
            p.get_resolution()

    def getPaths(self):
        return self.paths

    def normalizer(ll):
        return [x / sum(ll) for x in ll]

    def selectPath(self, number):
        number = int(number)

        mid = [(self.source[0] + self.destination[0]) / 2, (self.source[1] + self.destination[1]) / 2]
        m = folium.Map(location=mid, zoom_start=14)

        # markers
        # self.map_val['risk_map'].add_to(m)
        self.map_val['origin'].add_to(m)
        self.map_val['destination'].add_to(m)

        i = len(self.paths) - 1
        for path in self.paths:
            fg = folium.FeatureGroup(self.map_val['popup'][i])

            if i == number:
                folium.vector_layers.PolyLine(
                    self.map_val['pts'][i],
                    popup=self.map_val['popup'][i],
                    tooltip=self.map_val['tooltip'][i],
                    color=self.map_val['color'][i],
                    weight=10,
                    opacity=1
                ).add_to(fg)
            else:
                folium.vector_layers.PolyLine(
                    self.map_val['pts'][i],
                    popup=self.map_val['popup'][i],
                    tooltip=self.map_val['tooltip'][i],
                    color=self.map_val['color'][i],
                    weight=10,
                    opacity=0.3
                ).add_to(fg)

            fg.add_to(m)
            i -= 1

        folium.LayerControl().add_to(m)

        m.get_root().html.add_child(folium.JavascriptLink('../static/js/interactive_routes.js'))
        my_js = '''
        console.log('working perfectly')
        '''
        m.get_root().script.add_child(folium.Element(my_js))
        m.save(WEBNAME)


# trip = Trip_Recommender(source=[43.9443836, -79.4547236], destination=[43.9397253,-79.4533074], trip_count=5)
# trip.plot()
# time.sleep(5)
#
# trip = Trip_Recommender(source=[43.9444184, -79.4546002], destination=[43.9397253,-79.4533074], trip_count=5)
# trip.plot()