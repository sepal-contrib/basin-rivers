import pandas as pd
import plotly.graph_objects as go

import ipyvuetify as v

import sepal_ui.sepalwidgets as sw

import component.scripts as cs
import component.widget as cw
import component.parameter as cp
from component.message import cm
import component.parameter.fig_styles as style

__all__ = ["OverallPieCard", "DetailedStat"]

def figure_widget(**layout_options):
    """Create a figure widget with a plotyly dark theme"""

    ipyfig = go.FigureWidget()
    ipyfig.update_layout(
        template="plotly_dark", 
        template_layout_paper_bgcolor="#1a1a1a",
        **layout_options
    )
    return ipyfig


class OverallPieCard(cw.Card):
    def __init__(self, model, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.model = model
        
        self.grouped_df = None

        self.overall_pie_fig = self.get_overall_pie(
            **style.pie_layout, **style.legend_overall_pie
        )

        self.children = [self.overall_pie_fig]

        # Events
        self.model.observe(self.update_pie_trace, "selected_var")

    def get_overall_pie(self, **pie_layout):
        """Create an overall pie chart."""

        # Create an empty trace
        pie_trace = go.Pie(
            **style.pie_trace_options,
        )

        # Create pie figure
        pie_layout.update(title_text=cm.graphs.overall_pie.title)

        overall_pie_fig = figure_widget(**pie_layout)
        overall_pie_fig.add_traces(pie_trace)

        def pull_pie_event(trace, points, state):
            
            if self.model.zonal_df is None:
                return
            
            grouped_df = self.model.get_overall_pie_df()
            self.model.selected_var = grouped_df.iloc[points.point_inds[0]].group

        overall_pie_fig.data[0].on_click(pull_pie_event)

        return overall_pie_fig

    def update_pie_trace(self, _):
        """Pull chart slices when clicked event

        change (dict): variable (group) class i.e forest, loss, etc.

        """
        
        if self.model.zonal_df is None:
            return
        
        selected_var = self.model.selected_var
        
        grouped_df = self.model.get_overall_pie_df()

        pull_size = 0.1

        if not selected_var == "all":

            update_params = (
                grouped_df[grouped_df.group == selected_var].index[0],
                pull_size,
            )
        else:
            update_params = (None, pull_size)
            
        self.overall_pie_fig.update_traces(
            labels=grouped_df["group"].str.capitalize(),
            values=grouped_df["area"],
            marker_colors=grouped_df["color"],
            pull=cs.get_pull(grouped_df, *update_params)
        )

        
class DetailedStat(sw.Layout):
    """Detailed statistics dashboard. It will show specific statistics
    for the selected variable, range date and selected basins.
    """

    def __init__(self, model, *args, **kwargs):

        self.class_ = "d-block"

        super().__init__(*args, **kwargs)

        self.model = model
        self.base_df_year = None

        self.catchment_bar_fig = self.get_catch_bar()
        self.catchment_pie_fig = self.get_catch_pie(
            **style.pie_layout, **style.legend_detailed_pie
        )

        self.trend_fig = self.get_trend_fig(**style.trend_layout, **style.trend_legend)

        self.trend_card = sw.Card(children=[self.trend_fig]).hide()

        self.children = [
            v.Layout(
                class_="d-flex flex-wrap mb-2",
                children=[
                    v.Flex(
                        sm12=True,
                        md5=True,
                        children=[
                            cw.Card(
                                class_="mr-sm-2 mb-sm-2",
                                children=[
                                    self.catchment_pie_fig,
                                ],
                            )
                        ],
                    ),
                    v.Flex(
                        sm12=True,
                        md7=True,
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
            v.Flex(
                x12=True,
                class_="d-block", 
                children=[self.trend_card]
            ),
        ]

        # Events
        self.model.observe(self.update_traces, "selected_hybasid_chart")
        self.model.observe(self.update_traces, "selected_var")
        self.model.observe(self.update_traces, "sett_timespan")

    @staticmethod
    def get_trend_fig(**trend_layout_style):
        """Get trend figure"""
        
        trend_fig = figure_widget(**trend_layout_style)
        trend_fig.update_layout(title_text="Forest loss trend")

        return trend_fig
    
    @staticmethod
    def get_catch_bar_trace(x=[], y=[], **extra_trace_args):
        """Return a bar trace"""

        # Create a trace
        return go.Bar(
            x=x,
            y=y,
            **extra_trace_args,
            **style.bar_trace_options,
        )

    @staticmethod
    def get_trend_trace(x=[], y=[], **extra_trace_args):
        """Return a line trace"""
        
        return go.Scatter(x=x, y=y, **extra_trace_args, **style.trend_trace_options)

    def get_catch_bar(self):
        """Returns an stacked bar char of deforested area"""

        # Prepare first view dataframe data (default one)
        

        catch_bar_trace = self.get_catch_bar_trace()
        
        stacked_bar_fig = figure_widget(**style.bar_layout)
        stacked_bar_fig.update_layout(title_text="Total area")
        
        stacked_bar_fig.add_traces(catch_bar_trace)

        return stacked_bar_fig

    def get_catch_pie(self, **pie_layout):
        """Returns a pie chart with measured variable per catchment"""

        # Create the default pie-chart
        catch_pie_trace = go.Pie(

            **style.pie_trace_options,
        )

        pie_layout.update(title_text="Wathershed area ratio")

        catchment_pie_fig = figure_widget(**pie_layout)
        catchment_pie_fig.add_traces(catch_pie_trace)

        return catchment_pie_fig

    def add_color(self, dst_df):
        """Add catchment color palette to a filtered dataframe. Useful when the 
        dataframe has been grouped by any other variable and the color is lost."""

        return pd.merge(
            dst_df,
            self.model.zonal_df.groupby(["basin"]).first()[["catch_color"]].reset_index(),
            on="basin",
            how="inner",
        )

    def update_traces(self, _):
        """Update catchment pie and bar chart based on variable/catchment selected"""
        
        # Do nothing if the statistics are not calculated
        if self.model.zonal_df is None:
            return

        # Index model variables with short name
        base_df = self.model.zonal_df
        selected_var = self.model.selected_var
        hybas_id = self.model.selected_hybasid_chart
        from_, to = self.model.sett_timespan

        base_df = base_df[base_df.basin.isin(hybas_id)]
        
        if selected_var == "all":

            base_df = self.add_color(base_df.groupby(["basin"]).sum().reset_index())

            # Filter by hybas_id with all the variables
            labels = base_df["basin"]
            values = base_df["area"]
            colors = base_df["catch_color"]
            
            self.trend_card.hide()
            self.catchment_bar_fig.update_traces(
                x=labels, y=values, text=values, marker_color=colors
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

            with (
                self.catchment_bar_fig.batch_update() and 
                self.trend_fig.batch_update()
            ):

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
                            x=x, 
                            y=y, 
                            name=name, 
                            marker_color=marker_color.unique().tolist()*len(x),
                            line_color=marker_color.unique().tolist()[0]
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
                            x=labels, y=values, marker_color=colors, text=values
                        )
                    )
            else:
                self.catchment_bar_fig.update_traces(
                    x=labels, y=values, text=values, marker_color=colors
                )
        self.catchment_pie_fig.update_traces(
            labels=labels, values=values, marker_colors=colors
        )

        # Update layouts title
        # I will use eval to avoid create a translation transition
        self.catchment_pie_fig.update_layout(
            title_text=eval(f"cm.graphs.detail_pie.{selected_var}")
        )
        self.catchment_bar_fig.update_layout(
            title_text=eval(f"cm.graphs.bars.{selected_var}"),
            xaxis_title=eval(
                f"cm.graphs.bars.xaxis_{'year' if selected_var =='loss' else 'catch'}"
            ),
        )        
        
