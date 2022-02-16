import random
import ee
from ipyleaflet import Marker

import component.parameter as param

ee.Initialize()

def get_hydroshed(level):
    """Return a Feature collection based on the provided level"""
    
    if level not in range(1,12+1):
        raise Exception("Only levels 0 to 12 are valid")
        
    return ee.FeatureCollection(param.hybas_dataset.format(level))

def get_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


def color_basin(fc):
    """Return a ready image to display in map for a basin feature collection"""
    
    unique = fc.aggregate_array('HYBAS_ID').getInfo()
    
    color_fc = ee.Image().byte().paint(
      featureCollection=fc,
      color='HYBAS_ID',
    )
    min_ = min(unique)
    max_ = max(unique)

    vis_params = {
        'palette': [get_random_color() for _ in range(len(unique))],
        'min' : min_,
        'max' : max_
    }
    
    return color_fc, vis_params

def get_marker(coordinates):
    """Return a marker in the given coordinates"""

    marker = Marker(
        location=coordinates, 
        draggable=False, 
    )

    marker.__setattr__('_metadata', {'type':'marker'})
    marker.__setattr__('name', param.marker_name)

    return marker