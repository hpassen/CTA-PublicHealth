'''
This module collects City of Chicago public health indicators from the City
Health Portal API 

Roberto Barroso, Charmaine Runes, Hana Passen
'''
import numpy as np
import pandas as pd
import requests 
import json 


INDICATOR_YRS = [("diabetes", "2017,+1+Year+Modeled+Estimate"), 
                 ("high-blood-pressure", "2017,+1+Year+Modeled+Estimate"),
                 ("uninsured", "2017,+5+Year+Estimate"),
                 ("life-expectancy", "2010-2015,+6+Year+Modeled+Estimate"),
                 ("housing-with-potential-lead-risk", "2017,+5+Year+Estimate")]

COL_NAMES = {'life-expectancy': 'life_expectancy', 
             'housing-with-potential-lead-risk': 'lead_risk', 
             'high-blood-pressure': 'high_bp'}


def build_health_df():
    '''
    Builds a dataframe with all the health indicators by census tract

    Inputs:
        - none

    Returns:
        - health_df: (pandas dataframe) a dataframe with all health indicators
                      by geoid/census tract
    '''
    health_df = build_mini_frame(INDICATOR_YRS[0][0], INDICATOR_YRS[0][1])


    for metric in INDICATOR_YRS[1:]:
        indicator, data_yr_type = metric
        metric_mini_frame = build_mini_frame(indicator, data_yr_type)

        health_df = health_df.merge(metric_mini_frame, on="geoid")
        health_df.rename(columns=COL_NAMES, inplace=True)

    return health_df


def build_mini_frame(metric, data_yr_type): 
    '''
    Takes an api dictionary for a health indicator and produces a very small
    dataframe with a column for that indicator by census tract

    Inputs: 
        - metric: (str) a health metric we care about
        - data_yr_type: (str) the year the data was collected

    Returns: 
        - mini_df: (pandas dataframe) a dataframe with a geoid and health
                    indicator information 
    '''
    indicators_dict = get_api_data(metric, data_yr_type)

    dict_for_df = {"geoid": [], metric: []}

    for entry in indicators_dict["rows"]: 
        geoid = entry["stcotr_fips"]
        value = entry["est"]
        dict_for_df["geoid"].append(str(geoid))
        dict_for_df[metric].append(value)

    mini_df = pd.DataFrame(dict_for_df)

    return mini_df


def get_api_data(metric, data_yr_type):
    '''
    Build an API request and get data from the City Health Portal API

    Inputs: 
        - metric: (str) a health metric we care about
        - data_yr_type: (str) the year the data was collected

    Returns: 
        - indicators_dict: (dict) a dictionary where the keys are "metrics", 
                            with metadata for the information, "rows", which
                            represent the information from each tract, and 
                            "fields", which includes metadata for each column
    '''
    end_point = "api.cityhealthdashboard.com/api/data/tract-metric/"
    api_key = "4633880de801584e97b3650ac2eb1a53"
    location = "&city_name=Chicago&state_abbr=IL"


    request = "https://{}{}?token={}{}&data_yr_type={}"
    request = request.format(end_point, metric, api_key, location, data_yr_type)
    data_json = requests.get(request)
    indicators_dict = data_json.json()

    return indicators_dict






"/uninsured?token=4633880de801584e97b3650ac2eb1a53&city_name=Chicago&state_abbr=IL&data_yr_type=2017,+5+Year+Estimate"
"/life_expectancy?token=4633880de801584e97b3650ac2eb1a53&city_name=Chicago&state_abbr=IL&data_yr_type=2010-2015,+6+Year+Modeled+Estimate"
"/diabetes?token=4633880de801584e97b3650ac2eb1a53&city_name=Chicago&state_abbr=IL&data_yr_type=2017,+1+year+modeled+estimate"
"/housing-with-potential-lead-risk?token=4633880de801584e97b3650ac2eb1a53&city_name=Chicago&state_abbr=IL&data_yr_type=2017,+5+Year+Estimate"
"/high-blood-pressure?token=4633880de801584e97b3650ac2eb1a53&city_name=Chicago&state_abbr=IL&data_yr_type=2017,+1+Year+Modeled+Estimate"