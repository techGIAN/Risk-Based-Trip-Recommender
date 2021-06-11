import webbrowser
import os
import urllib.request
import json

import pgeocode
import geocoder

import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from Location import Location

WEBNAME = 'templates/recommender.html'

geoloc = Nominatim(user_agent='TripRecApp')
geolocation = RateLimiter(geoloc.geocode, min_delay_seconds=2, return_value_on_exception=None)
WEBNAME = 'templates/recommender.html'


class Trip_Recommender(Location):
    specific_poi = 'no'
    postal_code = None
    address = None
    trip_count = 3
    destination = None

    #  Initializes parameters
    def __init__(self, source, address, postal_code, specific_poi, trip_count, isCurrentLocation=True):
        if isCurrentLocation:
            self.source = geocoder.ip('me').latlng
        else:
            self.source = source

        self.specific_poi = specific_poi
        self.trip_count = trip_count
        self.address = address

        # retrieve coordinates of user's and desired destination
        self.destination = self.get_coordinates(postal_code, address)
        print('source = ',self.source , '\ndestination = ',self.destination)

    # list of path points of alternative routes
    def get_path_points(self, q, num_of_routes=1):
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
            dist_tags.append(round(routing_data['routes'][i]['distance'] / 1000.0, 2))
            duration_tags.append(round(routing_data['routes'][i]['duration'] / 60.0, 2))

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
    def get_coordinates(self, p_code, ad):
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

    #  Get paths from source to destination
    def getPaths(self):
        # flip coordinates for OSRM query
        mid = [(self.source[0] + self.destination[0]) / 2, (self.source[1] + self.destination[1]) / 2]

        self.source = self.source[::-1]
        self.destination = self.destination[::-1]
        print('source = ',self.source , '\ndestination = ',self.destination)

        query = 'http://router.project-osrm.org/route/v1/foot/' + str(self.source[0]) +','+ str(self.source[1])+ ';' + \
                str(self.destination[0]) + ','+str(self.destination[1]) + '?alternatives=true&geometries=geojson&overview=full'
        print(query)

        src_poi = 'Origin'
        tgt_poi = 'Destination'
        m = folium.Map(location=mid, zoom_start=14)

        # return to original coordinates
        self.source = self.source[::-1]
        self.destination = self.destination[::-1]

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

        path_list, distances, durations = self.get_path_points(query, self.trip_count)

        # for i in range(len(path_list)):
        for i in reversed(range(len(path_list))):
            pts = path_list[i]
            trip_name = 'OSRM Trip ' + str(i + 1) + '<br>' + \
                        str(distances[i]) + 'Km<br>' + \
                        str(durations[i]) + ' min'

            rand_color = 'darkblue'
            opacity_val = 0.3
            if i == 0:
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

        m.save(WEBNAME)
        path_to_open = 'file:///' + os.getcwd() + '/' + WEBNAME
        # webbrowser.open_new_tab(path_to_open)

# trip = Trip_Recommender(source=[43.8711, -79.4373], address='461 Sheppard Avenue East', postal_code='M7A 1A2',
#                         specific_poi=False,trip_count=3, isCurrentLocation=True)
# trip.getPaths()