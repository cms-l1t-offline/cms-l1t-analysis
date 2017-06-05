from rootpy.plotting.utils import draw as r_draw
from rootpy.plotting.hist import Efficiency
from rootpy.context import preserve_current_style
import rootpy.ROOT as ROOT
from rootpy.ROOT import gStyle
from exceptions import RuntimeError


__known_root_pallettes = set([
  "DeepSea",          "GreyScale",    "DarkBodyRadiator",
  "BlueYellow",      "RainBow",      "InvertedDarkBodyRadiator",
  "Bird",             "Cubehelix",    "GreenRedViolet",
  "BlueRedYellow",    "Ocean",        "ColorPrintableOnGrey",
  "Alpine",           "Aquamarine",   "Army",
  "Atlantic",         "Aurora",       "Avocado",
  "Beach",            "BlackBody",    "BlueGreenYellow",
  "BrownCyan",        "CMYK",         "Candy",
  "Cherry",           "Coffee",       "DarkRainBow",
  "DarkTerrain",      "Fall",         "FruitPunch",
  "Fuchsia",          "GreyYellow",   "GreenBrownTerrain",
  "GreenPink",        "Island",       "Lake",
  "LightTemperature", "LightTerrain", "Mint",
  "Neon",             "Pastel",       "Pearl",
  "Pigeon",           "Plum",         "RedBlue",
  "Rose",             "Rust",         "SandyTerrain",
  "Sienna",           "Solar",       "SouthWest",
  "StarryNight",     "Sunset",      "TemperatureMap",
  "Thermometer",     "Valentine",   "VisibleSpectrum",
  "WaterMelon",      "Cool",        "Copper",
  "GistEarth",       "Viridis"
])


def root_palette(value, max, min=0):
    colour_index = float(value - min) / float(max - min) * gStyle.GetNumberOfColors()
    return gStyle.GetColorPalette(int(colour_index))


def __clean(hists):
    cleaned_hists = []
    for hist in hists:
        if isinstance(hist, Efficiency):
            hist = hist.graph
        cleaned_hists.append(hist)
    return cleaned_hists


def __apply_colour_map(hists, colourmap, colour_values, change_colour):
    # Clean change_colour
    change_colour = [ c.lower() for c in change_colour ]

    # Resolve the requested pallette if it's not a function
    if isinstance(colourmap, str):
        if colourmap in __known_root_pallettes:
            gStyle.SetPalette(getattr(ROOT, "k"+colourmap))
            colourmap=root_palette
        else:
            raise RuntimeError("Unknown palette requested: "+colourmap)

    # Set the colour of each hist
    max = len(hists)
    for value, hist in enumerate(hists):
        if colour_values:
            value, max = colour_values(value)
        colour = colourmap(value, max)
        if "line" in change_colour:
            hist.linecolor = colour
        if "marker" in change_colour:
            hist.markercolor = colour


def draw(hists, colourmap="RainBow", colour_values=None, change_colour = ("line","marker")):
    with preserve_current_style():
        hists = __clean(hists)
        __apply_colour_map(hists, colourmap, colour_values, change_colour)
        r_draw(hists)
