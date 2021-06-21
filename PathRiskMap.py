from functional import seq
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
from pprint import pprint
import matplotlib.pyplot as plt
# from haversine import haversine

import grid
import RiskMap as rm

class PathRiskMap():

    bounds = None
    w = None
    grid_gdf = None
    hex_list = [] # hexes of the trips
    risk_list = [] # risks of the trips
    linestring_list = []
    linestring_hex_dict = dict()
    linestring_risk_dict = dict()
    MAX_TIME = 7 * 24 * 60  # discretizing up to every 1 minutes
    risk = 0

    # a dictionary whose keys are hexes and values are dict whose keys are discretized timepoints and values are risks
    hex_risks = dict()

    # a dictionary whose keys are hexes and values are dict whose keys are discretized timepoints and values are num of time units
    hex_units = dict()


    def __init__(self, w=2000):
        # north, south, west, east of Toronto
        self.bounds = [43.855943, 43.580178, -79.545557, -79.170079]
        self.w = w # w long side in meters (use smaller in actual)
        self.grid_gdf = grid.generate_hex_grid(self.bounds, self.w)
        # print('grid gdf create ok')
        # self.grid_gdf['hex_risk'] = dict()
        # print('creation of dic ok')
        # num_of_rows = self.grid_gdf.shape[0]
        # self.grid_gdf['hex_risk'] = dict()
        # self.grid_gdf['hex_risk'] = np.random.rand(num_of_rows)
        # self.grid_gdf['hex_risk'][1] = np.random.rand(num_of_rows)
        # print('RiskMap init ok')
        # self.grid_generator()

    



    def risk_of_trips(self, paths):
        '''
            Compute the risks of paths; store the results in a list
        '''
        # pathRisk_dict = dict()
        for path in paths:
            # pathRisk_dict[path] = self.path_risk(path=path)
            self.risk_list.append(self.path_risk(path=path))

        # return pathRisk_dict
        return self.risk_list
    
    def get_grid(self):
        return self.grid_gdf
    
    def set_linestring(self, ls):
        self.linestring_list = ls

    

    def save(self):
        self.grid_gdf.to_file("sample/hexes")
    
    def plot(self):
        self.grid_gdf.plot_map(figsize=(10, 6), alpha=0.2, edgecolor='k')
        plt.show()

    

    