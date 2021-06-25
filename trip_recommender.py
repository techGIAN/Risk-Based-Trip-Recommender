import copy
import webbrowser
import os
import ast
import pgeocode
import geocoder

import folium
import pandas as pd
import geopandas as gpd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from Location import Location
from Path import Path
from shapely import wkt
from utilityMethods import queryOSRM, get_path_points
import branca.colormap as cm

from RiskMap import RiskMap

# IS_DEBUG_MODE = True
geoloc = Nominatim(user_agent='TripRecApp')
geolocation = RateLimiter(geoloc.geocode, min_delay_seconds=2, return_value_on_exception=None)
WEBNAME = 'templates/recommender.html'


class Trip_Recommender(Location):
    specific_poi = 'no'
    postal_code = None
    address = None
    trip_count = 3
    destination = None
    paths = []
    query = None
    GDF_FILE = 'hex_gdf.csv'

    #  Initializes parameters
    def __init__(self, source, address, postal_code, specific_poi, trip_count, isCurrentLocation=True,
                 destination_coordinates=False, destination=None, IS_DEBUG_MODE=False, IS_FULL_DEBUG_MODE=False):
        
        self.source = [43.7925759,-79.4293432]
        self.setNewTrip(self.source, address, postal_code, specific_poi, trip_count, isCurrentLocation,
                        destination_coordinates=destination_coordinates, destination=destination,
                        IS_DEBUG_MODE = IS_DEBUG_MODE, IS_FULL_DEBUG_MODE = IS_FULL_DEBUG_MODE)

    def setNewTrip(self, source, address, postal_code, specific_poi, trip_count, isCurrentLocation=True,
                   destination_coordinates=False, destination=None, IS_DEBUG_MODE=False, IS_FULL_DEBUG_MODE=False):
        # if isCurrentLocation:
        #     self.source = geocoder.ip('me').latlng
        # else:
        #     self.source = source
        
        self.specific_poi = specific_poi
        self.trip_count = trip_count
        self.address = address
        self.query = None
        self.paths = []


        # retrieve coordinates of user's and desired destination
        if not destination_coordinates:
            self.destination = self.__get_coordinates(postal_code, address)
        else:
            self.destination = destination

        self.source = self.source[::-1]
        self.destination = self.destination[::-1]

        query = queryOSRM(source=self.source, destination=self.destination, IS_DEBUG_MODE=IS_DEBUG_MODE,
                          IS_FULL_DEBUG_MODE=IS_FULL_DEBUG_MODE)
        path_list, distances, durations = get_path_points(query, self.trip_count)
        
        # create a risk map if it does not exist
        if not os.path.exists(self.GDF_FILE):
            rm = RiskMap(w=1000)


        for i in reversed(range(len(path_list))):
            # pts = path_list[i]
            for pt in path_list[i]:
                temp = pt[0]
                pt[0] = pt[1]
                pt[1] = temp
            new_path = Path(path_list[i], distances[i], durations[i])
            new_path.set_risk_of_path()
            self.paths.append(new_path)

    # gets the geocoordinates of a location
    # requires either one of postal code or address
    # note: postal code takes precedence
    def __get_coordinates(self, p_code, ad):
        coords = [0.0, 0.0]
        if p_code != '':
            country_code = pgeocode.Nominatim('ca')
            postal_data = country_code.query_postal_code(p_code)
            lat = postal_data['latitude']
            lon = postal_data['longitude']
        else:
            locale = geoloc(ad)
            lat = locale['latitude']
            lon = locale['longitude']
        coords = [lat, lon]
        return coords

    #  Get paths from source to destination
    def plot(self):

        self.source = self.source[::-1]
        self.destination = self.destination[::-1]

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
        colormap = cm.LinearColormap(colors=['green', 'yellow', 'red'])
        colormap.caption = 'Risk Level'
        colormap.add_to(m)
        style_func = lambda x: {
            'color': 'black',
            'fillColor': colormap(x['properties']['risk_val']),
            'fillOpacity': 0.5
        }
        highlight_func = lambda x: {
            'fillColor': '#000000',
            'color': '#000000',
            'fillOpacity': 0.3
        }
        folium.features.GeoJson(
            grid_gdf,
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

        # markers
        folium.Marker(
            location=self.source,
            popup=src_poi,
            tooltip='<strong>' + src_poi + '</strong>',
            icon=folium.Icon(color='blue', prefix='fa', icon='home')
        ).add_to(m)
        folium.Marker(
            location=self.destination,
            popup=tgt_poi,
            tooltip='<strong>' + tgt_poi + '</strong>',
            icon=folium.Icon(color='red', prefix='fa', icon='star')
        ).add_to(m)

        i = len(self.paths) - 1
        for path in self.paths:
            pts = path.coordinates

            for pt in pts:
                temp = pt[0]
                pt[0] = pt[1]
                pt[1] = temp

            this_duration = str(round(path.total_duration,2)) + ' min'
            risk_val = str(round(path.risk,2))
            
            if path.total_duration >= 60:
                this_duration = str(round(path.total_duration / 60, 2)) + " h"

            trip_name = 'OSRM Trip ' + str(i + 1) + '<br>' + \
                        str(round(path.total_distance,2)) + ' Km<br>' + \
                        this_duration + '<br>' + \
                        'risk: ' + risk_val


            rand_color = 'darkblue'
            opacity_val = 0.3
            if i == 0:
                rand_color = 'darkblue'
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

            fg.add_to(m)
            i -= 1

        folium.LayerControl().add_to(m)
        m.save(WEBNAME)
        path_to_open = 'file:///' + os.getcwd() + '/' + WEBNAME
        # webbrowser.open_new_tab(path_to_open)

    # Prints the number of points per kilometer to get a sense of the resolution
    def get_resolution_data(self):
        for p in self.paths:
            p.get_resolution()

    def getPaths(self):
        return self.paths
#
# trip = Trip_Recommender(source=[43.797632, -79.421758], address='1486 Aldergrove Dr, Oshawa,', postal_code='L1K 2Y4',
#                         specific_poi=False,trip_count=3, isCurrentLocation=True)
# trip.plot()
# print()
# trip.get_resolution_data()
# print("\n\n\n\n")
# for p in trip.paths:
#     print(p.print())