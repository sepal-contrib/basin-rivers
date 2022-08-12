Resilient rivers and basins
==========================

Overview
________

The Resilient rivers and basins beta app is a tool that will allow you to get zonal statistics about the forest and forest change over a wide range of years divided by the upstream catchments that are draining to a given point. All of these processes can be done directly into your SEPAL instance without the need of any other source. To run this module we recommend initializing at least a machine with 4GB RAM (an t2 or m2 instance), to more detailed instructions, please refer to `this documentation <https://docs.sepal.io/en/latest/modules/index.html#start-instance-manually>`_.

Inputs
______

Once you have opened an instance, `search in the apps tab <https://docs.sepal.io/en/latest/modules/index.html#start-applications>`_  for the “resilient rivers and basins” app, wait for some seconds and the app will be showed up. The module is composed of two main sections, the left sidebar, where you can find all the processes (inputs and results) at the top and some helpful links (bug report, wiki, source code…) at the bottom; and the right side panel, where the process and inputs are displayed.

By default, the inputs drawer will be active. This section is divided into two main panels, in the left you can find all the input parameters to get the statistics, and on the right: the map view, where the calculated layers will be loaded.

.. thumbnail:: https://raw.githubusercontent.com/sepal-contrib/basin-rivers/master/doc/img/inputs.png
    :width: 80%
    :title: Inputs view
    :group: inputs
 
The first input is to get a coordinate pair, it will be used to calculate and retrieve all the upstream sub-catchments that are draining to it for the given hydro basin level. To do so, the module has two options: manual and automatic. Manual selection means that you can directly write the latitude and the longitude coordinates, click the :code:`next` button and the map will set a blue marker a will zoom into the area of interest; on the other hand, to use the “automatic” selection, switch off the manual switch and navigate through the map to find your desired area, click over it, and a blue marker will be displayed.
 
.. thumbnail:: https://raw.githubusercontent.com/sepal-contrib/basin-rivers/master/doc/img/coordinates.png
    :width: 55%
    :title: Inputs view
    :group: inputs
 
.. note::

    When using the automatic coordinate selection method, the latitude and longitude text fields will be deactivated. Notice that the coordinate will be automatically synchronized while you pass the cursor over the map.
    
The next step is to select the hydro basin target level by using the dropdown list, these levels are ranging from 5 to 12, and means the nested level in the sub-basins chain, where the lower levels are the most outer boundaries and the higher levels are the more detailed ones, to get more info about how this data is obtained, please refer directly to `the source <https://www.hydrosheds.org/products/hydrobasins>`_

The forest change map is based on the `Hansen et al., 2013 Global Forest Change product <https://www.science.org/doi/10.1126/science.1244693>`_ retrieved from `Google Earth Engine <https://developers.google.com/earth-engine/datasets/catalog/UMD_hansen_global_forest_change_2021_v1_9>`_ that was done at a global scale using Landsat imagery. This product has changed data from the year 2001 to the year 2000 as the baseline. The process will crop and get the zonal statistics for each of the classes at the given range of analysis: select the start and end year using the sliders. The forest threshold is a metric that determines if a pixel in the Hansen product is considered a forest or not, constraining or unbridling the value, will have different results. 

.. thumbnail:: https://raw.githubusercontent.com/sepal-contrib/basin-rivers/master/doc/img/levels.png
    :width: 55%
    :title: Settings levels
    :group: inputs

Click the :btn:`get upstream catchments` button to run the process. Wait some seconds and see the output result in the map: the upstream sub-catchments and the forest change map.
 
.. note::
    Depending on the selected level and the location of the point, the calculation step will take more or less time. A point at the mouth of a fairly mountainous area and with a high level of detail will have more upstream sub-basins than those found at higher levels in the same orography.
    
You can use the top left trash bin button in the map to remove the already set point in the map as well as to remove the sub-catchments selection (see the next section, how to constrain the analysis to a given set of sub-basins.

.. thumbnail:: https://raw.githubusercontent.com/sepal-contrib/basin-rivers/master/doc/img/trash_bin.png
    :width: 30%
    :title: Trash bin
    :group: inputs

To calculate and display the statistics in the results dashboard, use the statistics card. There are two selection methods: use all catchments, with means “no filter”, and do “filter”. When using the filter option, a new dropdown menu will appear at the bottom of the card with all the sub-catchments ids. Manually select or remove them by clicking each row, notice that the map is automatically syncing the selected catchments with a black boundary, and zooming in its total bounds. Click the “calculate statistics” button and wait until the button state changes from loading to fixed.
 
Wait patiently until the dashboard is calculated. Once it is done, a red dot will be shown up in the results drawer, as it is shown in the below image:

.. thumbnail:: https://raw.githubusercontent.com/sepal-contrib/basin-rivers/master/doc/img/results_done.png
    :width: 30%
    :title: Done drawer
    :group: inputs

Dashboard
_________

The dashboard panel is divided into three main sections, the top-left settings card, the top-right overall pie chart, and the detailed charts at the bottom of the dashboard.


.. tip::
    All the graphs have the option to be downloaded independently and directly to your browser, just hover the cursor in the top right corner and click on the :icon:`fas fa-camera` icon.
    
In the settings card, you can choose from several variables to display: all, gain and loss, loss, non-forest, forest, and gain, by selecting one of these options all the other graphs will display the statistics accordingly to the selection. From this menu you can also filter the data by one or more sub-catchments, allowing also the chance to generate comparisons between the different areas in a dynamic way.

.. thumbnail:: https://raw.githubusercontent.com/sepal-contrib/basin-rivers/master/doc/img/stats_card.png
    :width: 73%
    :title: Statistics card
    :group: dashboard

The overall ratio is an interactive pie chart that displays the proportion of the output variables. This graph also allows you to directly select the variable to be used in the detailed charts, click over any of the variables and the slice will come out.

.. thumbnail:: https://raw.githubusercontent.com/sepal-contrib/basin-rivers/master/doc/img/overal_pie_ratio.png
    :width: 55%
    :title: Overall pie ratio
    :group: dashboard

The detailed graphs display interactively both, the ratio and the total area of the selected variable. On the left, the pie chart shows the proportion of the area for each of the selected sub-catchments while the right bars chart shows the absolute values.

.. note:: 
    Remember that only the forest loss variable is temporal related. Meaning that a new graph will be shown up at the bottom of the screen, this graph represents the trend of the variable for the selected period.
    
.. image:: https://raw.githubusercontent.com/sepal-contrib/basin-rivers/master/doc/img/interactive_stats.gif
