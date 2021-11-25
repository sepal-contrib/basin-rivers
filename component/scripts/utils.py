import random
import ee
ee.Initialize()

def get_hydroshed(level):
    """Return a Feature collection based on the provided level"""
    
    if level not in range(1,12):
        raise Exception("Only levels 0 to 12 are valid")
        
    return ee.FeatureCollection(f"WWF/HydroSHEDS/v1/Basins/hybas_{level}")

def get_random_color():
    return "#{:06x}".format(random.randdint(0, 0xFFFFFF))


def get_nested_basins(fc, hybas_id):
    """
    Get all the basins whose has the hybas_id as NEXT_DOWN
    
    Args:
        fc (FeatureCollection): basin collection at given level
        hybas_id (str): target hydro basin id
    
    """
    
    return fc.filter(ee.Filter.eq('NEXT_DOWN', hybas_id))

def get_display_basin(fc):
    """Return a ready image to display in map for a basin feature collection"""
    
    unique = fc.aggregate_array('HYBAS_ID').getInfo()
    
    hydroshed = ee.Image().byte().paint(
      featureCollection=fc,
      color='HYBAS_ID',
    )
    min_ = min(unique)
    max_ = max(unique)

    vis_params = {
        'palette': [cu.get_random_color() for _ in range(len(unique))],
        'min' : min_,
        'max' : max_
    }
    
    return hydroshed, vis_params

def get_gfc(aoi, iniy, stopy, thres):
    """Creates a forest change map based on gfw dataset"""
    
    treecov = gfc.select(['treecover2000'])
    
    return (
        ee.Image(0)
          .where(treecov.lte(thres).And(gain.eq(1)), 50) # gain V
          .where(treecov.lte(thres).And(gain.eq(0)), 30) # non-forest
          .where(treecov.gt(thres).And(lossy.lt(iniy)), 30) # non-forest (lost forest before start date)
          .where(treecov.gt(thres).And(lossy.gt(stopy)), 40) # stable forest (forest lost after the dates)
          .where(treecov.gt(thres).And(gain.eq(1)).And(lossy.gte(iniy)).And(lossy.lte(stopy)), 51) #gain+loss
          .where(treecov.gt(thres).And(gain.eq(1)).And(lossy.eq(0)), 50) # gain
          .where(treecov.gt(thres).And(gain.eq(0)).And(lossy.gte(iniy)).And(lossy.lte(stopy)), lossy.add(2000)) # loss
          .where(treecov.gt(thres).And(gain.eq(0)).And(lossy.eq(0)), 40) # stable forest
          .selfMask()
    )

