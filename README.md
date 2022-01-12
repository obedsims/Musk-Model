# Musk-Model
Finding the optimal location for public charging stations – a GIS based MILP approach

# Data Sources
Existing EV charger locations : https://www.gov.uk/guidance/find-and-use-data-on-public-electric-vehicle-chargepoints

Council Managed Car Parks : https://www.manchester.gov.uk/open/homepage/3/manchester_open_data_catalogue

Road shapefiles : https://www.ordnancesurvey.co.uk/business-government/products/open-map-roads

Land-use classification : https://data.gov.uk/dataset/8b8c5df3-d7e3-484c-89d8-c7b819205002/national-historic-landscape-characterisation-250m-grid-england/

# Objective function and Constraints
![formulation](https://github.com/obedsims/Musk-Model/blob/main/screenshots/formulation.png)



It is assumed that each charger is possible to charge 𝑚 cars at most per day, and constraint (2) and (3) make sure that the cars charged in the station are less than both the capacity of the station and the charging demand. Constraint (4) ensures that the remaining charging demand in grid 𝑖 are in the service area of only one station, which ensures that different demand nodes are distributed to different charging stations. Formula (5) and (6) ensure that each station would have at least one charger and at most 𝑙𝑗 chargers, this can be determined according to the constraints at different points in the power grid. Moreover, the constraints also have the logical implication for example if there is no station, there is no charger and vice versa. Also, a company may have a maxmimum budget allocated to placing charging stations, so at most N stations would be placed in the city according to formula (7). Constraint (8) ensures all the decision variables are integers and non-negative.

# Equations
![equations](https://github.com/obedsims/Musk-Model/blob/main/screenshots/equations.png)


# Symbol Glossary
𝑥𝑗 = binary variable whether car park 𝑗 is selected for a charging station <br />
𝑛𝑗 = number of chargers in station 𝑗 <br />
𝑞𝑗 = number of cars charged by station 𝑗 <br />
𝑚𝑗 = maximum number of charging sessions per day in station 𝑗 <br />
𝑙𝑗 = upper bound of chargers in station 𝑗 <br />
𝑟𝑖𝑗 = binary variable which represents the service area coverage level of station 𝑗 on demand node 𝑖 <br />
𝑓𝑖 = average traffic flow in grid cell 𝑖 <br />
𝐾𝑖 = number of traffic flow measurement points in grid cell 𝑖 <br />
𝑓𝑘𝑖 = daily traffic flow in grid cell 𝑖 <br />
𝑣𝑖 = charging possiblility of an EV grid cell 𝑖 <br />
𝑣0 = daily traffic flow in grid cell 𝑖 <br />
𝐴 = total area of grid cell 𝑖 <br />
𝐴𝑖 = sum of mixed-use area in grid cell 𝑖 <br />
𝑑𝑟𝑖 = remaining demand in grid cell 𝑖 <br />
𝑑𝑖 = charging demand of an EV in grid cell 𝑖 <br />
𝑑𝑖𝑧 = charging demand of an EV in grid cell 𝑖 already being met by existing station z <br />
𝑐𝑗 = total costs of station 𝑗 <br />
𝑐<sup>𝑒</sup>𝑗 = capital cost of station 𝑗 <br />
𝑐<sup>𝑖</sup>𝑗 = installation cost of station 𝑗 <br />
𝑝𝑒 = price of electricity per kWh <br />
α = average capacity of EV battery (kWh) <br />

