import ee

ee.Initialize()

from traitlets import Bool, link
from ipywidgets import Output
from ipyleaflet import GeoJSON
import ipyvuetify as v

from sepal_ui import color as sc
import sepal_ui.sepalwidgets as sw
import sepal_ui.scripts.utils as su


import component.parameter as param
from component.message import cm



__all__ = ["BasinView", "Dashboard"]


class Dashboard(v.Card, sw.SepalWidget):
    def __init__(self, *args, **kwargs):

        self.class_ = "d-block pa-2 mt-4"

        super().__init__(*args, **kwargs)

        title = v.CardTitle(children=["Statistics"])
        # desc = v.CardText(children=['Statistics'])
        self.alert = sw.Alert()

        self.btn_csv = sw.Btn("Download .csv file", class_="mr-2 mb-2").hide()
        self.btn_pdf = sw.Btn("Download .pdf report", class_="mb-2").hide()

        self.output = Output()

        self.children = [
            title,
            # desc,
            self.btn_csv,
            self.btn_pdf,
            self.output,
        ]


class BasinView(v.Card, sw.SepalWidget):
    """Card to capture all the user inputs

    Args:
        model (Model): Model to store the widgets
        map_ (SepalMap): Map to display the output layers
    """


    def __init__(self, model, map_, dashboard, *args, **kwargs):

        self.class_ = "d-block pa-2 mt-4"

        super().__init__(*args, **kwargs)

        self.model = model
        self.map_ = map_

        title = v.CardTitle(children=["Statistics"])
        desc = v.CardText()

        self.alert = sw.Alert()

        self.dashboard = dashboard
        
        self.w_type = sw.Select(
            label=cm.basin.type.label,
            items=[
                {"text":cm.basin.type.all,"value":"all"},
                {"text":cm.basin.type.filter,"value":"filter"}
            ],
            v_model="all",
        )

        self.w_hybasid = sw.Select(
            label=cm.basin.basinid.label,
            items=[],
            v_model=self.model.selected_hybas,
            multiple=True,
            chips=True,
        ).hide()

        self.btn = sw.Btn("Calculate statistics")

        self.children = [title, desc, self.w_type, self.w_hybasid, self.btn, self.alert]

        self.model.observe(self.fill_catchs, "hybasin_list")
        
        self.w_hybasid.observe(self.zoom_to_selected, "v_model")
        self.w_type.observe(self.display_filter, "v_model")
        
        link((self.w_hybasid, 'v_model'), (self.model, 'selected_hybas'))

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

        hybas_id = self.w_hybasid.v_model

        zonal_statistics = self.model.calculate_statistics(hybas_id)

        df = self.model.get_dataframe(zonal_statistics)
        df = df.sort_values(by=["basin", "variable"])
        self.df = df[df["variable"] < 30]

        self.dashboard.btn_pdf.show()
        self.dashboard.btn_csv.show()

        with self.dashboard.output:

            self.dashboard.output.clear_output()

            agg_tips = (
                self.df.groupby(["basin", "variable"])["area"]
                .sum()
                .unstack()
                .fillna(0)
                .T
            )

            import seaborn as sns

            sns.set_theme(style="darkgrid")
            sns.set(rc={"figure.figsize": (20, 8.27)})

            import numpy as np
            from matplotlib import pyplot as plt

            fig, ax = plt.subplots()

            # Initialize the bottom at zero for the first set of bars.
            bottom = np.zeros(len(agg_tips))

            # Plot each layer of the bar, adding each bar to the "bottom" so
            # the next bar starts higher.
            for i, col in enumerate(agg_tips.columns):
                ax.bar(
                    [f"{i + 2000}" for i in self.df["variable"].unique()],
                    agg_tips[col],
                    bottom=bottom,
                    label=col,
                )
                bottom += np.array(agg_tips[col])

            ax.set_title("Deforested area")
            ax.legend()

            self.fig = fig
            display(fig)

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
                style={"fillOpacity": 0.1, "weight": 2, "color":"black"},

            )
        
            self.map_.zoom_bounds(bounds)            
            self.map_.add_layer(selected)
