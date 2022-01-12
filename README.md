# Musk-Model
Finding the optimal location for public charging stations – a GIS based MILP approach

# Data Sources
Existing EV charger locations : https://www.gov.uk/guidance/find-and-use-data-on-public-electric-vehicle-chargepoints

Council Managed Car Parks : https://www.manchester.gov.uk/open/homepage/3/manchester_open_data_catalogue

Road shapefiles : https://www.ordnancesurvey.co.uk/business-government/products/open-map-roads

Land-use classification (Geomni - UKLand) : https://digimap.edina.ac.uk/geomni


# Problem
![formulation](https://github.com/obedsims/Musk-Model/blob/main/screenshots/formulation.png)

𝑥𝑗 = binary variable whether car park 𝑗 is selected for a charging station
𝑛𝑗 = number of chargers in station 𝑗
𝑞𝑗 = number of cars charged by station 𝑗
𝑚𝑗 = maximum number of charging sessions per day in station 𝑗
𝑙𝑗 = upper bound of chargers in station 𝑗
𝑟𝑖𝑗 = binary variable which represents the service area coverage level of station j on demand node i
𝑓𝑖 = average traffic flow in grid cell 𝑖
𝐾𝑖 = Number of traffic flow measurement points in grid cell 𝑖




