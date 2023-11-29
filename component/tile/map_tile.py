from traitlets import CFloat, dlink, Bool
from ipyleaflet import LocalTileLayer, WidgetControl
import ipyvuetify as v

from sepal_ui.mapping import SepalMap
import sepal_ui.sepalwidgets as sw

import component.widget as cw
import component.scripts.utils as cu
import component.parameter as param
from component.message import cm


class MapTile(SepalMap):
    lat = CFloat(1.985, allow_none=True).tag(sync=True)
    lon = CFloat(-76.018, allow_none=True).tag(sync=True)

    def __init__(self, model, *args, **kwargs):
        self.model = model

        kwargs["basemaps"] = [
            "TERRAIN",
            "SATELLITE",
        ]
        kwargs["world_copy_jump"] = True
        kwargs["gee"] = False

        super().__init__(*args, **kwargs)

        self.zoom = 10
        self.center = [self.lat, self.lon]
        self.layout.height = "85vh"

        self.trash_btn = TrashMenu()

        trash_control = WidgetControl(
            widget=self.trash_btn,
            position="topleft",
        )

        self.metadata_table = cw.MetadataTable()

        metadata_control = WidgetControl(widget=self.metadata_table, position="topleft")

        self.add_control(trash_control)
        self.add_control(metadata_control)

        dlink((self, "lat"), (self.model, "lat"))
        dlink((self, "lon"), (self.model, "lon"))

        self.on_interaction(self.return_coordinates)

        self.trash_btn.on_event("trash_point", self.trash_event)
        self.trash_btn.on_event("trash_selection", self.trash_event)

    def add_layer(self, layer, *args, **kwargs):
        """Add layer and check its name"""

        if layer.name == param.marker_name:
            self.trash_btn.show()

        super().add_layer(layer, *args, **kwargs)

    def trash_event(self, widget, event, data):
        """restore coordinates and link lat-lon widgets"""

        if widget._metadata["name"] == "trash_point":
            self.restore_coordinates()

            # Link widgets again if automatic (not manual) is selected
            if not self.model.manual:
                self.model.lat_link.link()
                self.model.lon_link.link()

        elif widget._metadata["name"] == "trash_selection":
            self.model.selected_hybas = []

    def restore_coordinates(self, *args):
        """Remove marker and restore coordinates"""

        self.remove_layers_if("type", "marker", _metadata=True)
        self.lat, self.lon = [round(x, 3) for x in self.center]
        self.model.marker = False

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

            marker = cu.get_marker(kwargs.get("coordinates"))
            self.add_layer(marker)
            self.model.marker = True

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


class TrashMenu(sw.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.offset_x = True

        trash_btn = v.Btn(
            v_on="menuData.on",
            small=True,
            children=[
                v.Icon(children=["fa fa-trash"], small=True),
                v.Icon(children=["fa fa-caret-down"], small=True, right=True),
            ],
        )

        self.v_slots = [
            {
                "name": "activator",
                "variable": "menuData",
                "children": trash_btn,
            }
        ]

        self.items = [
            v.ListItem(
                _metadata={"name": title},
                children=[
                    v.ListItemTitle(children=[eval(f"cm.map.trash.{title}")]),
                ],
            )
            for title in ["trash_point", "trash_selection"]
        ]

        self.children = [
            v.List(dense=True, children=self.items),
        ]

    def on_event(self, name, event):
        """Define an event based on the item name"""

        for item in self.items:
            if item._metadata["name"] == name:
                item.on_event("click", event)
