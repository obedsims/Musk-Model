# Musk-Model
Finding the optimal location for public charging stations – a GIS based MILP approach

# Data Sources
Existing EV charger locations : https://www.gov.uk/guidance/find-and-use-data-on-public-electric-vehicle-chargepoints

Council Managed Car Parks : https://www.manchester.gov.uk/open/homepage/3/manchester_open_data_catalogue

Road shapefiles : https://www.ordnancesurvey.co.uk/business-government/products/open-map-roads

Land-use classification (Geomni - UKLand) : https://digimap.edina.ac.uk/geomni


# Objective function and Constraints
![formulation](https://github.com/obedsims/Musk-Model/blob/main/screenshots/formulation.png)

# Equations


# Symbol Glossary
𝑥𝑗 = binary variable whether car park 𝑗 is selected for a charging station <br />
𝑛𝑗 = number of chargers in station 𝑗 <br />
𝑞𝑗 = number of cars charged by station 𝑗 <br />
𝑚𝑗 = maximum number of charging sessions per day in station 𝑗 <br />
𝑙𝑗 = upper bound of chargers in station 𝑗 <br />
𝑟𝑖𝑗 = binary variable which represents the service area coverage level of station j on demand node i <br />
𝑓𝑖 = average traffic flow in grid cell 𝑖 <br />
𝐾𝑖 = Number of traffic flow measurement points in grid cell 𝑖 <br />
𝑓𝑘𝑖 = Daily traffic flow in grid cell 𝑖 <br />
𝑣𝑖 = Charging possiblility of an EV grid cell 𝑖 <br />
𝑣0 = Daily traffic flow in grid cell 𝑖 <br />
𝐴 = Total area of grid cell 𝑖 <br />
𝐴𝑖 = Sum of mixed-use area in grid cell 𝑖 <br />
𝑑𝑟𝑖 = Remaining demand in grid cell 𝑖 <br />
𝑑𝑖 = Charging demand of an EV in grid cell 𝑖 <br />







