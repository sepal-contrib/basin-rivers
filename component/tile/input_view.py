from traitlets import Bool, link
from ipywidgets import Layout
from ipyleaflet import GeoJSON
import ipyvuetify as v

import sepal_ui.sepalwidgets as sw
import sepal_ui.scripts.utils as su
from sepal_ui.mapping import SepalMap

import component.scripts.utils as cu
import component.parameter as param
import component.widget as cw
from component.message import cm


import ee

__all__ = ["InputsView"]


class InputsView(cw.Card):
    """Card to capture all the user inputs

    Args:
        model (Model): Model to store the widgets
        map_ (SepalMap): Map to display the output layers
    """

    valid_dates = Bool(True).tag(sync=True)

    deactivate_coords = Bool(True).tag(sync=True)
    """Wheter to active the coordinates the coordinate fields or not"""

    def __init__(self, model, map_: SepalMap, *args, **kwargs):
        self.class_ = "d-block pa-2"

        super().__init__(*args, **kwargs)

        self.model = model
        self.map_ = map_

        self.alert = sw.Alert()

        title = v.CardTitle(children=["Parameters"])
        desc = v.CardText()

        self.w_years = cw.DateSlider()

        self.w_thres = v.Slider(
            label=cm.inputs.thres, class_="mt-5", thumb_label="always", v_model=30
        )

        self.w_level = v.Select(
            class_="mb-3",
            label=cm.inputs.level.label,
            items=[
                {"text": cm.inputs.level.item.format(level), "value": level}
                for level in param.hybas_levels
            ],
            v_model=self.model.level,
        )

        self.w_coords = cw.CoordinatesView(model=model, map_=map_)

        self.btn = sw.Btn("Get upstream catchments", small=True)

        self.children = [
            title,
            desc,
            self.w_coords,
            self.w_level,
            self.w_years,
            self.w_thres,
            self.btn,
            self.alert,
        ]

        self.model.bind(self.w_years, "years").bind(self.w_thres, "thres").bind(
            self.w_level, "level"
        )

        self.btn.on_event("click", self.get_upstream)

    @su.loading_button()
    def get_upstream(self, *args):
        """Get the upstream catchments from the given coordinates"""

        if not self.model.marker:
            raise Exception("Please select a point in the map")
        # Remove previous loaded layers
        self.map_.remove_layers()

        geometry = ee.Geometry.Point((self.model.lon, self.model.lat))
        self.model.get_upstream_basin_ids(geometry)

        upstream_catch = self.model.get_upstream_fc()

        self.model.data = upstream_catch.getInfo()

        # Create GeoJSON ipyleaflet object
        upstream_catch_gj = GeoJSON(
            data=self.model.data,
            name="Upstream catchment",
            style={"fillOpacity": 0.1, "weight": 2},
            hover_style=param.hover_style,
        )

        def update_info(feature, **kargs):
            """Update map box and display feature properties"""
            self.map_.metadata_table.update(feature["properties"])

        upstream_catch_gj.on_hover(update_info)

        forest_change = self.model.get_gfc(upstream_catch.geometry()).set(param.gfc_vis)

        # Get bounds and zoom to the object
        if not hasattr(self.map_, "legend"):
            self.map_.add_legend(title="Legend", legend_dict=param.LEGEND)

        self.map_.zoom_bounds(self.model.get_bounds(self.model.data))
        self.map_.addLayer(forest_change, {}, "Forest change")
        self.map_.add_layer(upstream_catch_gj)
