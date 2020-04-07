'''
This file is used to load and clean Chicago census tracts public health
data.
''' 
import pandas as pd 

DATA_TYPES = {"state_fips":"str", "county_fips": "str",
              "tract_code": "str"}
PH_INDICATORS = ['Life expectancy', 'Diabetes', 'Housing with potential lead risk', 
                 'High blood pressure', 'Uninsured']
COL_NAMES = {'Life expectancy': 'life_expectancy', 'Diabetes': 'diabetes', 
             'Housing with potential lead risk': 'lead_risk', 
             'High blood pressure': 'high_bp', 'Uninsured': 'uninsured'}

def load_data(folder, file_name, data_types=DATA_TYPES):
    '''
    Function to load data into pandas dataframe.
    Input: 
    - folder: (string) folder where file is located.
    - file_name: (string) file name 
    - data_types: (dictionary) links column names to data type of interest
    Returns:
    - pandas data frame for loaded file
    '''
    df = pd.read_csv(folder+file_name, dtype=data_types ,index_col=0)

    return df


def clean_chicago_health_df(ph_indicators=PH_INDICATORS):
    '''
    Function to filter pandas data frame to only include 
    wanted ph_indicators. This function also creates a geoid column
    as a unique identifier, and filter out all unecessary columns.
    Input:
    - ph_indicators: list of strings for wanted public health indicators
    Return: 
    - pandas data frame
      '''
    dataframe = load_data("data/CityHealth/", "CHDB_data_tract_IL v8_1.csv")

    chicago_df = dataframe[dataframe.city_name=="Chicago"]
    ch_pub_health = chicago_df[(chicago_df.metric_name.isin(ph_indicators)) & 
                               (chicago_df.group_name == "total population")]

    ch_pub_health = ch_pub_health.loc[:,["state_fips", "county_fips",
                                         "tract_code","metric_name","est", 
                                         "data_yr_type"]].reset_index()

    ch_pub_health["geoid"] = (ch_pub_health["state_fips"] +  ch_pub_health["county_fips"]
                             +  ch_pub_health["tract_code"])
    ch_pub_health = ch_pub_health.rename(columns={"est":"estimate_value"})

    tract_health = pd.pivot_table(data=ch_pub_health, index="geoid",
                                  columns="metric_name").reset_index()
    tract_health.columns = tract_health.columns.to_series().str.join('_')
    tract_health.columns = tract_health.columns.str.lstrip("estimate_value").str.rstrip("_")
    tract_health.rename(columns=COL_NAMES, inplace=True)

    return tract_health
