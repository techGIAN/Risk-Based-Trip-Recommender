import urllib.request
import json
import os
from enum import Enum

class SORT_BY(Enum):
    haversine_distance = 1
    Distance = 2
    Time = 3
    Risk = 4

# Get paths from OSRM for a given source and destination
def queryOSRM(source, destination, IS_DEBUG_MODE=False, IS_FULL_DEBUG_MODE=False):
    source = source[::-1]
    destination = destination[::-1]

    query = 'http://router.project-osrm.org/route/v1/foot/' + str(source[0]) + ',' + str(source[1]) + ';' + \
        str(destination[0]) + ','+str(destination[1]) + '?alternatives=true&geometries=geojson&overview=full'

    if IS_FULL_DEBUG_MODE and IS_DEBUG_MODE:
        print(query)

    # return to original coordinates
    source = source[::-1]
    destination = destination[::-1]
    return query

# list of path points of alternative routes
def get_path_points(q, num_of_routes=1):
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
        dist_tags.append(round(routing_data['routes'][i]['distance'] / 1000.0, 5))   # Km
        duration_tags.append(round(routing_data['routes'][i]['duration'] / 60.0, 5)) # seconds

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