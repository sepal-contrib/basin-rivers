from traitlets import CFloat, dlink, Bool
from ipyleaflet import LocalTileLayer, WidgetControl

import sepal_ui.sepalwidgets as sw
from sepal_ui.mapping import SepalMap
import ipyvuetify as v

import component.scripts.utils as cu
import component.parameter as param


class MapTile(SepalMap):

    lat = CFloat(1.985, allow_none=True).tag(sync=True)
    lon = CFloat(-76.018, allow_none=True).tag(sync=True)

    def __init__(self, model, *args, **kwargs):

        self.model = model

        kwargs["basemaps"] = [
            "TERRAIN",
            "Google Satellite",
        ]
        kwargs["world_copy_jump"] = True
        kwargs["gee"] = False

        super().__init__(*args, **kwargs)

        self.zoom = 10
        self.center = [self.lat, self.lon]

        self.trash_btn = v.Btn(
            children=[v.Icon(children=["fa fa-trash"], small=True)], small=True
        )
        trash_control = WidgetControl(
            widget=sw.Tooltip(self.trash_btn, "Remove point", right=True),
            position="topleft",
        )
        self.add_control(trash_control)

        dlink((self, "lat"), (self.model, "lat"))
        dlink((self, "lon"), (self.model, "lon"))

        self.on_interaction(self.return_coordinates)
        self.trash_btn.on_event("click", self.trash_event)

    def add_layer(self, layer):
        """Add layer and check its name"""

        if layer.name == param.marker_name:
            self.trash_btn.show()

        super().add_layer(layer)

    def trash_event(self, *args):
        """restore coordinates and link lat-lon widgets"""

        self.restore_coordinates()

        # Link widgets again if automatic (not manual) is selected
        if not self.model.manual:
            self.model.lat_link.link()
            self.model.lon_link.link()

    def restore_coordinates(self, *args):
        """Remove marker and restore coordinates"""

        self.remove_layers_if("type", "marker", _metadata=True)
        self.lat, self.lon = [round(x, 3) for x in self.center]

    def return_coordinates(self, **kwargs):

        """Synchronize the cursor coordinates in the map with lat-lon traits"""

        if not self.model.manual:

            # Only update model coordinates when the widgets are linked
            if self.model.lat_link.linked:

                lat, lon = kwargs["coordinates"]
                self.lat = round(lat, 3)
                self.lon = round(lon, 3)

        if kwargs.get("type") == "click":

            # Stop the comunication between widgets after select the point
            # To avoid changing the captured coordinates
            self.model.lat_link.unlink()
            self.model.lon_link.unlink()

            # Remove markdown if there is one
            self.remove_layers_if("type", "marker", _metadata=True)
            self.remove_layers_if("type", "square", _metadata=True)

            marker = cu.get_marker(kwargs.get("coordinates"))
            self.add_layer(marker)

    def remove_layers_if(self, prop, equals_to, _metadata=False):
        """Remove layers with a given property and value
        Args:
            prop (str): Property or key (if using _metadata) of Layer
            equals_to (str): Value of property or key (if using _metadata) in Layer
            metadata (Bool): Whether the Layers have _metadata attribute or not
        """
        if _metadata:
            for layer in self.layers:
                if hasattr(layer, "_metadata"):
                    if layer._metadata[prop] == equals_to:
                        self.remove_layer(layer)
        else:
            for layer in self.layers:
                if hasattr(layer, prop):
                    if layer.__dict__["_trait_values"][prop] == equals_to:
                        if layer.name == param.marker_name:
                            self.trash_btn.hide()
                        self.remove_layer(layer)

    def remove_layers(self):
        """Remove all layers in map. Except the basemaps"""

        keep_layers = ["Marker", "Google Satellite", "Google Terrain"]

        _ = [
            self.remove_layer(layer)
            for layer in self.layers
            if layer.name not in keep_layers
        ]
