from traitlets import CFloat, dlink
from ipyleaflet import LocalTileLayer

from sepal_ui.mapping import SepalMap
from ipyleaflet import Marker
import ipyvuetify as v


class MapTile(SepalMap):
    
    lat = CFloat(1.9854,allow_none=True).tag(sync=True)
    lon = CFloat(-76.0185,allow_none=True).tag(sync=True)
    
    def __init__(self, model, *args, **kwargs):
        
        self.model = model
        
        kwargs['basemaps']=["TERRAIN", "Google Satellite",]
        kwargs['world_copy_jump'] = True
        kwargs['gee']=False
        
        super().__init__(*args, **kwargs)
        
        self.zoom = 10
        self.center = [self.lat, self.lon]
            
        dlink((self, 'lat'),(self.model, 'lat'))
        dlink((self, 'lon'),(self.model, 'lon'))
        
        self.on_interaction(self.return_coordinates)
        
                
    def return_coordinates(self, **kwargs):
        
        if not self.model.disable_coords:
        
            lat, lon  = kwargs['coordinates']

            self.lat = round(lat, 4)
            self.lon = round(lon, 4)
                
        if kwargs.get('type') == 'click':
            
            self.model.disable_coords = not self.model.disable_coords
            
            # Remove markdown if there is one
            self.remove_layers_if('type', 'marker', _metadata=True)
            self.remove_layers_if('type', 'square', _metadata=True)
            
            if self.model.disable_coords:

                marker = Marker(
                    location=kwargs.get('coordinates'), 
                    draggable=False, 
                )

                marker.__setattr__('_metadata', {'type':'marker'})
                marker.__setattr__('name', 'Marker')

                self.add_layer(marker)
            
    def remove_layers_if(self, prop, equals_to, _metadata=False):
        """Remove layers with a given property and value
        Args:
            prop (str): Property or key (if using _metadata) of Layer
            equals_to (str): Value of property or key (if using _metadata) in Layer
            metadata (Bool): Whether the Layers have _metadata attribute or not
        """
        if _metadata:
            for layer in self.layers:
                if hasattr(layer, "_metadata"):
                    if layer._metadata[prop] == equals_to:
                        self.remove_layer(layer)
        else:
            for layer in self.layers:
                if hasattr(layer, prop):
                    if layer.__dict__["_trait_values"][prop] == equals_to:
                        self.remove_layer(layer)
    
    
    def remove_layers(self):
        """Remove all layers in map. Except the basemaps"""        
        
        keep_layers = ['Marker', 'Google Satellite', 'Google Terrain']
        
        _ = [
            self.remove_layer(layer) 
            for layer 
            in self.layers 
            if layer.name not in keep_layers
        ]
