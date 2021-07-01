# imports
import pandas as pd
import numpy as np
import geopandas as gpd
import shapely
from shapely.geometry import Polygon
from shapely import wkt
import ast
import pyproj
from pyproj import Geod
import copy

# read datasets
poi_df = pd.read_csv('ca-geometry.csv')
patterns_df = pd.read_csv('2021-04-19-weekly-patterns.csv')
pop_df = pd.read_csv('ca-pop-da.csv')
home_df = pd.read_csv('2021-04-19-home-panel-summary.csv')
core_df = pdf.read_csv('core-poi.csv')

# lambda functions
def home_cbg_filler(x):
    if x['home_cbgs']:
        return x['home_cbgs']
    else:
        return [x['poi_cbg']]

def cbg_val_filler(x):
    if x['cbgs_vals']:
        return x['cbgs_vals']
    else:
        return [1]

def origin_cbg_filler(x):
    return x['home_cbgs'][x['counter_col']]

def visitor_home_cbg_filler(x):
    return x['cbgs_vals'][x['counter_col']]

def normalized_visits(x):
    return [float(v)/sum(x['visits_by_each_hour']) for v in x['visits_by_each_hour']]

def true_hourly_visits(x):
    return [x['ext_visits_upper']*float(v) for v in x['normalized_hourly_visits']]

def extract_lon_lats_from_polygon_wkt(polygon_wkt):
    polygon_latlon = shapely.wkt.loads(polygon_wkt)
    polygon_points = list(polygon_latlon.exterior.coords)
    lon, lat = zip(*polygon_points)
    return(lon,lat)

def get_geodesic_area(polygon_wkt, ellps_model='IAU76'):
    # Default uses model of Earth IAU 1976 https://en.wikipedia.org/wiki/IAU_(1976)_System_of_Astronomical_Constants 
    geod = Geod(ellps=ellps_model)
    lon, lat = extract_lon_lats_from_polygon_wkt(polygon_wkt)
    poly_area, poly_perimeter = geod.polygon_area_perimeter(lon, lat) # in square meters
#     square_feet_meter_conv = 10.7639 # square feet in 1 square meter
#     poly_area = poly_area * square_feet_meter_conv
    return(abs(poly_area))

def tuple_key(x):
    poi_cbg = str(x['poi_cbg'])
    return (x['location_name'], poi_cbg)

def comp_poi_risk(x):
    return [v*x['median_dwell']/np.sqrt(x['geodesic_area']) for v in x['true_hourly_visits']]

# get the population per dissemination area (cbg)
pop_df.rename(columns={'Population, 2016': 'population', 'Geographic code':'dissemination_area'}, inplace=True)
pop_df.drop(pop_df.columns.difference(['dissemination_area','population']), 1, inplace=True)
pop_df = pop_df[:-6] # remove some garbage
pop_df['dissemination_area'] = pop_df.dissemination_area.apply(int)

# modify NaNs and 0s
prev_count = 0
curr_count = 0
missing_code_list = []
for i in range(pop_df.shape[0]):
    if not np.isnan(pop_df.iloc[i,1]) and pop_df.iloc[i,1] > 0:
        curr_count = pop_df.iloc[i,1]
        new_pop = np.mean([prev_count, curr_count])
        for code in missing_code_list:
            pop_df.loc[(pop_df.dissemination_area == code), 'population'] = new_pop
        prev_count = curr_count
        missing_code_list = []
    else:
        missing_code_list.append(pop_df.iloc[i,0])

pop_df['population'] = pop_df.population.apply(int)
pop_df['dissemination_area'] = pop_df.dissemination_area.apply(str)

patterns_temp = patterns_df.copy()

patterns_list_columns = ['location_name','raw_visit_counts', 'raw_visitor_counts', 'visits_by_day',
                         'visits_by_each_hour', 'poi_cbg', 'visitor_home_cbgs', 'median_dwell']
patterns_df['poi_cbg'] = patterns_df.poi_cbg.apply(lambda x: int(x[3:]))
patterns_df.drop(patterns_df.columns.difference(patterns_list_columns), 1, inplace=True)

expdf = patterns_df.copy()
expdf.drop(['median_dwell'], axis=1, inplace=True)
expdf['origin_cbg'] = None

cols = expdf.columns.tolist()
cols = cols[0:1] + cols[-1:] + cols[1:-1]
expdf = expdf[cols]

expdf['visitor_home_cbgs'] = expdf.visitor_home_cbgs.apply(eval)
expdf['count_col'] = expdf.visitor_home_cbgs.apply(len)

expdf['count_col'] = expdf.count_col.apply(lambda x: max(x,1))
expdf['home_cbgs'] = expdf.visitor_home_cbgs.apply(list)
expdf['home_cbgs'] = expdf.home_cbgs.apply(lambda x: [c[3:] for c in x])
expdf['cbgs_vals'] = expdf.visitor_home_cbgs.apply(lambda x: list(x.values()))

expdf['home_cbgs'] = expdf.apply(home_cbg_filler, axis=1)
expdf['cbgs_vals'] = expdf.apply(cbg_val_filler, axis=1)

# counter_col
expdf = expdf.loc[expdf.index.repeat(expdf['count_col'])]
expdf.insert(0, 'counter_col', expdf.groupby(level=0).cumcount())
expdf = expdf.reset_index(drop=True)

expdf['origin_cbg'] = expdf.apply(origin_cbg_filler, axis=1)
expdf['visitor_home_cbgs'] = expdf.apply(visitor_home_cbg_filler, axis=1)

expdf['est_visits_per_visitor'] = expdf['raw_visit_counts']/expdf['raw_visitor_counts']
expdf['visitor_home_lower'] = expdf.visitor_home_cbgs.apply(lambda x: 2 if x == 4 else x)
expdf['visitor_home_upper'] = expdf.visitor_home_cbgs.apply(lambda x: 4 if x == 4 else x)

# set checkpoint
temp_expdf = expdf.copy()

# extract cbg and number_devices_residing (SG sample number) from home_df
home_columns = ['census_block_group', 'number_devices_residing']
home_df.drop(home_df.columns.difference(home_columns), 1, inplace=True)
home_df['census_block_group'] = home_df.census_block_group.apply(lambda x: str(x[3:]))

expdf = temp_expdf.copy()

# join expdf and home_df
expdf = expdf.join(home_df.set_index('census_block_group'), on='origin_cbg')
expdf['number_devices_residing'] = expdf['number_devices_residing'].fillna(1)
expdf['number_devices_residing'] = expdf.number_devices_residing.apply(int)

# join expdf and pop_df
expdf['origin_cbg'] = expdf.origin_cbg.apply(str)
expdf = expdf.join(pop_df.set_index('dissemination_area'), on='origin_cbg')
expdf = expdf[~expdf['population'].isnull()]
expdf['population'] = expdf.population.apply(int)

# filling extrapolated visitor and visits
expdf = expdf.rename(columns={'number_devices_residing':'safegraph_sample_size'})
expdf['scale_factor'] = expdf['population']/expdf['safegraph_sample_size']
expdf['ext_visitor_upper'] = expdf['scale_factor']*expdf['visitor_home_upper']
expdf['ext_visits_upper'] = expdf['ext_visitor_upper']*expdf['est_visits_per_visitor']

# drop unnecessary columns
expdf = expdf.drop(columns=['counter_col', 'origin_cbg', 'home_cbgs', 'cbgs_vals', 'visitor_home_lower',
                           'visitor_home_upper', 'safegraph_sample_size', 'population', 'scale_factor'])

# adding the cum_sum column -- used to perform groupby for consecutive same rows
expdf['shift'] = expdf.poi_cbg.shift(1)
expdf['b_val'] = expdf['poi_cbg'] != expdf['shift']
expdf['cum_sum'] = expdf.b_val.cumsum()
expdf['cum_sum'] = expdf['cum_sum']-1

# take only specific columns bec we want to aggregate (sum) rows having same cum_sum
# then do group by and reset the indices
expdf_copy = expdf.drop(expdf.columns.difference(['location_name','poi_cbg', 'cum_sum', 'ext_visitor_upper', 'ext_visits_upper']), 1)
expdf_copy = expdf_copy.groupby(['cum_sum', 'poi_cbg', 'location_name']).sum().reset_index()

# get only specific columns
expdf_copy5 = pd.DataFrame(columns=['ext_visitor_upper','ext_visits_upper'])
expdf_copy5[['ext_visitor_upper','ext_visits_upper']] = expdf_copy[['ext_visitor_upper','ext_visits_upper']]

expdf_copy3 = expdf.drop(expdf.columns.difference(['location_name','poi_cbg', 'cum_sum', 'visits_by_each_hour']), 1)
expdf_copy4 = expdf_copy3.drop_duplicates()
expdf_copy4 = expdf_copy4.reset_index().drop(columns=['index'])
extrapolation_df = pd.concat([expdf_copy4, expdf_copy5], axis=1)

# checkpoint
tempextrap = extrapolation_df.copy()

# need the extrapolation_df
extrapolation_df['visits_by_each_hour'] = extrapolation_df.visits_by_each_hour.apply(eval)
extrapolation_df['total_visits'] = extrapolation_df.visits_by_each_hour.apply(sum)
extrapolation_df['total_visits'] = extrapolation_df.total_visits.apply(float)
extrapolation_df['normalized_hourly_visits'] = extrapolation_df.apply(normalized_visits, axis=1)
extrapolation_df['true_hourly_visits'] = extrapolation_df.apply(true_hourly_visits, axis=1)

patterns_df = patterns_temp.copy()
patterns_df['poi_cbg'] = patterns_df.poi_cbg.apply(str)
patterns_df['poi_cbg'] = patterns_df.poi_cbg.apply(lambda x: x[3:])
patterns_df['tup_key'] = patterns_df.apply(tuple_key, axis=1)

extrapolation_df['tup_key'] = extrapolation_df.apply(tuple_key, axis=1)

dwell_df = pd.DataFrame(columns=['tup_key', 'safegraph_place_id', 'median_dwell'])
dwell_df[['tup_key', 'safegraph_place_id', 'median_dwell']] = patterns_df[['tup_key', 'safegraph_place_id', 'median_dwell']]

extrapolation_dwell_df = extrapolation_df.join(dwell_df.set_index('tup_key'), on='tup_key')

# preprocess
poi_df = poi_df[poi_df['iso_country_code'] == 'CA']
poi_df['bool_poly'] = poi_df.polygon_wkt.apply(lambda x: 'MULTIPOLYGON' in x)
poi_df = poi_df[~poi_df['bool_poly']]
poi_df = poi_df.drop(columns=['bool_poly', 'location_name'])

# get area in sq metres
poi_df['geodesic_area'] = poi_df['polygon_wkt'].apply(get_geodesic_area, ellps_model='IAU76')

# join extrapolation_dwell_df and poi_df
poi_risk_df = poi_df.join(extrapolation_dwell_df.set_index('safegraph_place_id'), on='safegraph_place_id')

poi_risk_df = poi_risk_df[poi_risk_df['median_dwell'].notna()]
poi_risk_df = poi_risk_df[poi_risk_df['true_hourly_visits'].notna()]
poi_risk_df = poi_risk_df[poi_risk_df['geodesic_area'].notna()]

poi_risk_df['poi_risk'] = poi_risk_df.apply(comp_poi_risk, axis=1)
poi_risk_df = poi_risk_df.reset_index().drop(columns=['index'])

poi_risk_dataframe = poi_risk_df[['placekey', 'safegraph_place_id', 'location_name', 'latitude', 'longitude', 'poi_risk']]
core_df = core_df[['placekey', 'top_category']]
poi_risk_dataframe = pd.merge(poi_risk_dataframe, core_df, on='placekey')

for i in range(24*7):
    name = 'poiRisk_' + str(i)
    poi_risk_dataframe[name] = poi_risk_dataframe.poi_risk.apply(lambda x: x[i])

poi_risk_dataframe = poi_risk_dataframe.drop(columns=['poi_risk'])

poi_risk_dataframe.to_csv('ca_poi_risks_2021-04-19-one-week.csv', index=False) #save
poi_risk_dataframe.head()