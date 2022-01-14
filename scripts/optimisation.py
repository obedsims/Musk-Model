import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pulp import *
from scipy.spatial import distance
from plot_roads import read_shapefile, plot_roads
import math

desired_width = 320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns', 12)

# Import GIS data and car park location data
GIS_data = pd.read_csv('/optimise_EV_location/mean_car_count_per_grid.csv')
car_park_data = pd.read_csv('/optimise_EV_location/council_car_parks_in_grid.csv')
existing_chg_data = pd.read_csv('/optimise_EV_location/existing_ev_charging_locations_touching.csv')

GIS_df = pd.DataFrame(GIS_data)
car_park_df = pd.DataFrame(car_park_data)
existing_chg_df = pd.DataFrame(existing_chg_data)

# Create demand centroids for each cell i
GIS_df['centroid_x'] = (GIS_df['right'] + GIS_df['left'])/2
GIS_df['centroid_y'] = (GIS_df['top'] + GIS_df['bottom'])/2

# Group by id, if id > 1 then there are more than 1 charger in each cell i
existing_chg_df2 = existing_chg_df.groupby(by=['fid']).count().reset_index()

# Drop unneeded columns
drop_columns = ['left', 'top', 'right', 'bottom', 'id', 'latitude', 'longitude']
existing_chg_df2 = existing_chg_df2.drop(labels=drop_columns, axis=1)

# Merge the demand grids ids 'fid' between the two dataframes
GIS_df2 = pd.merge(GIS_df, existing_chg_df2, how='left', on='fid')
GIS_df['no_existing_chg'] = GIS_df2['latitude_touch']
GIS_df.sort_values('fid', ascending=True)


def gen_sets(df_demand, df_parking):
    """Generate sets to use in the optimization problem"""
    # set of charging demand locations (destinations)
    demand_lc = df_demand.index.tolist()
    # set of candidates for charging station locations (currently existing parking lots)
    chg_lc = df_parking.index.tolist()

    return demand_lc, chg_lc


def gen_parameters(df_demand, df_parking):
    """Generate parameters to use in the optimization problem,
    including cost to install charging stations, operating costs and others..."""

    v0 = 0.05   # the charging possibility of an EV in cell i
    u = 0.10    # the EV penetration rate (utilisation rate) - 10 % of each day are used for charging
    pe = 0.17   # price of electricity per kWh (£/kWh)
    lj = 10     # maximum number of chargers in a station
    alpha = 52  # Average battery capacity (kWh)
    N = 10       # Total number of stations to be installed

    Ai = df_demand["mixed_use_area_per_cell"]  # Ai stands for sum of area of the mixed use parts in cell i
    A = df_demand["Area_of_cell"]              # A is the total area of cell i
    vi = Ai / A * v0                           # Where vi is the charging possibility of an EV in cell i
    fi = df_demand["car_count_final"]          # Where fi is the average traffic flow in grid i
    di = u * vi * fi                           # Where di represents the charging demand of EV in grid i
    di = di.to_dict()

    # Fast Chargers
    df_demand['m'] = 2                       # Number of charging sessions per day (session/day)
    m = df_demand['m'].to_dict()
    df_demand['p'] = 2                       # Cost of charging per minute (£/minute) (approx £6-7/30min)
    p = df_demand['p'].to_dict()
    df_demand['t'] = 240                     # Charging time for an EV (minutes)
    t = df_demand['t'].to_dict()
    df_demand['ci_j'] = 1000                 # Installation cost
    ci_j = df_demand['ci_j'].to_dict()
    df_demand['cr_j'] = 30                   # cr_j represents the parking fee per day of parking lot j
    cr_j = df_demand['cr_j'].to_dict()
    df_demand['ce_j'] = 1100                 # ce_j represents the price of a charger in station j
    ce_j = df_demand['ce_j'].to_dict()

    # distance matrix of charging station location candidates and charging demand location
    coords_parking = [(x, y) for x, y in zip(df_parking['Easting'], df_parking['Northing'])]

    coords_demand = [(x, y) for x, y in zip(df_demand['centroid_x'], df_demand['centroid_y'])]

    distance_matrix = distance.cdist(coords_parking, coords_demand, 'euclidean')
    scaling_ratio = 1
    distance_matrix2 = scaling_ratio * distance_matrix
    distance_matrix3 = pd.DataFrame(distance_matrix2, index=df_parking.index.tolist(),
                                    columns=df_demand.index.tolist())

    return di, m, p, t, ci_j, cr_j, ce_j, pe, alpha, lj, N, distance_matrix3


def gen_demand(df_demand):
    """generate the current demand for charging for each cell i"""

    diz = df_demand["no_existing_chg"]  # Number of existing chargers in cell i
    diz = diz.to_dict()

    return diz


def optimize(df_demand, df_parking):

    # Import i and j set function
    demand_lc, chg_lc = gen_sets(df_demand, df_parking)

    # Import parameters function
    di, m, p, t, ci_j, cr_j, ce_j, pe, alpha, lj, N, distance_matrix = gen_parameters(df_demand, df_parking)

    # Import current demand of car park z in cell i
    diz = gen_demand(df_demand)

    # set up the optimization problem
    prob = LpProblem('FacilityLocation', LpMaximize)

    n = LpVariable.dicts("no_of_chgrs_station_j",
                         [j for j in chg_lc],
                         0, lj, LpInteger)
    q = LpVariable.dicts("Remaining_dem_station_j",
                         [j for j in chg_lc],
                         0)
    c = LpVariable.dicts("Tot_costs_station_j",
                         [j for j in chg_lc],
                         0)
    x = LpVariable.dicts("UseLocation", [j for j in chg_lc], 0, 1, LpBinary)

    r = np.full([len(demand_lc), len(chg_lc)], None)

    for i in demand_lc:
        for j in chg_lc:
            if distance_matrix[i][j] <= 500:
                r[i][j] = 1
            else:
                r[i][j] = 0
    count = np.count_nonzero(r == 1)
    print("The number of potential connections with a distance less than 500m is:", count)

    # Objective function
    prob += lpSum(p[j] * t[j] * q[j] - c[j] for j in chg_lc)

    # Create empty dictionary for the remaining demand in cell i
    zip_iterator = zip(demand_lc, [None]*len(demand_lc))
    dr = dict(zip_iterator)

    # For each cell i subtract the existing number of charging stations from the charging demands in cell i
    for i in demand_lc:
        for j in chg_lc:
            dr[i] = di[i] - diz[i] * m[j]
            if dr[i] < 0:       # Can't have negative demand therefore limit minimum demand to zero
                dr[i] = 0

    # Constraints
    for j in chg_lc:
        prob += c[j] == (cr_j[j] + ce_j[j] + ci_j[j] + 0.1 * ce_j[j] + 0.1 * ci_j[j]) * n[j] \
                + pe * alpha * q[j]
    for j in chg_lc:
        prob += q[j] - n[j] * m[j] <= 0                                 # Constraint 1
    for j in chg_lc:
        prob += q[j] - lpSum(r[i][j] * dr[i] for i in demand_lc) <= 0   # Constraint 2
    for i in chg_lc:
        prob += lpSum(x[j] * r[i][j] for j in chg_lc) - 1 <= 0          # Constraint 3
    for j in chg_lc:
        prob += n[j] - x[j] >= 0                                        # Constraint 4
    for j in chg_lc:
        prob += n[j] - lj * x[j] <= 0                                   # Constraint 5

    prob += lpSum(x[j] for j in chg_lc) == N                            # Constraint 6

    prob.solve()
    print("Status: ", LpStatus[prob.status])
    tolerance = .00001
    opt_location = []
    for j in chg_lc:
        if x[j].varValue > tolerance:   # If binary value x is positive then the car park has been selected
            opt_location.append(j)
            print("Establish charging station at parking lot", j)
    df_status = pd.DataFrame({"status": [LpStatus[prob.status]], "Tot_no_chargers": [len(opt_location)]})
    print("Final Optimisation Status:\n", df_status)

    varDic = {}
    for variable in prob.variables():
        var = variable.name
        if var[:5] == 'no_of':      # Filter to obtain only the variable 'no_of_chgrs_station_j'
            varDic[var] = variable.varValue

    for variable in prob.variables():
        var = variable.name
#         print(var)
#         print(variable.varValue)

    var_df = pd.DataFrame.from_dict(varDic, orient='index', columns=['value'])
    # Sort the results numerically
    sorted_df = var_df.index.to_series().str.rsplit('_').str[-1].astype(int).sort_values()
    var_df = var_df.reindex(index=sorted_df.index)
    var_df.reset_index(inplace=True)

    location_df = pd.DataFrame(opt_location, columns=['opt_car_park_id'])
#     print(location_df.head())
#     print(car_park_df.head())
    opt_loc_df = pd.merge(location_df, car_park_df, left_on='opt_car_park_id',  right_index=True, how='left')
    opt_loc_df2 = pd.merge(opt_loc_df, var_df, left_on='opt_car_park_id',  right_index=True, how='left')
#     opt_loc_df2.to_csv(path_or_buf='optimal_locations.csv')

    # Import the road shapefiles
    shp_path_roads_1 = '/optimise_EV_location/Road_Data/SD_region.shp'
    shp_path_roads_2 = '/optimise_EV_location/Road_Data/SJ_region.shp'

    roads_df = plot_roads(shp_path_roads_1, shp_path_roads_2)

    base = roads_df.plot(figsize=(12, 8), color='grey', lw=0.4, zorder=0)
    plot = sns.scatterplot(ax=base, x=opt_loc_df['Easting'], y=opt_loc_df['Northing'], color='dodgerblue', legend='full')
    plot.set_xlim(382181, 389681)
    plot.set_ylim(393634, 402134)
    plot.set_title(f'Optimal locations for {N} chargers')

    for line in range(0, opt_loc_df2.shape[0]):
        plot.text(opt_loc_df2.Easting[line] + 50, opt_loc_df2.Northing[line],
                  opt_loc_df2.value[line], horizontalalignment='left',
                  size='medium', color='black', weight='semibold')

    plt.show()

    return opt_location, df_status
