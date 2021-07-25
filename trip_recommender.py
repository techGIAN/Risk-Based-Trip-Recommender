import webbrowser
import os
import time

import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from Location import Location
from Path import Path
from utilityMethods import query, ROUTE_FROM

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
        'color' : []
    }

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

        path_list, distances, durations = query(source=self.source,
                                                destination=self.destination,
                                                trip_count=self.trip_count,
                                                IS_DEBUG_MODE=IS_DEBUG_MODE,
                                                IS_FULL_DEBUG_MODE=IS_FULL_DEBUG_MODE,
                                                ROUTE_FROM=self.ROUTE_FROM,
                                                mode_of_transit=self.mode_of_transit)

        for i in reversed(range(len(path_list))):
            pts = path_list[i]
            self.paths.append(Path(pts, distances[i], durations[i], ROUTE_FROM=self.ROUTE_FROM))

    #  Get paths from source to destination
    def plot(self):
        self.results_html = ''
        mid = [(self.source[0] + self.destination[0]) / 2, (self.source[1] + self.destination[1]) / 2]
        src_poi = 'Origin'
        tgt_poi = 'Destination'
        m = folium.Map(location=mid, zoom_start=14)

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
            pts = path.coordinates

            this_distance = str(round(path.total_distance, 2)) + 'Km'
            this_duration = str(round(path.total_duration, 2)) + ' min'
            if path.total_duration >= 60:
                this_duration = str(round(path.total_duration / 60, 2)) + " h"

            trip_name = self.mode_of_transit + ': Trip ' + str(i + 1) + '<br>' + \
                        this_distance + '<br>' + this_duration

            self.results_html = "<button id='path_selector' onclick='selectRoute("+str(i)+")' >Trip " + str(i+1) + ': <div style="padding-left:10px;">time:' + this_duration + '</div>' \
                                '<div style="padding-left:10px;">distance: ' + this_distance + \
                                '</div></button>\n' + self.results_html

            rand_color = 'darkblue'
            opacity_val = 0.3
            if i == 0:
                opacity_val = 1

            fg = folium.FeatureGroup(trip_name)
            folium.vector_layers.PolyLine(
                pts,
                popup=trip_name,
                tooltip=trip_name,
                color=rand_color,
                weight=10,
                opacity=opacity_val
            ).add_to(fg)

            self.map_val['pts'].append(pts)
            self.map_val['popup'].append(trip_name)
            self.map_val['tooltip'].append(trip_name)
            self.map_val['color'].append(rand_color)

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
        self.map_val['origin'].add_to(m)
        self.map_val['destination'].add_to(m)

        i = len(self.paths) - 1
        for path in self.paths:
            print("\ti = "+ str(i))
            fg = folium.FeatureGroup(self.map_val['popup'][i])

            if i == number:
                print("\t\ti = "+ str(number))
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

# trip = Trip_Recommender(source='300 Antibes Drive Toronto Canada', destination='York University Canada',
#                         trip_count=5, ROUTE_FROM=ROUTE_FROM.OSRM)
# trip.plot()
# trip.get_resolution_data()
# print("\n\n\n\n")
# for p in trip.paths:
#     start = time.time()
#     p.calculate_risk()
#     end = time.time()
#     print("time took to process request: "+str(end-start))
#     print(p.print())

# time.sleep(10)

# trip.setNewTrip(source=[43.797632, -79.421758], address='1486 Aldergrove Dr, Oshawa,', postal_code='L1K 2Y4',
#                 specific_poi=False,trip_count=5, isCurrentLocation=True, ROUTE_FROM=ROUTE_FROM.GRASS_HOPPER)
# trip.plot()
# print()
# trip.get_resolution_data()
# print("\n\n\n\n")
# for p in trip.paths:
#     start = time.time()
#     p.calculate_risk()
#     end = time.time()
#     print("time took to process request: "+str(end-start))
#     print(p.print())
