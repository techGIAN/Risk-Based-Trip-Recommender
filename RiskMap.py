# from functional import seq
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
from pprint import pprint
import matplotlib.pyplot as plt
# from haversine import haversine

import grid

class RiskMap():

    bounds = None
    w = None
    grid_gdf = None
    MAX_TIME = 1 #7 * 24 * 60

    # north, south, west, east of Toronto
    # def __init__(self, bounds=[43.872954, 43.531890, -79.906792, -79.139932], w=2000, filename='hex_gdf.csv'):
    def __init__(self, bounds=[43.779574, 43.769315, -79.519378, -79.490257], w=50, filename='hex_gdf.csv'):
        self.bounds = bounds
        self.w = w # w long side in meters (use smaller in actual)
        print('about to generate hex grid ...')
        self.grid_gdf = grid.generate_hex_grid(self.bounds, self.w)
        print('about to compute hex risk...')
        self.compute_hex_risk()
        print('about to save file ...')
        self.to_csv(filename)
        self.plot()
    
    def compute_hex_risk(self):
        '''
            Computes the risk of each hexagon
            Each hexagon has a different risk per time unit
        '''
        self.grid_gdf['hex_risk'] = [self.get_hex_list() for cid in self.grid_gdf['cellID']]

    def get_hex_list(self):
        '''
            Each hexagon will return a list of floats (risks)
            [r0, r1, r2, ...]; the index represents the time unit
        '''
        hex_risks = []

        # First attempt, each hexagon has a random risk
        for t in range(self.MAX_TIME):
            print(t)
            hex_risks.append(round(np.random.rand(),2))

        # Second attempt, each hexagon's risk depends on a) density of people in hex and b) duration
        # TODO later

        return hex_risks
    
    def to_csv(self, filename):
        '''
            Saves the current grid_gdf into a csv file
            Params
            ------
            filename : filename of the file, 'hex_gdf.csv' by default
        '''
        self.grid_gdf.to_csv(filename, index=False)

    def save(self):
        '''
            Saves the hexagons into shapely file
        '''
        self.grid_gdf.to_file("sample/hexes")
    
    def plot(self):
        '''
            Plots hexagons into a figure
        '''
        self.grid_gdf.plot_map(figsize=(10, 6), alpha=0.2, edgecolor='k')
        plt.show()


# r= RiskMap(bounds=[43.793088, 43.754751, -79.527427, -79.478950])
# r= RiskMap()