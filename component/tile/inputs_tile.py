import ipyvuetify as v
import sepal_ui.sepalwidgets as sw

import component.tile as ct


__all__ = ["InputsTile"]

class InputsTile(sw.Layout):
    
    def __init__(self, model, *args, **kwargs):
        
        self._metadata = {"mount_id":"home"}
        self.class_='d-flex flex-wrap'
        
        super().__init__(*args, **kwargs)
        
        map_= ct.MapTile(model=model)
        input_View = ct.InputsView(model=model, map_=map_)
        basin_view = ct.BasinView(model=model, map_=map_)
        
        self.children=[
            sw.Flex(
                class_="pa-2", 
                sm12=True, 
                md4=True, 
                children=[
                    v.Flex(
                        class_="d-block",
                        children=[input_View,basin_view]
                    )
                ]
            ),
            sw.Flex(
                class_="pa-2", 
                sm12=True, 
                md8=True, 
                children=[map_]
            ),
        ]