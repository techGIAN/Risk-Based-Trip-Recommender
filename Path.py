import copy
from shapely import wkt
import pandas as pd
import numpy as np
import geopandas as gpd
import ast
from shapely.geometry import Point, LineString, Polygon

from shapely.geometry import Point, LineString, Polygon
from utilityMethods import query, queryOSRM, get_path_points, get_path_points_OSRM, get_path_points_GRASS_HOPPER

IS_DEBUG_MODE = True
IS_FULL_DEBUG_MODE = True


class Path:
    coordinates = None
    hexagons = dict()
    total_distance = None
    risk = None
    risks = None
    total_duration = None
    time_by_segment = []
    distance_by_segment = []
    discretized_points = []
    discretized_linestrings = []
    id = 0
    grid_gdf = None
    ROUTE_FROM = None

    def __init__(self, coordinates, distance, time, ROUTE_FROM='OSRM', id=0, gdf_file='hex_gdf.csv'):
        self.coordinates = coordinates
        # print(str(self.coordinates[0]))
        self.total_distance = distance
        self.total_duration = time
        self.id = id
        self.ROUTE_FROM = ROUTE_FROM
        self.init_gdf(gdf_file)
    
    def init_gdf(self, gdf_file='hex_gdf.csv'):
        '''
            Initiate the hex grid dataframe
        '''
        df = pd.read_csv(gdf_file)
        df['geometry'] = df['geometry'].apply(wkt.loads)
        grid_gdf = gpd.GeoDataFrame(df, crs='epsg:4326')
        self.grid_gdf = grid_gdf
    
    def set_risk_of_path(self):
        '''
            Sets the risk of the path
        '''
        self.discretize_path()
        path_hex = self.hex_of_path()
        self.risk = self.path_risk()
    # def get_risk_of_path(self):
    #     return self.risk

    def discretize_path(self):
        '''
            Discretizes the path. First into  points then into linestrings
        '''
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
            mini_query = query(S, T, trip_count=1, ROUTE_FROM=self.ROUTE_FROM)
            # unit = sum(get_path_points(mini_query, ROUTE_FROM=self.ROUTE_FROM)[2])
            unit = sum(mini_query[2])
            if unit >= 1:
                self.discretized_points.append(T)
                S = T
                
        # append the last point in the path if it's not yet included
        if T not in self.discretized_points:
            self.discretized_points.append(T)
    
    def set_discretized_linestrings(self):
        '''
            Populate list of discrete LineStrings on the path.
        '''
        for i in range(len(self.discretized_points)-1):
            s0 = tuple(self.discretized_points[i])
            s1 = tuple(self.discretized_points[i+1])
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
            Computes and returns the risk of the path
        '''
        pathRisk = 0
        t = 0

        for line_hex in self.hexagons.items():
            l_string, hexes = line_hex
            risk_vals = []

            for hex in hexes:
                hex_data = self.grid_gdf[self.grid_gdf['cellID'] == hex]
                hex_risk_list = ast.literal_eval(hex_data.iloc[0,2])
                risk_vals.append(hex_risk_list[t])

            risk_vals = [v/len(risk_vals) for v in risk_vals]
            pathRisk += sum(risk_vals)
            t += 1
        
        self.risk = pathRisk
        return pathRisk