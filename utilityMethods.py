import urllib.request
import json
import os
from enum import Enum

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
    q = None

    if ROUTE_FROM == ROUTE_FROM.OSRM:
        q = queryOSRM(source, destination, mode_of_transit, IS_DEBUG_MODE, IS_FULL_DEBUG_MODE)
    elif ROUTE_FROM == ROUTE_FROM.GRASS_HOPPER:
        q = queryGrassHopper(source, destination, trip_count, mode_of_transit, IS_DEBUG_MODE, IS_FULL_DEBUG_MODE)

    return __get_path_points(q, ROUTE_FROM, trip_count)


# Get paths from OSRM for a given source and destination
def queryOSRM(source, destination, mode_of_transit, IS_DEBUG_MODE=False, IS_FULL_DEBUG_MODE=False):
    source = source[::-1]
    destination = destination[::-1]

    q = 'http://router.project-osrm.org/route/v1/' + mode_of_transit + '/' + str(source[0]) + ',' + str(source[1]) + \
        ';' + str(destination[0]) + ',' + str(destination[1]) + '?alternatives=true&geometries=geojson&overview=full'

    if IS_FULL_DEBUG_MODE and IS_DEBUG_MODE:
        print(q)

    # return to original coordinates
    source = source[::-1]
    destination = destination[::-1]
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
        dist_tags.append(round(routing_data['routes'][i]['distance'] / 1000.0, 5))    # Km
        duration_tags.append(round(routing_data['routes'][i]['duration'] / 60.0, 5))  # seconds

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
        dist_tags.append(round(routing_data['paths'][i]['distance'] / 1000.0, 5))    # Km
        duration_tags.append(round(routing_data['paths'][i]['time'] / 60000.0, 5))  # seconds

        # swap the coordinates
        for point in path_points:
            temp = point[0]
            point[0] = point[1]
            point[1] = temp
        routes.append(path_points)

    return routes, dist_tags, duration_tags
