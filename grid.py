import math, geopy
import numpy as np
import pandas as pd
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
# from functional import seq
from geopy.distance import distance
from shapely.geometry import Point, Polygon

# from spatialnet.spatialnet import Trajectory


def generate_hex_grid(bounds, w):
    """Get a hexagonal grid over the provided rectangular area.
    Params
    ------
    bounds : list or dict of floats (north, south, west, east)
        Geo coordinates of input area bounding box
    w : int
        Length of a hex's long side in meters
    """
    if isinstance(bounds, dict):
        north = bounds['north']
        south = bounds['south']
        west = bounds['west']
        east = bounds['east']
    else:
        north, south, west, east = bounds

    # distance between centers of consecutive hexes in each axis
    x_sep = w * 3/4
    y_sep = math.sqrt(3) * w / 4

    # get number of hex rows and columns required to cover input area
    nw = geopy.Point(north, west)
    x_size = distance(nw, geopy.Point(north, east)).meters
    y_size = distance(nw, geopy.Point(south, west)).meters
    n_rows = 1 + int(x_size / x_sep)
    n_cols = 2 + int(y_size / y_sep)
    print("\tConstructing hex grid with {} cells".format(n_rows*n_cols//2))
    print('\trow='+str(n_rows) + ', cols='+str(n_cols))
    # get cell geo coord offset from the start
    # see stackoverflow.com/questions/24427828
    def offset(row, col):
        x = distance(meters=col*x_sep).destination(point=nw,bearing=90)
        return distance(meters=row*y_sep).destination(point=x,bearing=180)

    # get the coordinates of the 6 vertices as a Polygon given its center
    def get_hex(c):
        vertices = [distance(meters=w/2).destination(point=c,bearing=330),
                    distance(meters=w/2).destination(point=c,bearing=30),
                    distance(meters=w/2).destination(point=c,bearing=90),
                    distance(meters=w/2).destination(point=c,bearing=150),
                    distance(meters=w/2).destination(point=c,bearing=210),
                    distance(meters=w/2).destination(point=c,bearing=270)]
        return Polygon([(p.longitude, p.latitude) for p in vertices])

    # hex grid algorithm, see redblobgames.com/grids/hexagons/ for details
    cells = {'cellID':[], 'geometry':[]}
    for row in range(n_cols):
        print(row)
        # print("Cell {}/{} ({:.1f})%".format(
            # row*n_cols//2, n_rows*n_cols//2, 100*row/n_rows), end="\r")
        for col in range(n_rows):
            print('\t',col)
            # doubled coord system
            if (row + col) % 2 == 0:
                center = offset(row, col)
                cells['cellID'].append('Hex_{}_{}'.format(row,col))
                cells['geometry'].append(get_hex(center))

    gdf = GridDataFrame(cells, crs="EPSG:4326")
    # print(gdf.head())
    # return GridDataFrame(cells, crs="EPSG:4326")
    return gdf


class GridDataFrame(gpd.GeoDataFrame):
    """Handles construction and querying of geographical grid blocks."""

    def __init__(self, *args, **kwargs):
        """Initialize GridDataFrame with grid cells as index."""

        super().__init__(*args, **kwargs)
        self.set_index('cellID', inplace=False)


    # def get_cell_counts(self, trajectories):
    #     """Get the count of intersecting trajectories for each cell.
    #     Params
    #     ------
    #     trajectories: GeoDataFrame, Series, iter of Trajectories, LineStrings
    #         Collection of trajectory traces of moving objects.
    #     Returns
    #     -------
    #     pandas.Series of ints
    #         The counts of traces passing through grid cells, indexed by cell
    #     """
        
    #     # transform to Sequence of Linestrings
    #     if isinstance(trajectories, gpd.GeoDataFrame):
    #         ls_seq = seq(trajectories.geometry.to_list())
    #     elif isinstance(trajectories, pd.Series):
    #         ls_seq = seq(trajectories.to_list())
    #     else:
    #         trajectories = list(trajectories)
    #         if isinstance(trajectories[0], Trajectory):
    #             ls_seq = seq(trajectories).map(get_linestring)
    #         else:
    #             ls_seq = seq(trajectories)

    #     bool_seq = ls_seq.map(lambda l: self.geometry.intersects(l))
    #     int_seq = bool_seq.map(lambda s:s.astype(int))
    #     counts_series = pd.Series(int_seq.aggregate(lambda c, a: c + a),
    #                                 index=self.index)
    #     return counts_series


    def plot_map(self, **kwargs):
        """Plot the grid block outlines with a map background.
        
        Params
        ------
        kwargs
            Arguments for GeoDataFrame.plot()
        """

        # plot cells (cells are in the GeoDataFrame 'self')
        ax = self.plot(**kwargs)
        
        # get OpenStreetMap background
        ctx.add_basemap(ax, crs=self.crs.to_string(),
            source=ctx.providers.OpenStreetMap.Mapnik)
        

    def plot_heatmap(self, block_risk, dynamic=False):
        """Plot a heatmap of block risk values.
        Params
        ------
        block_risk : pandas.Series or list/iterable of floats
        """
        
        # if given the whole dataframe, get the first column only
        if isinstance(block_risk, pd.DataFrame):
            b_risk_series = block_risk.iloc[:,0]

        # make sure this is a series and index is grid cell blocks
        elif not isinstance(block_risk, pd.Series):
            b_risk_series = pd.Series(block_risk, index=self.index)
        else:
            b_risk_series = block_risk

        # TODO visualization
        # remember that the cells are in the GeoDataFrame 'self'
        # also self.geometry.bounds is a thing

        heatmap = pd.DataFrame(self)

        # problem: not sure at which timestamp we should plot, now it's the first col
        # I think we can either have dynamic plot or have an aggregate one. 
        # If aggregate, we just need to add up rows
        col = len(block_risk.columns) if dynamic else 1 

        fig, ax = plt.subplots(1, figsize=(10, 6)) 
        
        def set_format():
            variable = 'risk'
            heatmap.plot(column=variable, cmap='Reds', linewidth=0.8, ax=ax, edgecolor='0.8')

            # add a title
            ax.set_title('Risk Map', fontdict={'fontsize': '25', 'fontweight' : '3'})

            # create an annotation for the  data source
            ax.annotate('Source: SUMO generator', xy=(.1, .08), xycoords='figure fraction',
                horizontalalignment='left', verticalalignment='top',
                fontsize=5, color='#555555')

            # create colorbar as a legend
            # problem: in dynamic plotting, colorbars keep showing up in each loop
            if not dynamic:
                sm = plt.cm.ScalarMappable(cmap='Reds', norm=plt.Normalize())
                sm._A = []
                cbar = fig.colorbar(sm)

        i = 0 
        while(i<col): # loop for dynamic plotting
            b_risk_series = block_risk.loc[:,i]
            heatmap['risk'] = b_risk_series
            heatmap = gpd.GeoDataFrame(heatmap)
            set_format()
            plt.tight_layout()
            plt.draw()
            plt.pause(0.1)
            i += 1
            plt.cla()

    @classmethod
    def from_file(cls, *args, **kwargs):
        """Read a GridDataFrame object from file."""

        return GridDataFrame(super().from_file(*args, **kwargs))