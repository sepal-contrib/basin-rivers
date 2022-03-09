from sepal_ui import color as sc


gfc_min_year = 0
gfc_max_year = 20
gfc_dataset = "UMD/hansen/global_forest_change_2020_v1_8"
gfc_names = {30: "non_forest", 40: "forest", 50: "gain", 51: "gain_loss"}

year_range = list(range(0, gfc_max_year + 1))

gfc_classes = year_range + [30, 40, 50, 51]

gfc_labels = [f"loss_{y+2000}" for y in year_range] + [
    "non_forest",
    "forest",
    "gain",
    "gain_loss",
]


# Create a group for each category and a translation dictionary
gfc_groups = ["loss"]*(gfc_max_year+1) + gfc_labels[gfc_max_year+1:]
gfc_translation = dict(
    zip(gfc_classes, gfc_groups)
)

year_items = [{"text": str(y + 2000), "value": y} for y in year_range]

hybas_dataset = "WWF/HydroSHEDS/v1/Basins/hybas_{}"
hybas_levels = list(range(5, 13))

# Create a visualization parameters to the selected element
selected_vis = {"palette": "red"}
basinbound_vis = {"palette": "black"}

# Create a name to the marker point in the map

marker_name = "Marker"


# Catchment properties to display
display_prop = ["HYBAS_ID"]


# Define a maximum number of catchments to display on the detailed graphs
MAX_CATCH_NUMBER = 10

