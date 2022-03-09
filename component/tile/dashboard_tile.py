import ipyvuetify as v
import sepal_ui.sepalwidgets as sw
import component.tile as ct
import component.widget as cw


__all__ = ["DashboardTile"]


class DashboardTile(sw.Layout):
    """Tile to distribute the graphics cards in two rows
    first: will contain the settings and an overall pie chart
    second: Will contain 1-r(piechart, barchart) 2r-(trend-chart)
    """
    
    def __init__(self, model, *args, **kwargs):

        self._metadata = {"mount_id":"dashboard"}
        self.class_ = "pa-4 d-block"
        self.model = model

        super().__init__(*args, **kwargs)
        
        # First row
        self.stat_setting_card = cw.StatSettingCard(
            self.model,
            class_="pa-4 mb-sm-2 mr-md-2",
        )
        self.overall_pie_card = ct.OverallPieCard(self.model)

        # Second row
        self.detail_stat_layout = ct.DetailedStat(self.model)

        overall_row = v.Layout(
            class_="d-flex flex-wrap mb-2",
            children=[
                v.Flex(
                    sm12=True,
                    md5=True,
                    children=[self.stat_setting_card],
                ),
                v.Flex(
                    sm12=True, 
                    md7=True, 
                    children=[self.overall_pie_card]),
            ],
        )
        

        self.children = [
            overall_row, 
            self.detail_stat_layout
        ]
        
        
        self.model.observe(self.update_traces, "ready")
    
    def update_traces(self,_):
        """Update figures traces"""
        
        self.overall_pie_card.update_pie_trace({"new":""})
        self.detail_stat_layout.update_traces({"new":""})
        
