import webbrowser
import os

import folium

import pandas as pd
import geopandas as gpd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from Location import Location
from Path import Path
from utilityMethods import query, ROUTE_FROM

from shapely import wkt
import branca.colormap as cm


# uncomment this line
# from RiskMap import RiskMap

geoloc = Nominatim(user_agent='TripRecApp')
geolocation = RateLimiter(geoloc.geocode, min_delay_seconds=2, return_value_on_exception=None)
WEBNAME = 'templates/recommender.html'


class Trip_Recommender(Location):
    trip_count = 3
    destination = None
    paths = []
    ROUTE_FROM = ROUTE_FROM.OSRM
    mode_of_transit = 'car'
    map_val = {
        'origin': None,
        'destination':None,
        'pts' : [],
        'popup' : [],
        'tooltip' : [],
        'color' : [],
        'risk_map':None
    }
    total_risk = 0
    GDF_FILE = 'hex_gdf.csv'

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
        if not os.path.exists(self.GDF_FILE):
            rm = RiskMap(w=1000)

        path_list, distances, durations = query(source=self.source,
                                                destination=self.destination,
                                                trip_count=self.trip_count,
                                                IS_DEBUG_MODE=IS_DEBUG_MODE,
                                                IS_FULL_DEBUG_MODE=IS_FULL_DEBUG_MODE,
                                                ROUTE_FROM=self.ROUTE_FROM,
                                                mode_of_transit=self.mode_of_transit)

        for i in reversed(range(len(path_list))):
            # new_path = Path(path_list[i], distances[i], durations[i], ROUTE_FROM=self.ROUTE_FROM)
            swapped_points = [[pt[1],pt[0]] for pt in path_list[i]]
            new_path = Path(swapped_points, distances[i], durations[i], ROUTE_FROM=self.ROUTE_FROM)

            new_path.set_risk_of_path()
            new_path_risk = new_path.get_risk_of_path()
            self.total_risk += new_path_risk
            self.paths.append(new_path)

            print('Risk of Path ' + str(i) + ': ' + str(new_path_risk) + '; TotalRiskSoFar: ' + str(self.total_risk))

    #  Get paths from source to destination
    def plot(self):
        self.results_html = ''

        mid = [(self.source[0] + self.destination[0]) / 2, (self.source[1] + self.destination[1]) / 2]
        src_poi = 'Origin'
        tgt_poi = 'Destination'
        m = folium.Map(location=mid, zoom_start=14)


        # Add hexagon layer
        print('init hex layer')
        df = pd.read_csv(self.GDF_FILE)
        df['geometry'] = df['geometry'].apply(wkt.loads)
        grid_gdf = gpd.GeoDataFrame(df, crs='epsg:4326')
        # risk at 0 only
        grid_gdf['hex_risk'] = grid_gdf['hex_risk'].apply(eval)
        grid_gdf['risk_val'] = [l[0] for l in grid_gdf['hex_risk']]
        # gray map
        # folium.GeoJson(
        #     grid_gdf['geometry'],
        #     style_function=lambda x:{'fillColor':'gray', 'color':'black'}
        # ).add_to(m)
        # colormap
        # colormap = cm.LinearColormap(colors=[(255,0,0,0), 'red'])
        # colormap.caption = 'Risk Level'
        # colormap.add_to(m)
        # style_func = lambda x: {
        #     'color': 'black',
        #     'fillColor': colormap(x['properties']['risk_val']),
        #     'fillOpacity': 0.5
        # }
        # highlight_func = lambda x: {
        #     'fillColor': '#000000',
        #     'color': '#000000',
        #     'fillOpacity': 0.3
        # }
        # self.map_val['risk_map'] = folium.features.GeoJson(
        #     grid_gdf,
        #     style_function=style_func,
        #     highlight_function=highlight_func,
        #     control=False,
        #     tooltip=folium.features.GeoJsonTooltip(
        #         fields=['cellID', 'risk_val'],
        #         aliases=['Hex ID', 'Risk Level'],
        #         style=('background-color: white; color: #333333; font-family: arial; font-sizeL 12px; padding: 10px;'),
        #         sticky=True
        #     )
        # )
        # self.map_val['risk_map'].add_to(m)

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
            pts = [[pt[1],pt[0]] for pt in path.coordinates]


            # for pt in pts:
            #     temp = pt[0]
            #     pt[0] = pt[1]
            #     pt[1] = temp

            this_distance = str(round(path.total_distance, 2)) + 'Km'
            this_duration = str(round(path.total_duration, 2)) + ' min'
            risk_val = str(round(path.risk,2))
            rrisk_val = str(round(path.risk/self.total_risk,2))

            if path.total_duration >= 60:
                this_duration = str(round(path.total_duration / 60, 2)) + " h"

            trip_name = self.mode_of_transit + ': Trip ' + str(i + 1) + '<br>' + \
                        this_distance + '<br>' + this_duration + '<br>' + \
                        'rrisk: ' + rrisk_val

            self.results_html = "<button id='path_selector' onclick='selectRoute("+str(i)+")' >Trip " + str(i+1) + \
                                ': <div style="padding-left:10px;">time:' + this_duration + '</div>' \
                                '<div style="padding-left:10px;">distance: ' + this_distance + '</div>' \
                                '<div style="padding-left:10px;"rrisk: ' + rrisk_val + '</div>' \
                                '</button>\n' + self.results_html

            rand_color = 'darkblue'
            opacity_val = 0.3

            if i == 0:
                opacity_val = 1

            fg = folium.FeatureGroup(trip_name)
            folium.vector_layers.PolyLine(
                pts,
                popup='<b>' + trip_name + '</b>',
                tooltip=trip_name,
                color=rand_color,
                weight=10,
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

    # Prints the number of points per kilometer to get a sense of the resolution
    def get_resolution_data(self):
        for p in self.paths:
            p.get_resolution()

    def getPaths(self):
        return self.paths

    def selectPath(self, number):
        number = int(number)
        print("path value that needs to change: "+ str(number))
        mid = [(self.source[0] + self.destination[0]) / 2, (self.source[1] + self.destination[1]) / 2]
        m = folium.Map(location=mid, zoom_start=14)

        # markers
        self.map_val['risk_map'].add_to(m)
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