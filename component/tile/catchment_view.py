import ee
ee.Initialize()

from traitlets import Bool, link
import ipyvuetify as v

from sepal_ui import color as sc
import sepal_ui.sepalwidgets as sw
import sepal_ui.scripts.utils as su


import component.parameter as param
from component.message import cm

__all__ = ["BasinView"]


class BasinView(v.Card, sw.SepalWidget):
    """Card to capture all the user inputs
    
    Args:
        model (Model): Model to store the widgets
        map_ (SepalMap): Map to display the output layers
    """
    
    all_item = [{'text': "All catchments",'value':'all'}]


    def __init__(self, model, map_, *args, **kwargs):

        self.class_ = "d-block pa-2 mt-4"

        super().__init__(*args, **kwargs)

        self.model = model
        self.map_ = map_
        
        self.alert = sw.Alert()

        self.w_hybasid = v.Select(
            label=cm.basin.basinid.label,
            items=self.all_item,
            v_model=self.model.hybasin_id,
            multiple=True, 
            chips=True,
            filled=True,
        )
        
        self.btn = sw.Btn('Calculate statistics')
        
        self.children = [self.w_hybasid, self.btn, self.alert]
        
        self.model.observe(self.fill_catchs, 'hybasin_list')
        self.w_hybasid.observe(self.zoom_to_selected, 'v_model')
        
        self.btn.on_event('click', self.calculate_statistics)
    
    @su.loading_button(debug=True)
    def calculate_statistics(self, widget, event, data):
        """Calculate zonal statistics based on the selected hybas_id"""
        
        hybas_id = self.w_hybasid.v_model
        
        zonal_statistics = self.model.calculate_statistics(hybas_id)
        self.df = self.model.get_dataframe(zonal_statistics)
        

    def fill_catchs(self, change):
        """Fill the selection widget list with the gathered"""
        
        new_items = [
            {'text': hybasid, 'value': hybasid} for hybasid in change['new']
        ]
        
        self.w_hybasid.items = self.all_item + new_items
    
    su.switch('loading', 'disabled', on_widgets=['w_hybasid'])
    def zoom_to_selected(self, change):
        """Highlight selection and zoom over it"""
        
        if not change['new']:
            return
        
        if change['new'][-1] == 'all':
            
            # deselect previous selected elements
            self.w_hybasid.v_model = ['all']
            bounds = self.model.get_bounds(
                self.model.get_upstream_fc()
            )
            self.map_.remove_layers_if('name', 'Selection')
            self.map_.zoom_bounds(bounds)
            
        else:
            self.w_hybasid.v_model = [id_ for id_ in self.w_hybasid.v_model if id_!='all']  
            # Get bounds and zoom to the object
            selected = self.model.get_selected(change['new'])        
            bounds = self.model.get_bounds(selected)

            self.map_.zoom_bounds(bounds)

            outline = ee.Image().byte().paint(
                featureCollection=selected, color=1, width=3
            )
            
            self.map_.addLayer(outline, param.selected_vis, 'Selection')