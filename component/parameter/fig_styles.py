from component.message import cm

title = dict(
        font_size=20,
        x=0.5
)

pie_layout =dict(
    title=title
)

legend_overall_pie = dict(
    legend=dict(
        borderwidth=1,
        itemclick="toggleothers",
        orientation="h",
        yanchor="bottom",
        y=-0.4,
        xanchor="right",
        x=1
    )
)

legend_detailed_pie =dict(
    legend=dict(
        borderwidth=1,
        itemclick="toggleothers",
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=0.95
    )
)

pie_trace_options = dict(
    textposition='auto', 
    textinfo='percent', 
    hoverinfo='label+percent+text+value',
    hole=.5,
)


### TOTAL AREA BAR CHART

bar_layout =dict(
    title=title,
    template_layout_plot_bgcolor="#1a1a1a",
    yaxis_title=cm.graphs.bars.yaxis_title,
    showlegend=False,
    uniformtext_minsize=8, 
    uniformtext_mode='hide',
)

bar_trace_options = dict(
    textposition='outside', 
    hoverinfo='x+y+text+name',
)


# LOSS TREND - LINES CHART
trend_title = title.update(text=cm.graphs.trend.title)
trend_layout=dict(
    template_layout_plot_bgcolor="#1a1a1a",
    yaxis_title=cm.graphs.trend.yaxis_title,
    xaxis_title=cm.graphs.trend.xaxis_title,
    showlegend=False,
    title=title,
    hovermode="x unified",
)


trend_trace_options = dict(
    line_shape="spline",
    mode="lines+markers",
)
trend_legend=dict()