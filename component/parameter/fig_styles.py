
pie_layout =dict(
    title=dict(
        font_size=20,
        x=0.5
    ),
    legend=dict(
        borderwidth=1,
        itemclick="toggleothers",
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="right",
        x=1
    )
)


bar_layout =dict(
    title=dict(
        font_size=20,
        x=0.5
    ),
    legend=dict(
        borderwidth=1,
        itemclick="toggleothers",
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="right",
        x=1
    )
)

pie_trace_options = dict(
    textposition='auto', 
    textinfo='percent', 
    hoverinfo='label+percent+text+value',
    hole=.4,
)


bar_trace_options = dict(
    textposition='auto', 
    hoverinfo='x+y+text+name',
)