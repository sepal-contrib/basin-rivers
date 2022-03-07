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

__all__ = ["StatSettingCard", "OverallPieCard", "DetailedStat", ]


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
        
        
class DetailedStat(sw.Layout):
    """Detailed statistics dashboard. It will show specific statistics
    for the selected variable, range date and selected basins.
    """

    def __init__(self, model, *args, **kwargs):

        self.class_ = "d-flex flex-wrap"

        super().__init__(*args, **kwargs)

        self.model = model
        self.base_df = self.model.data
        self.base_df_year = None

        self.catchment_bar_fig = self.get_catch_bar()
        self.catchment_pie_fig = self.get_catch_pie(
            **style.pie_layout, **style.legend_detailed_pie
        )

        self.trend_fig = self.get_trend_fig(**style.trend_layout, **style.trend_legend)

        self.trend_card = sw.Card(children=[self.trend_fig]).hide()

        self.children = [
            v.Flex(
                row=True,
                class_="d-flex flex-wrap",
                children=[
                    v.Flex(
                        xs12=True,
                        sm5=True,
                        children=[
                            cw.Card(
                                class_="mr-sm-2 mb-sm-4",
                                children=[
                                    self.catchment_pie_fig,
                                ],
                            )
                        ],
                    ),
                    v.Flex(
                        xs12=True,
                        sm7=True,
                        children=[
                            cw.Card(
                                children=[
                                    self.catchment_bar_fig,
                                ]
                            )
                        ],
                    ),
                ],
            ),
            v.Flex(row=True, class_="d-block", x12=True, children=[self.trend_card]),
        ]

        # Events
        self.model.observe(self.update_traces, "selected_hybasid_chart")
        self.model.observe(self.update_traces, "selected_var")
        self.model.observe(self.update_traces, "sett_timespan")

        # Trigger the first event
        self.update_traces(_)

    @staticmethod
    def get_catch_bar_trace(x, y, **extra_bar_args):
        """Convenient method to be used multiple times using predefined styles"""

        # Create a trace
        return go.Bar(
            x=x,
            y=y,
            **extra_bar_args,
            **style.bar_trace_options,
        )

    @staticmethod
    def get_trend_trace(x, y, **extra_trend_args):
        """"""

        return go.Scatter(x=x, y=y, **extra_trend_args, **style.trend_trace_options)

    def get_trend_fig(self, **trend_layout_style):
        """Get trend lines figure"""

        return figure_widget(**trend_layout_style)

    def get_catch_bar(self):
        """Returns an stacked bar char of deforested area"""

        # Prepare first view dataframe data (default one)
        catch_area_df = self.base_df.groupby(["basin"]).sum().reset_index()

        catch_bar_trace = self.get_catch_bar_trace(
            x=catch_area_df["basin"],
            y=catch_area_df["area"],
        )

        stacked_bar_fig = figure_widget(**style.bar_layout)
        stacked_bar_fig.add_traces(catch_bar_trace)

        return stacked_bar_fig

    def get_catch_pie(self, **pie_layout):
        """Returns a pie chart with measured variable per catchment"""

        # Create the default pie-chart
        catch_pie_trace = go.Pie(
            labels=self.base_df["basin"],
            values=self.base_df["area"],
            **style.pie_trace_options,
        )

        pie_layout.update(title_text="Total area")

        catchment_pie_fig = figure_widget(**pie_layout)
        catchment_pie_fig.add_traces(catch_pie_trace)

        return catchment_pie_fig

    def add_color(self, df):
        """Add catchment color palette to a filtered dataframe"""

        return pd.merge(
            df,
            self.base_df.groupby(["basin"]).first()[["catch_color"]].reset_index(),
            on="basin",
            how="inner",
        )

    def update_traces(self, _):
        """Update catchment pie and bar chart based on variable/catchment selected"""

        # Index model variables with short name
        base_df = self.base_df
        selected_var = self.model.selected_var
        hybas_id = self.model.selected_hybasid_chart
        from_, to = self.model.sett_timespan

        base_df = base_df[base_df.basin.isin(hybas_id)]

        if not selected_var:
            return

        if selected_var == "all":

            self.trend_card.hide()

            base_df = self.add_color(base_df.groupby(["basin"]).sum().reset_index())

            # Filter by hybas_id with all the variables
            labels = base_df["basin"]
            values = base_df["area"]
            colors = base_df["catch_color"]

            self.catchment_bar_fig.update_traces(
                x=labels, y=values, marker_color=colors
            )
        elif selected_var == "loss":

            self.trend_card.show()

            df = base_df.query(f"year>={from_}&year<={to}")

            df_for_pie = self.add_color(
                df[df.group == "loss"].groupby(["basin", "group"]).sum().reset_index()
            )

            labels, values, colors = (
                df_for_pie["basin"],
                df_for_pie["area"],
                df_for_pie["catch_color"],
            )
            self.catchment_bar_fig.update_layout(barmode="stack")

            with self.catchment_bar_fig.batch_update() and self.trend_fig.batch_update():

                self.catchment_bar_fig.pop("data")
                self.trend_fig.pop("data")

                for basin in df.basin.unique().tolist():

                    x = df[df.basin == basin]["year"]
                    y = df[df.basin == basin]["area"]
                    name = basin
                    marker_color = df[df.basin == basin]["catch_color"]

                    self.catchment_bar_fig.add_trace(
                        self.get_catch_bar_trace(
                            x=x, y=y, name=name, marker_color=marker_color
                        )
                    )
                    self.trend_fig.add_trace(
                        self.get_trend_trace(
                            x=x, y=y, name=name, marker_color=marker_color
                        )
                    )
        else:
            self.trend_card.hide()

            filtered_df = self.add_color(
                base_df[base_df.group == selected_var]
                .groupby(["basin", "group"])
                .sum()
                .reset_index()
            )

            labels, values, colors = (
                filtered_df["basin"],
                filtered_df["area"],
                filtered_df["catch_color"],
            )

            # Check if there is more than one trace
            if len(self.catchment_bar_fig.data) > 1:

                with self.catchment_bar_fig.batch_update():

                    self.catchment_bar_fig.pop("data")
                    self.catchment_bar_fig.add_trace(
                        self.get_catch_bar_trace(
                            x=labels, y=values, marker_color=colors
                        )
                    )
            else:
                self.catchment_bar_fig.update_traces(
                    x=labels, y=values, marker_color=colors
                )
        self.catchment_pie_fig.update_traces(
            labels=labels, values=values, marker_colors=colors
        )

        # Update layouts
        self.catchment_pie_fig.update_layout(title_text=selected_var)
        self.catchment_bar_fig.update_layout(title_text=selected_var)
        self.trend_fig.update_layout(title_text=selected_var)