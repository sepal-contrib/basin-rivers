# Resilient rivers and basins

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


Starting from a point on the map, the module will use the, Global watershed boundaries and sub-basin delineations dataset, derived from [HydroSHEDS](https://www.hydrosheds.org/page/hydrobasins) data at fifteen second resolution, to obtain all the sub-basins that drain towards the selected point at the given detail level.

![inputs](https://raw.githubusercontent.com/sepal-contrib/basin-rivers/master/doc/img/inputs.gif)


The module will generate a dashboard with zonal statistics using the [Global Forest Change dataset v1.8](https://developers.google.com/earth-engine/datasets/catalog/UMD_hansen_global_forest_change_2020_v1_8) published by Hansen et al., where we can find zones of change (forests and non-forests) and zones of no change (gain and loss).

![dashboard](https://raw.githubusercontent.com/sepal-contrib/basin-rivers/master/doc/img/dashboard.gif)