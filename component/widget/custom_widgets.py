from traitlets import link as traitlets_link
import ipyvuetify as v
import sepal_ui.sepalwidgets as sw

from component.message import cm
import component.scripts.utils as cu
import component.parameter as param

import ee

ee.Initialize()

__all__ = ["CoordinatesView", "MetadataTable"]


class link(traitlets_link):
    """inherited traitlets link class to add a linked parameter, useful
    to know the current state of the link"""

    def link(self):
        try:
            setattr(
                self.target[0],
                self.target[1],
                self._transform(getattr(self.source[0], self.source[1])),
            )

            self.linked = True

        finally:

            self.source[0].observe(self._update_target, names=self.source[1])
            self.target[0].observe(self._update_source, names=self.target[1])

    def unlink(self):

        try:
            self.source[0].unobserve(self._update_target, names=self.source[1])
            self.target[0].unobserve(self._update_source, names=self.target[1])
            self.linked = False
        finally:
            pass


class CoordinatesView(v.Layout, sw.SepalWidget):
    """Card to capture, and send coordinates to the map through a marker

    Args:
        model (Model): Model to store widget values
        map_ (SepalMap): Map toa display the output layers
    """

    def __init__(self, model, map_, *args, **kwargs):

        self.class_ = "d-flex align-center flex-wrap justify-space-between pa-4"

        super().__init__(*args, **kwargs)

        self.model = model
        self.map_ = map_

        self.w_manual = v.Switch(
            class_="mr-2 ",
            v_model=True,
            label="Manual",
        )

        self.w_lat = v.TextField(
            class_="d-flex",
            label=cm.inputs.lat,
            v_model=self.model.lat,
            disabled=True,
        )

        self.w_lon = v.TextField(
            class_="ml-2 mr-2",
            label=cm.inputs.lon,
            v_model=self.model.lon,
            disabled=True,
        )

        self.btn_use = v.Btn(
            children=[v.Icon(children=["fas fa-arrow-right"])],
            color="primary",
            small=True,
            disabled=True,
            block=True,
        )

        widgets = [self.w_manual, self.w_lat, self.w_lon, self.btn_use]

        self.children = [v.Flex(xs12=True, children=[widget]) for widget in widgets]

        xs = ["sm3", "sm4", "sm4", "sm1"]
        md = ["md4", "md3", "md3", "md2"]

        [
            (setattr(w, xs, True), setattr(w, md, True))
            for w, xs, md in zip(self.children, xs, md)
        ]

        link((self.model, "manual"), (self.w_manual, "v_model"))

        self.model.lat_link = link((self.model, "lat"), (self.w_lat, "v_model"))
        self.model.lon_link = link((self.model, "lon"), (self.w_lon, "v_model"))

        self.w_manual.observe(self.toggle_coords, "v_model")

        self.btn_use.on_event("click", self.send_marker)

    def send_marker(self, widget, event, data):
        """Create a marker using manual coordinates"""

        self.map_.restore_coordinates()

        self.model.lat = self.w_lat.v_model
        self.model.lon = self.w_lon.v_model

        if self.model.manual:
            manual_marker = cu.get_marker([self.model.lat, self.model.lon])
            self.map_.add_layer(manual_marker)

        self.map_.set_center(self.model.lon, self.model.lat)

    def toggle_coords(self, change):

        self.map_.restore_coordinates()

        manual = self.model.manual

        self.w_lat.disabled = not manual
        self.w_lon.disabled = not manual
        self.btn_use.disabled = not manual

        if manual:
            # disabled, then activate link
            self.model.lat_link.unlink()
            self.model.lon_link.unlink()
        else:
            self.model.lat_link.link()
            self.model.lon_link.link()


class MetadataTable(sw.Card):
    """Widget to get a simple table displaying the metadata of catchments"""

    def __init__(self, *args, **kwargs):
        self.max_width = "250px"

        # Create table
        super().__init__(*args, **kwargs)

        # self.close = sw.Icon(children=["mdi-close"], small=True)
        # self.title = sw.CardTitle(class_="pa-0 ma-0", children=[sw.Spacer(), self.close])

        # self.close.on_event("click", lambda *args: self.hide())

    def update(self, data):
        """Create metadata Simple Table based on the given data
        Args:
            data (list of lists): Each element has to follow: [header, value]
        """

        self.show()

        def get_row(header, value):

            return [sw.Html(tag="th", children=[f"{header}: "])] + [
                sw.Html(tag="td", children=[value])
            ]

        rows = [
            sw.Html(tag="tr", children=get_row(str(row_header), str(row_value)))
            for row_header, row_value in data.items()
            if row_header in param.display_prop
        ]

        self.children = [
            sw.SimpleTable(dense=True, children=[sw.Html(tag="tbody", children=rows)])
        ]

    def reset(self):
        """Create an empty table"""

        self.children = []
