import ee

ee.Initialize()

from traitlets import Bool, link
from ipywidgets import Output
from ipyleaflet import GeoJSON
import ipyvuetify as v

from sepal_ui import color as sc
import sepal_ui.sepalwidgets as sw
import sepal_ui.scripts.utils as su


import component.widget as cw
import component.parameter as param
from component.message import cm



__all__ = ["BasinView"]


class BasinView(cw.Card):
    """Card to capture all the user inputs

    Args:
        model (Model): Model to store the widgets
        map_ (SepalMap): Map to display the output layers
    """

    def __init__(self, model, map_, *args, **kwargs):

        self.class_ = "d-block pa-2 mt-4"

        super().__init__(*args, **kwargs)

        self.model = model
        self.map_ = map_

        title = v.CardTitle(children=["Statistics"])
        desc = v.CardText()

        self.alert = sw.Alert()
        
        self.w_type = sw.Select(
            label=cm.basin.type.label,
            items=[
                {"text": cm.basin.type.all, "value": "all"},
                {"text": cm.basin.type.filter, "value": "filter"},
            ],
            v_model="all",
        )

        self.w_hybasid = sw.Select(
            label=cm.basin.basinid.label,
            items=[],
            v_model=[],
            multiple=True,
            chips=True,
        ).hide()

        self.btn = sw.Btn("Calculate statistics", small=True,)

        self.children = [title, desc, self.w_type, self.w_hybasid, self.btn, self.alert]

        self.model.observe(self.fill_catchs, "hybasin_list")

        self.w_hybasid.observe(self.zoom_to_selected, "v_model")
        self.w_type.observe(self.display_filter, "v_model")

        link((self.w_hybasid, "v_model"), (self.model, "selected_hybas"))
        link((self.w_type, "v_model"),(self.model, "method"))

        self.btn.on_event("click", self.calculate_statistics)

    def display_filter(self, change):
        """Display hybasin id filter widget"""

        if change["new"] == "filter":
            self.w_hybasid.show()

        else:
            # All is selected
            self.w_hybasid.hide()
            if self.model.data:
                self.map_.zoom_bounds(self.model.get_bounds(self.model.data))

    @su.loading_button(debug=True)
    def calculate_statistics(self, widget, event, data):
        """Calculate zonal statistics based on the selected hybas_id"""
        
        self.model.ready = False

        zonal_statistics = self.model.calculate_statistics()
        
        self.model.zonal_df = self.model.get_dataframe(zonal_statistics)
        
        # Graphs dashboard is listening this trait to load its data
        self.model.ready = True
        


    def fill_catchs(self, change):
        """Fill the selection widget list with the gathered"""

        new_items = [{"text": hybasid, "value": hybasid} for hybasid in change["new"]]

        self.w_hybasid.items = new_items

    def zoom_to_selected(self, change):
        """Highlight selection and zoom over it"""

        self.map_.remove_layers_if("name", "Selected")

        if not change["new"]:
            return

        else:

            # Get bounds and zoom to the object
            selected = self.model.get_selected(change["new"], from_json=True)
            bounds = self.model.get_bounds(selected)

            selected = GeoJSON(
                data=selected,
                name="Selected",
                style={"fillOpacity": 0.1, "weight": 2, "color": "black"},
            )

            self.map_.zoom_bounds(bounds)
            self.map_.add_layer(selected)

            