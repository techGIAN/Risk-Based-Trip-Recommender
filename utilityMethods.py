import time
import urllib.request
import json
import os
from enum import Enum
import numpy as np
import pandas as pd
import ast

GRASS_HOPPER_KEY = 'fc4feee8-6646-46a1-a480-ad2a14f094c2'


class SORT_BY(Enum):
    haversine_distance = 1
    Distance = 2
    Time = 3
    Risk = 4
    POIScore = 5


class ROUTE_FROM(Enum):
    OSRM = 1
    GRASS_HOPPER = 2


# returns path_list, distances, durations
def query(source, destination, trip_count, IS_DEBUG_MODE=False, IS_FULL_DEBUG_MODE=False, ROUTE_FROM=ROUTE_FROM.OSRM,
          mode_of_transit='car'):
    """
    :param source: source coordinates
    :param destination: destination coordinates
    :param trip_count: max number of trips to query
    :param IS_DEBUG_MODE: outputs debug messages
    :param IS_FULL_DEBUG_MODE: outputs extended debug messages
    :return: search results: distance, duration, routes
    """
    file_name = 'df_past_coordinates_search.csv'

    if ROUTE_FROM == ROUTE_FROM.OSRM:
        if os.path.isfile(file_name):
            # Since it is a large file, read it in chunks
            for coordinate_file in pd.read_csv(file_name, chunksize=5000):
                row = coordinate_file[(coordinate_file['source'] == str(source)) &
                                      (coordinate_file['destination'] == str(destination))]

                # Take into account a reverse trip with the assumption that the distance and
                # duration remains the same
                if len(row) == 0:
                    row = coordinate_file[(coordinate_file['source'] == str(destination)) &
                                          (coordinate_file['destination'] == str(source))]

                # Entry exists! retrive and use it
                if len(row) > 0:
                    print("\tEntry Exists!!!")
                    distance = ast.literal_eval(row['distance'].values[0])
                    duration = ast.literal_eval(row['duration'].values[0])
                    routes = ast.literal_eval(row['routes'].values[0])

                    return routes, distance, duration

        else:
            coordinate_file = pd.DataFrame(columns=['source',
                                                    'destination',
                                                    'distance',
                                                    'duration',
                                                    'routes',
                                                    'mode_of_transit'])

        print("\tEntry does't Exists!!!")

        q = queryOSRM(source, destination, mode_of_transit, IS_DEBUG_MODE, IS_FULL_DEBUG_MODE)
        routes, distance, duration = __get_path_points(q, ROUTE_FROM, trip_count)

        # save entry to the csv file
        row = pd.DataFrame({'source': [source], 'destination': [destination],
                            'distance': [distance], 'duration': [duration],
                            'routes': [routes], 'mode_of_transit': [mode_of_transit]})

        row.to_csv(file_name, mode='a', index=False, header=False)

        # return routes, distance and duration
        return routes, distance, duration

    elif ROUTE_FROM == ROUTE_FROM.GRASS_HOPPER:
        q = queryGrassHopper(source, destination, trip_count, mode_of_transit, IS_DEBUG_MODE, IS_FULL_DEBUG_MODE)
        return __get_path_points(q, ROUTE_FROM, trip_count)


# Get paths from OSRM for a given source and destination
def queryOSRM(source, destination, mode_of_transit, IS_DEBUG_MODE=False, IS_FULL_DEBUG_MODE=False):
    q = 'http://router.project-osrm.org/route/v1/' + mode_of_transit + '/' + str(source[1]) + ',' + str(source[0]) + \
        ';' + str(destination[1]) + ',' + str(destination[0]) + '?alternatives=true&geometries=geojson&overview=full'

    if IS_FULL_DEBUG_MODE and IS_DEBUG_MODE:
        print(q)

    return q


# Get paths from OSRM for a given source and destination
def queryGrassHopper(source, destination, trip_count, mode_of_transit, IS_DEBUG_MODE=False, IS_FULL_DEBUG_MODE=False):
    q = 'https://graphhopper.com/api/1/route?point=' + str(source[0]) + ',' + str(source[1]) + \
        '&point=' + str(destination[0]) + ',' + str(destination[1]) + '&vehicle=' + mode_of_transit + \
        '&calc_points=true' + '&key=' + GRASS_HOPPER_KEY + '&points_encoded=false&alternative_route.max_paths=' + \
        str(trip_count) + '&algorithm=alternative_route'

    if IS_FULL_DEBUG_MODE and IS_DEBUG_MODE:
        print(q)

    return q


# list of path points of alternative routes
def __get_path_points(q, ROUTE_FROM, num_of_routes=1):
    urllib.request.urlretrieve(q, "query.json")
    routing_file = open('query.json', )

    # obtain the coordinates of the points along the path as suggested by osrm
    routing_data = json.load(routing_file)

    try:
        if ROUTE_FROM == ROUTE_FROM.OSRM:
            routes, dist_tags, duration_tags = __get_path_points_OSRM(routing_data, num_of_routes)
        elif ROUTE_FROM == ROUTE_FROM.GRASS_HOPPER:
            routes, dist_tags, duration_tags = __get_path_points_GRASS_HOPPER(routing_data, num_of_routes)
    except Exception as e:
        print("\t\tBad Gateway, trying again after 1 second")
        time.sleep(2)
        if ROUTE_FROM == ROUTE_FROM.OSRM:
            routes, dist_tags, duration_tags = __get_path_points_OSRM(routing_data, num_of_routes)
        elif ROUTE_FROM == ROUTE_FROM.GRASS_HOPPER:
            routes, dist_tags, duration_tags = __get_path_points_GRASS_HOPPER(routing_data, num_of_routes)

    # Close and delete file
    routing_file.close()
    os.remove('query.json')

    return routes, dist_tags, duration_tags


def __get_path_points_OSRM(routing_data, num_of_routes):

    routes = []
    m_min = min(num_of_routes, len(routing_data['routes']))

    dist_tags = []
    duration_tags = []

    for i in range(m_min):
        path_points = routing_data['routes'][i]['geometry']['coordinates']
        dist_tags.append(round(routing_data['routes'][i]['distance'] / 1000.0, 5))    # m -> Km
        duration_tags.append(round(routing_data['routes'][i]['duration'] / 60.0, 5))  # seconds -> minutes

        # swap the coordinates
        for point in path_points:
            temp = point[0]
            point[0] = point[1]
            point[1] = temp
        routes.append(path_points)

    return routes, dist_tags, duration_tags


def __get_path_points_GRASS_HOPPER(routing_data, num_of_routes):
    routes = []
    m_min = min(num_of_routes, len(routing_data['paths']))

    dist_tags = []
    duration_tags = []

    for i in range(m_min):
        path_points = routing_data['paths'][i]['points']['coordinates']
        dist_tags.append(round(routing_data['paths'][i]['distance'] / 1000.0, 5))    # m -> Km
        duration_tags.append(round(routing_data['paths'][i]['time'] / 60000.0, 5))   # milliseconds -> minutes

        # swap the coordinates
        for point in path_points:
            temp = point[0]
            point[0] = point[1]
            point[1] = temp
        routes.append(path_points)

    return routes, dist_tags, duration_tags


def haversine_dist(source, latitude, longitude):
    R = 6373.0
    lat1 = np.deg2rad(source[0])
    lon1 = np.deg2rad(source[1])
    lat2 = np.deg2rad(latitude)
    lon2 = np.deg2rad(longitude)
    d_lon = lon2 - lon1
    d_lat = lat2 - lat1
    d = np.sin(d_lat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(d_lon / 2) ** 2
    cons = 2 * np.arctan2(np.sqrt(d), np.sqrt(1 - d))
    return R * cons
