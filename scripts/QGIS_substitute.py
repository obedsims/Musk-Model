import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import shapefile as shp
import pyproj
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon
import mapclassify as mc
from scipy import ndimage
import geopandas as gpd


desired_width = 320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns', 10)


# locate manchester traffic data
data_path = '/optimise_EV_location/manchester_traffic_data.csv'
data = pd.read_csv(data_path)
raw_traffic_df = pd.DataFrame(data=data)
print(raw_traffic_df.info())


# Only use traffic data from the year 2019 and drop useless columns
raw_traffic_df = raw_traffic_df[raw_traffic_df['year'] == 2019]
raw_traffic_df = raw_traffic_df.drop(labels=['region_id', 'region_name', 'local_authority_id', 'local_authority_name',
                                             'start_junction_road_name', 'end_junction_road_name', 'link_length_miles',
                                             'estimation_method'], axis=1)

# Add a coordinate column to the dataframe and convert to UK EPSG:27700 (meters)
proj = pyproj.Transformer.from_crs(4326, 27700, always_xy=True)
x1, y1 = (raw_traffic_df['longitude'], raw_traffic_df['latitude'])
x2, y2 = proj.transform(x1, y1)
x2, y2 = (pd.DataFrame(x2, columns=['horizontal']), pd.DataFrame(y2, columns=['vertical']))
raw_traffic_df = pd.concat([raw_traffic_df, x2, y2], axis=1)

def point_df_to_gdf(df):
    """takes a dataframe with columns named 'longitude' and 'latitude'
    to transform to a geodataframe with point features"""

    df['coordinates'] = df[['longitude', 'latitude']].values.tolist()
    df['coordinates'] = df['coordinates'].apply(Point)
    df = gpd.GeoDataFrame(df, geometry='coordinates')
    return df

traffic_points_gdf = point_df_to_gdf(raw_traffic_df)
print(traffic_points_gdf.head())
# traffic_points_gdf = traffic_points_gdf.set_crs(crs="EPSG:4326")
print('Traffic CRS', '\n', traffic_points_gdf.crs)
traffic_points_gdf.to_file("/optimise_EV_location/Road_Data/traffic_points.shp")

# adding roads to the plot of the traffic measurement points
shp_path_roads_1 = '/optimise_EV_location/Road_Data/SD_Region.shp'
shp_path_roads_2 = '/optimise_EV_location/Road_Data/SJ_Region.shp'
sf_roads_1, sf_roads_2 = (shp.Reader(shp_path_roads_1), shp.Reader(shp_path_roads_2, encoding='windows-1252'))

def read_shapefile(sf):
    """
    Read a shapefile into a Pandas dataframe with a 'coords'
    column holding the geometry information. This uses the pyshp
    package
    """
    fields = [x[0] for x in sf.fields][1:]
    records = sf.records()
    records = [y[:] for y in sf.records()]
    shps = [s.points for s in sf.shapes()]
    df = pd.DataFrame(columns=fields, data=records)
    df = df.assign(coords=shps)
    return df


df_roads_1, df_roads_2 = (read_shapefile(sf_roads_1), read_shapefile(sf_roads_2))
df_roads = pd.concat([df_roads_1, df_roads_2])  # Combine road dataframes into single dataframe

# Select whether to include motorways or not (currently excludes motorways)
df_roads_exc_mtrwy = df_roads[~df_roads['class'].str.contains('Motorway')]
df_roads_exc_mtrwy['coords'] = df_roads_exc_mtrwy['coords'].apply(LineString)
df_roads_exc_mtrwy = gpd.GeoDataFrame(df_roads_exc_mtrwy, geometry='coords')

y_lim = (394500, 400500)                                    # y coordinates (boundaries of city of Manchester)
x_lim = (382000, 387500)                                    # x coordinates (boundaries of city of Manchester)
x1_y1 = (-2.272481011086273, 53.44695395956606)             # latitudes (boundaries of city of Manchester)
x2_y2 = (-2.1899126640044337, 53.50104467521926)            # longitudes (boundaries of city of Manchester)
# inProj = pyproj.CRS(init='epsg:27700')
# outProj = pyproj.CRS(init='epsg:4326')
# x1, y1 = x_lim[0], y_lim[0]
# x2, y2 = x_lim[1], y_lim[1]
# x1, y1 = pyproj.transform(inProj, outProj, x1, y1)
# x2, y2 = pyproj.transform(inProj, outProj, x2, y2)
# print(x1, y1)
# print(x2, y2)
base = df_roads_exc_mtrwy.plot(figsize=(12, 8), color='deepskyblue', lw=0.4, zorder=0)  # Zorder controls the layering of the charts with
base.set_xlim(x_lim)
base.set_ylim(y_lim)
traffic_points_gdf.plot(ax=base, x='horizontal', y='vertical', c='cars_and_taxis', cmap='viridis', kind='scatter', s=7, zorder=10)


def point_grid(y_min, y_max, x_min, x_max):
    """This function takes the coordinate limits and creates a regular grid
    across the area"""

    step_size = 500     # Distance in meters
    gridpoints = []

    x = x_min
    while x <= x_max:
        y = y_min
        while y <= y_max:
            p = (x, y)
            gridpoints.append(p)
            y += step_size
        x += step_size

    grid_df = pd.DataFrame(data=gridpoints, columns=['x', 'y'])
    plt.scatter(grid_df['x'], grid_df['y'], color='maroon', s=2)
    # open the file in the write mode
    # with open('/optimise_EV_location/gridpoints.csv', 'w') as csv_file:
    #     # create the csv writer
    #     csv_file.write('hor;vert\n')
    #     for p in gridpoints:
    #         csv_file.write('{:f};{:f}\n'.format(p.x, p.y))

def polygon_grid(ymin, ymax, xmin, xmax):
    """This function takes the coordinate limits and creates a polygon grid
    across the area"""

    height = 500
    width = 500

    cols = list(np.arange(xmin, xmax + width, width))
    rows = list(np.arange(ymin, ymax + height, height))

    polygons = []
    for x in cols[:-1]:
        for y in rows[:-1]:
            polygons.append(Polygon([(x, y), (x + width, y), (x + width, y + height), (x, y + height)]))
    poly_grid = gpd.GeoDataFrame({'geometry': polygons})
    poly_grid.plot(ax=base, facecolor="none", edgecolor='black', lw=0.7, zorder=15)
    poly_grid.to_file("/optimise_EV_location/Road_Data/grid.shp")


polygon_grid(x1_y1[1], x2_y2[1], x1_y1[0], x2_y2[0])


traffic_points = gpd.read_file("/optimise_EV_location/Road_Data/traffic_points.shp")
print(traffic_points)

polys = gpd.read_file("/optimise_EV_location/Road_Data/grid.shp")

points_polys = gpd.sjoin(traffic_points, polys, how="right")
print(points_polys.head())
print(points_polys.info())
print(points_polys['index_left'].unique())
# print(points_polys.loc[points_polys.index_left == 0, 'cars_and_t'].count())

# Calculate the average of the traffic counts in each grid unit
stats_pt = points_polys.groupby('index_left')['cars_and_t'].agg(['mean'])
stats_pt.columns = ["_".join(x) for x in stats_pt.columns.ravel()]
print(stats_pt)
plt.show()
