Resilient rives and basins
==========================

Overview
________

The Resilient rivers and basins SEPAL app in its beta version is a tool that will allow you to get statistics about the forest and land cover change over a wide range of years divided by the upstreamcatchments that are draining to the given point. All of these processes can be done directly in your sepal instance without the need of downloading any other app. To run this module we recommend to initialize at least a machine with 2GB RAM (an t2 or m2 instance), please following these steps prior to open the module.

Inputs
______

Once you have opened an isntance, search in the apps tab the “resilient rivers and basins” app, wait for some seconds and the app will be showed up. The module is composed by two main sections, the left side bar, where you can find all the processes (inputs and results) and helpful links (bug report, wiki, source code…); and the right side panel, where the process and inputs are displayed.

By default, the inputs drawer is active. This section is divided by two main panels, in the left you can find all the parameters useful to get the statistics, and the right the map view, where the calculated layers will be loaded.

.. thumbnail:: https://raw.githubusercontent.com/sepal-contrib/basin-rivers/master/doc/img/inputs.png
    :width: 24%
    :title: Inputs view
    :group: inputs
 
The first input is to get a coordinate pair, it will be used to calculate and retrieve all the upstream subcatchments that are draining to that point for the given hydrobasin level. To do so, the module has two options: manual and automatic. Manual selection means that you can  directly write the latitude and the longitude coordinates, click the “next” button and the map will zoom into the area and will set a blue marker in the area of interest; on the other hand, to use the “automatic” selection, switch off the manual switch and navigate trhough the map to find your desired area, click in, and a blue marker will be displayed.
 
.. thumbnail:: https://raw.githubusercontent.com/sepal-contrib/basin-rivers/master/doc/img/coordinates.png
    :width: 24%
    :title: Inputs view
    :group: inputs
 
.. note::

    When use the automatic coordinate selection method, the latitude and longitude text field will be deactivated. Notice that the coordinate will be automatically syncronized while you pass the cursor over the map.
    
Then you have to select the hydrovasin target level using the dropdown list, these levels are ranging from 5 to 12, and means the nested level in the sub basins chain, where the lower levels are the most outer boundaries and the higher levels are the more detailed ones. 

The forest change map is based on the Hansen et., al. 2021 Google Earth Engine product that was done at global scale using Landsat imagery. This product has change data since the year 2001 with respect to the year 2000 as baseline. The process will crop and get the zonal statistics for each of the classes at the given range of analysis: select the start and end year using the sliders. The forest threshold is a metric which determines if a pixel in the Hansen product is considered as forest or not, constraining or unbridle the value, will have different results. 

.. thumbnail:: https://raw.githubusercontent.com/sepal-contrib/basin-rivers/master/doc/img/levels.png
    :width: 24%
    :title: Inputs view
    :group: inputs

Click the “get upstream catchments” button to run the process. Wait some seconds and see the output result in the map: the upstream subcatchments and the forest change map.
 

.. note::
Depending on the selected level and the location of the point, the calculation step will take more or less time. A point at the mouth of a fairly mountainous area and with a high level of detail, will have more upstream sub-basins than those found at higher levels in a same orography.
You can use the top left trash bin button in the map to remove the already set point in the map as well as to remove the subcatchments selection (see the next section, how to constrain the analysis to a given set of sub basins.




 

To calculate and display the statistics in the results dashboard, use the statistics card. There are two selection methods: use all catchments, with means “no filter”, and do “filter”. When using the filter option, a new dropdown menu will appear at the bottom of the card with all the sub catchments ids. Manually select or remove them by clicking each row, notice that the map is automatically syncing the selected catchments with a black boundary, and zooming in its total bounds. Click the “calculate statistics” button and wait until the button state changes from loading to fixed.
 

