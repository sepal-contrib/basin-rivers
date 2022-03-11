from copy import deepcopy

from traitlets import link, directional_link
import ipyvuetify as v
import sepal_ui.sepalwidgets as sw

from component.message import cm
import component.widget as cw
import component.parameter as cp


from sepal_ui.frontend import js

__all__=["StatSettingCard"]

class StatSettingCard(cw.Card):
    """Statistics settings card. It includes all the required inputs to compute
    and display graphics in the statistics dashboard.
    """
    
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        # set the resizetrigger
        self.rt = js.rt
        
        
        self.model = model

        title = v.CardTitle(children=[cm.graphs.setting.title])

        self.w_variable = sw.Select(
            label=cm.graphs.setting.w_variable.label,
            v_model="all",
            items=[{"text": "All variables", "value": "all"}]
            + [
                {"text": eval(f"cm.gfc.{var}"), "value": var}
                for var in list(set(cp.gfc_translation.values()))
            ],
        )
        self.w_years = cw.DateSlider(v_model=self.model.sett_timespan).hide()
        self.w_hybasid = sw.Select(
            label=cm.basin.basinid.label,
            v_model=[],
            items=[],
            small_chips=True,
            multiple=True,
            chips=True,
            deletable_chips=True,
        )

        self.children = [
            title,
            self.w_variable,
            self.w_hybasid,
            self.w_years,
        ]

        # Links
        link((self.w_variable, "v_model"), (self.model, "selected_var"))
        link((self.w_hybasid, "v_model"), (self.model, "selected_hybasid_chart"))

        # UI Events
        self.w_variable.observe(self.show_years, "v_model")

        # model Events
        self.w_years.on_event("change", self.years_event)
        self.w_hybasid.observe(self.at_least_one, "v_model")

        # Fill w_hybasid items when the the zonal statistics area calculated
        self.model.observe(self.fill_items ,"ready")

    def at_least_one(self, change):
        """Deactivate the last item when there is only one selectled. Useful
        to avoid showing up graphs without info"""

        widget = change["owner"]
        new_val = change["new"]
        new_items = deepcopy(widget.items)

        if len(widget.v_model) == 1:

            idx = [
                item["index"] for item in widget.items if item["value"] == new_val[0]
            ][0]

            new_items[idx].update(disabled=True)
        elif len(widget.v_model) >= cp.MAX_CATCH_NUMBER:

            for item in widget.items:
                if item["value"] not in new_val:
                    new_items[item["index"]].update(disabled=True)
        else:

            [item.update(disabled=False) for item in new_items]
            
        widget.items = new_items

    def fill_items(self, _):
        """Fill w_hybasid items once model.ready is True with the inputs step and select the
        first five(5) elements (arbitrary)"""
        
        method = self.model.method
        if method == "all":
            inputs_selection = self.model.hybasin_list
        else:        
            inputs_selection = self.model.selected_hybas
        
        
        # Convert into string to graphic purposes        
        self.w_hybasid.items = [
            {"text": str(val), "value": str(val), "disabled": False, "index": idx}
            for idx, val in enumerate(inputs_selection)
        ]

        self.w_hybasid.v_model = [it["value"] for it in self.w_hybasid.items[:5]]
            

    def years_event(self, widget, event, data):
        """Workaround event (overriding observe) to avoid double calls in slider.
        it will bind selected years with model data.
        """

        self.model.sett_timespan = data

    def show_years(self, change):
        """Hide years selection widget when loss is selected"""
        
        self.rt.resize()

        if change["new"] == "loss":
            self.w_years.show()
        else:
            self.w_years.hide()

            
