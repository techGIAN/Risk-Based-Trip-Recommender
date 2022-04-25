import copy
from utilityMethods import query, ROUTE_FROM

# uncomment this line
# from RiskMap import RiskMap
from shapely import wkt
import pandas as pd
import numpy as np
import geopandas as gpd
import ast
import itertools

from shapely.geometry import Point, LineString, Polygon

IS_DEBUG_MODE = True
IS_FULL_DEBUG_MODE = True


class Path:
    coordinates = None
    total_distance = None
    risk = None
    total_duration = None
    time_by_segment = []
    distance_by_segment = []
    ROUTE_FROM = ROUTE_FROM.OSRM

    hexagons = dict()
    discretized_points = []
    discretized_linestrings = []
    id = 0
    hex_ids = None
    grid_gdf = None
    rank = -1
    score = 0

    def __init__(self, id, coordinates, distance, time, grid_gdf, ROUTE_FROM=ROUTE_FROM.OSRM, hexagons=None,
                 discretized_points=None, discretized_linestrings=None):
        self.coordinates = coordinates
        self.total_distance = distance
        self.total_duration = time
        self.ROUTE_FROM = ROUTE_FROM
        self.grid_gdf = grid_gdf
        self.id = id

        self.hexagons = hexagons if hexagons is not None else dict()
        self.discretized_points = discretized_points if discretized_points is not None else []
        self.discretized_linestrings = discretized_linestrings if discretized_linestrings is not None else []
        # self.init_gdf(self.GDF_FILE)

    # def init_gdf(self, gdf_file='hex_gdf.csv'):
    #     '''
    #         Initiate the hex grid dataframe
    #     '''
    #     df = pd.read_csv(gdf_file)
    #     df['geometry'] = df['geometry'].apply(wkt.loads)
    #     grid_gdf = gpd.GeoDataFrame(df, crs='epsg:4326')
    #     self.grid_gdf = grid_gdf
    #
    # def calculate_risk(self):
    #     # get the distance and duration of each line segment of the path
    #     self.__set_paths__full_data()

    def print(self):
        return "<<-----------------------------\n" \
               "\tcoordinates = " + str(self.coordinates) + "\n" \
               "\thexagons = " + str(self.hexagons) + "\n" \
               "\ttotal_distance = " + str(self.total_distance) + "\n" \
               "\trisk = " + str(self.risk) + "\n" \
               "\ttotal_duration = " + str(self.total_duration) + "\n" \
               "\ttime_by_segment (minutes) = " + str(self.time_by_segment) + "\n" \
               "\tdistance_by_segment (km)  = " + str(self.distance_by_segment) + "\n" \
               "----------------------------->>"

    # For each line segment that is part of a path, this method finds its distance and duration
    # and updates the path's information accordingly
    # def __set_paths__full_data(self):
    #     pts = self.coordinates
    #     isFirst = True
    #     last = None
    #     segment_distances = []
    #     segment_durations = []
    #     q = None
    #
    #     # For each line segment in a path do:
    #     for line in pts:
    #         if isFirst:
    #             isFirst = False
    #         else:
    #             sub_path_list, dist, dur = query(last, line, trip_count=1, ROUTE_FROM=self.ROUTE_FROM)
    #
    #             segment_durations.append(dur)
    #             segment_distances.append(dist)
    #
    #         last = line
    #
    #     self.time_by_segment = copy.deepcopy(segment_durations)
    #     self.distance_by_segment = copy.deepcopy(segment_distances)

    # Prints the number of points per kilometer to get a sense of the resolution
    def get_resolution(self):
        pts = self.coordinates

        print("\t"+str(round(len(pts)/self.total_distance,2)) + " points\Km (" + str(len(pts)) + " points for " +
              str(self.total_distance) + 'Km)')
        print(pts)

    def set_risk_of_path(self):
        '''
            Sets the risk of the path
        '''
        self.discretize_path()

        # path_hex = self.hex_of_path()

        self.risk = self.path_risk()

    def set_general_risk_of_path(self):
        # the general assumption is that the person spend equal amount of
        # time in each hexagon. As such, the risk is simple the average of
        # all the hexagon values

        points = []
        for i in range(len(self.coordinates)):
            points.append([self.coordinates[i][1],self.coordinates[i][0]])

        self.hex_ids = hex_of_path(self.grid_gdf, points)
        risks = self.grid_gdf.loc[self.hex_ids]['hex_risk']
        time_per_hex = self.total_duration / len(self.hex_ids)

        self.risk = 0

        for x in risks:
            self.risk += ast.literal_eval(x)[0]

        # self.risk = self.risk / len(risks)

    def get_risk_of_path(self):
        return self.risk

    def discretize_path(self):
        '''
            Discretizes the path. First into  points then into linestrings
        '''
        if len(self.discretized_points) == 0:
            self.set_discretized_points()
        self.set_discretized_linestrings()

    def set_discretized_points(self):
        '''
            Populate list of discrete points on the path.
        '''
        # append the path's starting point
        S = self.coordinates[0]
        self.discretized_points.append(S)

        # determine which of the points on the path are 1 time unit away
        for i in range(1, len(self.coordinates)):
            T = self.coordinates[i]
            # mini_query = queryOSRM(S, T)
            # unit = sum(get_path_points(mini_query)[2])
            routes, dist_tags, duration_tags = query(source=S, destination=T, trip_count=5,ROUTE_FROM=self.ROUTE_FROM)
            unit = sum(duration_tags)

            if unit >= 1:
                self.discretized_points.append(T)
                S = T

        # append the last point in the path if it's not yet included
        if self.coordinates[-1] not in self.discretized_points:
            self.discretized_points.append(self.coordinates[-1])

    def set_discretized_linestrings(self):
        '''
            Populate list of discrete LineStrings on the path.
        '''
        swapped_points = [[pt[1],pt[0]] for pt in self.discretized_points]

        for i in range(len(self.discretized_points)-1):
            s0 = tuple(swapped_points[i])
            s1 = tuple(swapped_points[i+1])
            string = LineString([s0,s1])
            self.discretized_linestrings.append(string)

    # def get_by_segment(self):
    #     return (self.time_by_segment,
    #             self.distance_by_segment)

    def hex_of_path(self):
        '''
            Returns a dictionary
            Params
            ------
            path : a list of the LineStrings of the path
            Return
            -----
            dict : keys = LineStrings and
                   values = list of hexagons intersecting the given LineString
        '''
        hex_ids = list(self.grid_gdf.cellID)
        hexes = list(self.grid_gdf.geometry)

        for ls in self.discretized_linestrings:
            idx = 0
            hexes_in_linestring = []
            for h in hexes:
                if ls.intersects(Polygon(h)):
                    hexes_in_linestring.append(hex_ids[idx])
                idx += 1
            ls_coords = tuple(ls.coords)
            self.hexagons[ls_coords] = hexes_in_linestring

        return self.hexagons

    def path_risk(self):
        '''
            Computes the risk of the path
        :param offset: from what hour to start evaluation. Value ranges between 0 to 167
        :return: returns the risk of the path
        '''

        pathRisk = 0
        t = 0

        for line_hex in self.hexagons.items():
            l_string, hexes = line_hex
            risk_vals = []

            for hex in hexes:
                hex_data = self.grid_gdf[self.grid_gdf['cellID'] == hex]
                hex_risk_dict = ast.literal_eval(hex_data.iloc[0,2])
                risk_vals.append(hex_risk_dict[t])

            risk_vals = [v/len(risk_vals) for v in risk_vals]
            pathRisk += sum(risk_vals)
            t += 1

        # self.risk = pathRisk
        return pathRisk

    def get_risk_of_path_over_a_week(self):
        '''
            Computes and returns the risk of a path over time
        '''
        pathRisks = [0]*168

        t = [60*i for i in range(168)]

        for line_hex in self.hexagons.items():
            l_string, hexes = line_hex
            risk_vals = []
            [risk_vals.append([]) for i in range(168)]

            for hex in hexes:
                hex_data = self.grid_gdf[self.grid_gdf['cellID'] == hex]
                hex_risk_dict = ast.literal_eval(hex_data.iloc[0,2])

                for i in range(168):
                    risk_vals[i].append(hex_risk_dict[t[i]])

            for i in range(168):
                risk_vals[i] = [v/len(risk_vals[i]) for v in risk_vals[i]]
                pathRisks[i] += sum(risk_vals[i])

            for i in range(168):
                t[i] += 1

        return pathRisks

    def get_hexagons(self):
        return self.hexagons


def hex_of_path(grid_gdf, points):
    '''
        Returns a dictionary
        Params
        ------
        path : a list of the LineStrings of the path
        Return
        -----
        dict : keys = LineStrings and
               values = list of hexagons intersecting the given LineString
    '''
    # hex_ids = list(grid_gdf.cellID)
    try:
        hexes = list(grid_gdf.geometry)
    except Exception as e:
        print("ERROR in path 1 : "+str(e))
    try:
        points = [Point(p) for p in points]
    except Exception as e:
        print("\tERROR in path 2 : "+str(e))

    ind = []

    try:
        counter = 0
        for hex in hexes:
            tmp = np.where(np.array([hex.contains(x) or hex.intersects(x) for x in points])==True)[0]
            # print(hex)
            # print(points[0])
            if len(tmp) > 0:
                ind.append(counter)
            counter += 1
    except Exception as e:
        print("\tERROR in path 3 : "+str(e))

    try:
        ind = list(set(list(itertools.chain(*ind))))
    except Exception as e:
        print("\tERROR in path 4 : "+str(e))

    return ind


def risk_map_intersect_poi(grid_gdf, pois):
    # grid_gdf and pois are a geopandas dataframe geopandas.GeoDataFrame()
    hexes = list(grid_gdf.geometry)
    polys = list(pois.polygon_wkt)
    ind = []
    counter = 0
    for hex in hexes:
        tmp = np.where(np.array([hex.contains(x) or hex.intersects(x) for x in polys])==True)[0]

        if len(tmp) > 0:
            ind.append(counter)
        counter += 1

    return ind