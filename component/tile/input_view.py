from traitlets import Bool, link
import ipyvuetify as v

import sepal_ui.sepalwidgets as sw
import sepal_ui.scripts.utils as su

import component.scripts.utils as cu
import component.parameter as param
import component.widget as cw
from component.message import cm


import ee

ee.Initialize()

__all__ = ["InputsView"]


class InputsView(v.Card, sw.SepalWidget):
    """Card to capture all the user inputs

    Args:
        model (Model): Model to store the widgets
        map_ (SepalMap): Map to display the output layers
    """

    valid_dates = Bool(True).tag(sync=True)

    deactivate_coords = Bool(True).tag(sync=True)
    """Wheter to active the coordinates the coordinate fields or not"""

    def __init__(self, model, map_, *args, **kwargs):

        self.class_ = "d-block pa-2"

        super().__init__(*args, **kwargs)

        self.model = model
        self.map_ = map_

        self.alert = sw.Alert()

        title = v.CardTitle(children=["Parameters"])
        desc = v.CardText()

        self.w_years = v.RangeSlider(
            label=cm.inputs.year,
            class_="mt-5",
            thumb_label="always",
            min=2000 + param.gfc_min_year,
            max=2000 + param.gfc_max_year,
        )
        self.w_years.v_model = [self.w_years.min, self.w_years.max]

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

        self.btn = sw.Btn("Get upstream catchments")

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

    @su.loading_button(debug=True)
    def get_upstream(self, *args):
        """Get the upstream catchments from the given coordinates"""

        # Remove previous loaded layers
        self.map_.remove_layers()

        geometry = ee.Geometry.Point((self.model.lon, self.model.lat))
        self.model.get_upstream_basin_ids(geometry)

        upstream_catch = self.model.get_upstream_fc()

        forest_change = self.model.get_gfc(upstream_catch.geometry()).set(param.gfc_vis)

        # Get bounds and zoom to the object
        bounds = self.model.get_bounds(upstream_catch)
        self.map_.zoom_bounds(bounds)

        self.map_.addLayer(forest_change, {}, "Forest change")

        outline = (
            ee.Image().byte().paint(featureCollection=upstream_catch, color=1, width=2)
        )

        self.map_.addLayer(outline, param.basinbound_vis, "Upstream catchment")
