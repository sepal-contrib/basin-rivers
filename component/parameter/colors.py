from matplotlib import colors
import numpy as np

from .app import year_range, gfc_labels, gfc_classes

__all__ = ["gfc_vis", "gfc_colors", "gfc_vis", "gfc_colors_dict"]


def color_fader(v=0):
    """return a rgb (0-255) tuple corresponding the v value in a 19
    spaces gradient between yellow and darkred"""

    c1 = "yellow"
    c2 = "darkred"

    n = len(year_range)
    mix = v / n

    c1 = np.array(colors.to_rgb(c1))
    c2 = np.array(colors.to_rgb(c2))

    return (1 - mix) * c1 + mix * c2


gfc_colors = [colors.to_hex(color_fader(year)) for year in year_range] + [
    colors.to_hex(strcolor)
    for strcolor in ["lightgrey", "darkgreen", "lightgreen", "purple", "darkred"]
]

gfc_colors_dict = dict(zip(gfc_labels, gfc_colors))
gfc_colors_dict.update({"loss":'darkred'})

gfc_vis = {
    "visualization_0_type": "categorical",
    "visualization_0_name": "CLASS",
    "visualization_0_bands": "constant",
    "visualization_0_palette": gfc_colors,
    "visualization_0_labels": gfc_labels,
    "visualization_0_values": gfc_classes,
}
