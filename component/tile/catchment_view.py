import ee
ee.Initialize()

from traitlets import Bool, link
from ipywidgets import Output
import ipyvuetify as v

from sepal_ui import color as sc
import sepal_ui.sepalwidgets as sw
import sepal_ui.scripts.utils as su


import component.parameter as param
from component.message import cm

__all__ = ["BasinView", "Dashboard"]


class Dashboard(v.Card, sw.SepalWidget):
    
    def __init__(self, *args, **kwargs):

        self.class_ = "d-block pa-2 mt-4"

        super().__init__(*args, **kwargs)
        
        title = v.CardTitle(children=['Statistics'])
        # desc = v.CardText(children=['Statistics'])
        self.alert = sw.Alert()
        
        self.btn_csv = sw.Btn('Download .csv file', class_='mr-2 mb-2').hide()
        self.btn_pdf = sw.Btn('Download .pdf report', class_ = 'mb-2').hide()
        
        self.output = Output()
        
        self.children=[
            title,
            # desc,
            self.btn_csv,
            self.btn_pdf,
            self.output,
        ]



class BasinView(v.Card, sw.SepalWidget):
    """Card to capture all the user inputs
    
    Args:
        model (Model): Model to store the widgets
        map_ (SepalMap): Map to display the output layers
    """
    
    all_item = [{'text': "All catchments",'value':'all'}]


    def __init__(self, model, map_, dashboard, *args, **kwargs):

        self.class_ = "d-block pa-2 mt-4"

        super().__init__(*args, **kwargs)

        self.model = model
        self.map_ = map_
        
        title = v.CardTitle(children=['Statistics'])
        desc = v.CardText()
        
        self.alert = sw.Alert()
        
        self.dashboard = dashboard

        self.w_hybasid = v.Select(
            label=cm.basin.basinid.label,
            items=self.all_item,
            v_model=self.model.hybasin_id,
            multiple=True, 
            chips=True,
            filled=True,
        )
        
        self.btn = sw.Btn('Calculate statistics')
        
        self.children = [title, desc, self.w_hybasid, self.btn, self.alert]
        
        self.model.observe(self.fill_catchs, 'hybasin_list')
        self.w_hybasid.observe(self.zoom_to_selected, 'v_model')
        
        self.btn.on_event('click', self.calculate_statistics)
    
    @su.loading_button(debug=True)
    def calculate_statistics(self, widget, event, data):
        """Calculate zonal statistics based on the selected hybas_id"""
        
        hybas_id = self.w_hybasid.v_model
        
        zonal_statistics = self.model.calculate_statistics(hybas_id)
        
        df = self.model.get_dataframe(zonal_statistics)
        df = df.sort_values(by=['basin','variable'])
        self.df = df[df["variable"] < 30]
        
        self.dashboard.btn_pdf.show()
        self.dashboard.btn_csv.show()

        with self.dashboard.output:
            
            self.dashboard.output.clear_output()
            
            agg_tips = self.df.groupby(
                ['basin', 'variable']
            )['area'].sum().unstack().fillna(0).T

            
            import seaborn as sns
            
            sns.set_theme(style="darkgrid")
            sns.set(rc={'figure.figsize':(20,8.27)})

            
            import numpy as np
            from matplotlib import pyplot as plt

            fig, ax = plt.subplots()

            # Initialize the bottom at zero for the first set of bars.
            bottom = np.zeros(len(agg_tips))

            # Plot each layer of the bar, adding each bar to the "bottom" so
            # the next bar starts higher.
            for i, col in enumerate(agg_tips.columns):
                ax.bar([f'{i + 2000}' for i in self.df["variable"].unique()], agg_tips[col], bottom=bottom, label=col)
                bottom += np.array(agg_tips[col])

            ax.set_title('Deforested area')
            ax.legend()
            
            self.fig = fig
            display(fig)


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
                featureCollection=selected, color=1, width=2
            )
            
            self.map_.addLayer(outline, param.selected_vis, 'Selection')