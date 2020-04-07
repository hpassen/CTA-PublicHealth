"""
Importing and filtering CTA metro stop data for use in our software

Hana Passen, Charmaine Runes, Roberto Barroso

"""
import numpy as np
import pandas as pd
import requests 
import json 


END_POINT = "https://data.cityofchicago.org/resource/8pix-ypme.json"
API_KEY = "sJyI5hpZy8dZHJBbMhrhdBkyi"
COLUMNS = ["map_id", "station_descriptive_name", "location"]


def import_clean_cta_data():
    '''
    Returns a dataframe with the name, location, and map_id for all CTA stops

    Inputs: 
        - none (all default values in the cta module)

    Returns:
        - cta_df: (pandas dataframe) dataframe with lat, lon, map_id,
                   descriptive name, name, lines

    '''
    api_request = build_api_request()
    stops_list = get_data(api_request)

    cta_df = process_data(stops_list)

    return cta_df


def build_api_request(endpoint=END_POINT, api=API_KEY, cols=COLUMNS):
    '''
    Returns the string needed to make the json request from the city data API

    Inputs: 
        - end_point: (str) a string representing the html endpoint of data
        - api: (str) a string representing the API authentication key
        - cols: (lst) a list of the columns to select from data set

    Returns: 
        - api_request: (str) a string properly formatted to request data
    '''
    api_request = END_POINT + "?"
    api_request += "$$app_token={}".format(API_KEY)
    api_request += "&$select={}".format(",".join(COLUMNS))

    return api_request


def get_data(api_request):
    '''
    Returns a list of dictionaries, in which the keys are the columns we
    indicated in our request and the values are the entries for those columns

    Inputs:
        - api_request: (str) a string representing the request for data

    Returns: 
        - stops_list: (lst) a list of dictionaries, in form {column: entries...}
                       for each column of data requested
    '''

    data_json = requests.get(api_request)
    stops_list = data_json.json()

    return stops_list


def process_data(stops_list):
    '''
    Returns a pandas dataframe with cleaned and processed data from the api data
    request

    Inputs:
        - stops_list: (lst) a list of dictionaries, in form {column: entries...}
                       for each column of data requested

    Returns:
        - stops_df: (pandas dataframe) a processed pandas dataframe
    '''
    processed_stops = {COLUMNS[0]: [], "descriptive_name": [], "latitude": [], 
                       "longitude": []}
    for entry in stops_list:
        location = entry[COLUMNS[2]]
        lat = float(location["latitude"])
        lon = float(location["longitude"])
        processed_stops[COLUMNS[0]].append(entry[COLUMNS[0]])
        processed_stops["descriptive_name"].append(entry[COLUMNS[1]])
        processed_stops["latitude"].append(lat)
        processed_stops["longitude"].append(lon)

    stops_df = pd.DataFrame(processed_stops)
    stops_df.drop_duplicates(("latitude", "longitude"), inplace=True)
    stops_df.index = range(len(stops_df))

    stops_df["name"] = stops_df["descriptive_name"].str.extract(r"([^()]+)")
    stops_df["name"] = stops_df["name"].str.strip()

    #Handling corner case where name from scraper and API differ there are two
    #situations in which this happens
    blvd = stops_df["name"] == "South Boulevard"
    stops_df.loc[blvd, "name"] = "South Blvd"
    stops_df.loc[blvd, "descriptive_name"] = "South Blvd (Purple Line)"

    conservatory = stops_df["name"] == "Conservatory"
    stops_df.loc[conservatory, "name"] = "Conservatory-Central Park Drive"
    stops_df.loc[conservatory,
                 "descriptive_name"] = "Conservatory-Central Park Drive (Green Line)"

    stops_df_in_order = stops_df.reindex(sorted(stops_df.columns), axis=1)

    return stops_df_in_order

    