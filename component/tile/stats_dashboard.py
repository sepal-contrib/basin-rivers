import pandas as pd
import plotly.graph_objects as go

from copy import deepcopy
from traitlets import link, directional_link

import ipyvuetify as v

import sepal_ui.sepalwidgets as sw

import component.widget as cw
import component.parameter as cp
from component.message import cm
import component.parameter.fig_styles as styles

__all__ = ["StatSettingCard", "OverallPieCard"]


class StatSettingCard(cw.Card):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.class_ = "pa-4"
        self.model = model
        self.first_time = True

        title = v.CardTitle(children=[cm.statistics.title])

        self.w_variable = sw.Select(
            label=cm.statistics.w_variable.label,
            v_model="all",
            items=[{"text": "All variables", "value": "all"}]
            + [
                {"text": eval(f"cm.gfc.{var}"), "value": var}
                for var in list(set(cp.gfc_translation.values()))
            ],
        )
        self.w_years = cw.DateSlider(v_model=self.model.sett_timespan).hide()
        self.w_hybasid = sw.Select(
            label=cm.basin.basinid.label,
            v_model=[],
            items=[],
            small_chips=True,
            multiple=True,
            chips=True,
            deletable_chips=True,
        )

        self.children = [
            title,
            self.w_variable,
            self.w_hybasid,
            self.w_years,
        ]

        # Links
        link((self.w_variable, "v_model"), (self.model, "selected_var"))
        link((self.w_hybasid, "v_model"), (self.model, "selected_hybasid_chart"))

        # UI Events
        self.w_variable.observe(self.show_years, "v_model")

        # model Events
        self.w_years.on_event("change", self.years_event)
        self.w_hybasid.observe(self.at_least_one, "v_model")

        self.w_hybasid.observe(self.fill_items, "items")

        directional_link((self.model, "hybasin_list"), (self.w_hybasid, "items"))

    def at_least_one(self, change):
        """Deactivate the last item when there is only one selectled. Useful
        to avoid showing up graphs without info"""

        widget = change["owner"]
        new_val = change["new"]
        new_items = deepcopy(widget.items)

        if len(widget.v_model) == 1:

            idx = [
                item["index"] for item in widget.items if item["value"] == new_val[0]
            ][0]

            new_items[idx].update(disabled=True)
        elif len(widget.v_model) >= cp.MAX_CATCH_NUMBER:

            for item in widget.items:
                if item["value"] not in new_val:
                    new_items[item["index"]].update(disabled=True)
        else:

            [item.update(disabled=False) for item in new_items]
        widget.items = new_items

    def fill_items(self, _):
        """Fill w_hybasid items once are retreived in the inputs step and select the
        first five(5) elements (arbitrary)"""

        if self.first_time:
            self.w_hybasid.items = [
                {"text": val, "value": val, "disabled": False, "index": idx}
                for idx, val in enumerate(self.model.hybasin_list)
            ]

            self.w_hybasid.v_model = [it["value"] for it in self.w_hybasid.items[:5]]
        self.first_time = False

    def years_event(self, widget, event, data):
        """Workaround event (overriding observe) to avoid double calls in slider.
        it will bind selected years with model data.
        """

        self.model.sett_timespan = data

    def show_years(self, change):
        """Hide years selection widget when loss is selected"""

        if change["new"] == "loss":
            self.w_years.show()
        else:
            self.w_years.hide()



class OverallPieCard(cw.Card):
    def __init__(self, model, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.model = model

        self.base_df = self.model.data
        self.grouped_df = None

        self.overall_pie_fig = self.get_overall_pie(
            **style.pie_layout, **style.legend_overall_pie
        )

        self.children = [self.overall_pie_fig]

        # Events
        self.model.observe(self.update_pie_trace, "selected_var")

    def get_overall_pie(self, **pie_layout):
        """Create an overall pie chart."""

        # Prepare dataframe to show statistics
        # Group by groups
        grouped_df = self.base_df.groupby(["group"]).sum().reset_index()
        grouped_df["color"] = grouped_df["group"].apply(lambda x: cp.gfc_colors_dict[x])
        self.grouped_df = grouped_df

        # Create a trace
        pie_trace = go.Pie(
            labels=grouped_df["group"].str.capitalize(),
            values=grouped_df["area"],
            marker_colors=grouped_df["color"],
            **style.pie_trace_options,
        )

        # Create pie figure
        pie_layout.update(title_text="Overall statistics")

        overall_pie_fig = cw.figure_widget(**pie_layout)
        overall_pie_fig.add_traces(pie_trace)

        def pull_pie_event(trace, points, state):

            self.model.selected_var = grouped_df.iloc[points.point_inds[0]].group

        overall_pie_fig.data[0].on_click(pull_pie_event)

        return overall_pie_fig

    def update_pie_trace(self, change):
        """Pull chart slices when clicked event

        change (dict): variable (group) class i.e forest, loss, etc.

        """

        pull_size = 0.1

        if not change["new"] == "all":

            update_params = (
                self.grouped_df[self.grouped_df.group == change["new"]].index[0],
                pull_size,
            )
        else:
            update_params = (None, pull_size)
        self.overall_pie_fig.update_traces(
            pull=cw.get_pull(self.grouped_df, *update_params)
        )