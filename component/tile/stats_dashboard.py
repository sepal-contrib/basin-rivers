from copy import deepcopy
from traitlets import link, directional_link

import ipyvuetify as v

import sepal_ui.sepalwidgets as sw

import component.widget as cw
import component.parameter as cp
from component.message import cm


__all__ = ["StatSettingCard", "StatDashboard"]

class StatDashboard(sw.Layout):
    
    def __init__(self, model, *args, **kwargs):
        
        self.model = model
        
        self.class_ = "pa-4 d-block"
        
        super().__init__(*args, **kwargs)
        
        # First row
        self.stat_setting_card = ct.StatSettingCard(model=self.model)
        self.overall_pie_card = OverallPieCard(self.model)
        
        # Second row
        self.detail_stat_layout = DetailedStat(self.model)
        
        overall_row = v.Layout(
            class_="d-flex mb-4",
            children=[
                v.Flex(
                    class_='mr-2',
                    xs5=True,
                    children=[
                        self.stat_setting_card
                    ]
                ),
                v.Flex(
                    xs7=True,
                    children=[
                        self.overall_pie_card
                    ]
                )
            ]
        )
        
        self.children=[overall_row, self.detail_stat_layout]
        

class StatSettingCard(cw.Card):
    
    
    
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.class_ = "pa-4"
        self.model = model
        self.first_time = True

        title = v.CardTitle(children=[cm.statistics.title])

        self.w_variable = sw.Select(
            label=cm.statistics.w_variable.label,
            v_model="all",
            items=[{"text": "All variables", "value": "all"}]
            + [
                {"text": eval(f"cm.gfc.{var}"), "value": var}
                for var in list(set(cp.gfc_translation.values()))
            ],
        )
        self.w_years = cw.DateSlider().hide()        
        self.w_hybasid = sw.Select(
            label=cm.basin.basinid.label,
            v_model=[],
            items=[],
            small_chips=True,
            multiple=True,
            chips=True,
            deletable_chips=True
        )

        self.children = [
            title,
            self.w_variable,
            self.w_hybasid,
            self.w_years,
        ]

        # Links
        link((self.w_variable, "v_model"), (self.model, "selected_var"))        
        link((self.w_hybasid, 'v_model'), (self.model, 'selected_hybasid_chart'))
        
        # UI Events
        self.w_variable.observe(self.show_years, "v_model")
        
        # model Events
        self.w_years.on_event("change", self.years_event)
        self.w_hybasid.observe(self.at_least_one, "v_model")
        
        self.w_hybasid.observe(self.fill_items, "items")
        
        directional_link((self.model, "hybasin_list"), (self.w_hybasid, "items"))
    
    def at_least_one(self, change):
        """Deactivate the last item when there is only one selectled. Useful
        to avoid showing up graphs without info"""
        
        widget = change["owner"]
        new_val = change["new"]
        new_items = deepcopy(widget.items)


        if len(widget.v_model) == 1:

            idx = [
                item["index"] for item in widget.items if item["value"]==new_val[0]
            ][0]
            
            new_items[idx].update(disabled=True)
            
        elif len(widget.v_model) == cp.MAX_CATCH_NUMBER:
            
            _=[
                new_items[item["index"]].update(disabled=True) 
                for item
                in widget.items if item["value"] not in new_val
            ]
            

        else:
            [item.update(disabled=False) for item in new_items]

        widget.items = new_items
    
    def fill_items(self, _):
        """Fill w_hybasid items once are retreived in the inputs step and select the 
        first five(5) elements (arbitrary)"""
        
        if self.first_time:
            self.w_hybasid.items = [
                {
                    "text": val, 
                    "value": val, 
                    "disabled": False, 
                    "index":idx
                } for idx, val in enumerate(self.model.hybasin_list)
            ]

            self.w_hybasid.v_model = [it["value"] for it in self.w_hybasid.items[:5]]
            
        self.first_time=False
            
    def years_event(self, widget, event, data):
        """Workaround event (overriding observe) to avoid double calls in slider.
        it will bind selected years with model data.
        """
        
        self.model.sett_timespan = data
        

    def show_years(self, change):
        """Hide years selection widget when loss is selected"""

        if change["new"] == "loss":
            self.w_years.show()
        else:
            self.w_years.hide()
