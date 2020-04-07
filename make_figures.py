'''
Plotting module. 

Written by: Hana Passen, Charmaine Runes and Roberto Barroso
'''

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import geopandas as gpd
import pandas as pd
from cta_classes import MetroLine

CENSUS_TRACTS = gpd.read_file('data/ChicagoShapefiles/Chi_census_tract.shp')
UNITS = {"diabetes": "Diabetes among adults aged ≥18 years (%)",
         "high_bp": "High blood pressure among adults aged ≥18 years (%)",
         "lead_risk": "Housing stock with potential elevated lead risk (%)",
         "life_expectancy": "Life expectancy at birth (yrs)",
         "uninsured": "Lack of health insurance, people aged 0-64 years (%)",
         "agg_health_norm": "Normalized aggregated health score",
         "poverty_pct": "Percent of people living in poverty (%)",
         "nhblack_pct": "Percent non-Hispanic Black or African American (%)",
         "nhwhite_pct": "Percent non-Hispanic white (%)",
         "hisp_pct": "Percent Hispanic or Latinx, any race (%)",
         "poc_pct": "Percent people of color (%)",
         "median_rent": "Median monthly housing cost ($USD)",
         "65over_pct": "Percent residents 65 years old and over (%)"}


def generate_df_to_plot(colors):
    '''
    Generate geopandas dataframes from MetroLine objects.

    Input:
    - colors: list of strings (colors of CTA lines wanted)
    Returns:
    - all_lines: dataframe with information of all cta lines
    - line_objs: list of MetroLine objects
    '''

    line_objs = []
    frames = []
    for cta_color in colors:
        line = MetroLine(cta_color)
        line_objs.append(line)
        frames.append(line.census_tracts)

    all_lines = pd.concat(frames)

    return all_lines, line_objs


def make_plot_axes(all_lines, line_objs, indicator, axes):
    '''
    Add plots to axes.

    Inputs:
    - all_lines: dataframe with information of all cta lines
    - line_objs: list of MetroLine objects
    - indicator: public-health or socio-economic/demographic indicator
    - axes: matplotlib axes for figure

    Returns:
    - title: string with title for main figure
    '''
    prev = CENSUS_TRACTS.boundary.plot(ax=axes, color="gray", 
                                           alpha=.8, linewidth=1)
    divider = make_axes_locatable(axes)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    if indicator in  ["life_expectancy", "agg_health_norm"]:
        #Reverse color map for life expectancy since all other
        #ph indicators have negative valence as values increase
        color_map = plt.cm.get_cmap('coolwarm')
        heat_color = color_map.reversed()
    else:
        heat_color = "coolwarm"

    prev = all_lines.plot(ax=prev, column=indicator, 
                          cmap=heat_color, legend=True, cax=cax, alpha=1,
                          legend_kwds={"label":UNITS[indicator]},
                          missing_kwds= {"color": "gray",
                                         "label": "Missing values"})
    title = "CTA lines shown: "
    for line_obj in line_objs:
        prev = line_obj.line_shape.plot(ax=prev, color=line_obj.get_name(),
                                        alpha=1, linewidth=1.2)
        prev = line_obj.stops_shape.plot(ax=prev, color="black", markersize=8)
        title += line_obj.get_name().upper() + ", "
    
    axes.axis('off')
    return title


def plot_indicator_line(colors, ph_indicator, se_indicator):
    '''
    Function to plot multiple lines on the same plot with one
    public health indicator.
    Inputs:
    - colors: list of strings for CTA lines wanted
    - ph_indicator: Public health indicator
    - se_indicator: socio economic/ demographics indicator

    Returns:
    - fig: matplotlib object
    '''

    plt.style.use('seaborn-talk')

    (all_lines, line_objs) = generate_df_to_plot(colors)
    if se_indicator:
        fig, (ax1, ax2) = plt.subplots(ncols=2, sharex=True, sharey=True)
        title = make_plot_axes(all_lines, line_objs, ph_indicator, ax1)
        make_plot_axes(all_lines, line_objs, se_indicator, ax2)
        fig.suptitle(title[:-2] , fontsize=30)

    else:
        fig, ax1 = plt.subplots(1, 1)
        make_plot_axes(all_lines, line_objs, ph_indicator, ax1)

    fig.set_size_inches(25, 10)
    return fig
