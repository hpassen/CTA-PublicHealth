'''
CTA Health Project: Which are the Healthiest Metro Stops in Chicago?

Roberto Barroso, Hana Passen, Charmaine Runes

Skeleton Code tying the project together: 
    - Import and clean data
    - Scrape web and construct objects
    - Link objects and data
    - Create Visualizations

'''
import numpy as np
import pandas as pd
import census_data_wrangle as acs
import health_wrangle as ph


HEALTH_AGGREGATORS = ["diabetes", "high_bp", "lead_risk", "poverty_pct",
                      "uninsured"]


def build_acs_health_df():
    '''
    Merges the acs and health dataframes on the census tract unique identifier

    Inputs: 
        none: all inputs are defaults in health_wrangle and census_data_wrangle
              modules

    Return:
        - tracts: (pandas dataframe) a dataframe with all heath and demographic
                   indicators by unique census tract identifier
    '''
    health_df = ph.build_health_df()
    acs_df = acs.compile_acs_files()

    acs_ph = acs_df.merge(health_df, on="geoid", indicator=True)

    calculate_adversity_index(acs_ph)

    return acs_ph


def calculate_adversity_index(df):
    '''
    Calculates the aggregated health score for each census tract by taking the
    mean of all indicators available as percentages in a tract, then weighting 
    that average more heavily if the life expectancy in the tract is below the 
    average life expectancy in Chicago

    Inputs:
        - dataframe: (pandas dataframe) dataframe of health indicators

    Returns: 
        nothing: updates dataframe in place
    '''
    avg_life_expect = df["life_expectancy"].mean()
    df["agg_health"] = df[HEALTH_AGGREGATORS].mean(axis=1)
    early_death = df["life_expectancy"] < avg_life_expect

    #Weight agg_health by whether life expectancy is above or below the mean
    df.loc[early_death, "agg_health"] = df.loc[early_death, "agg_health"] * 1.1

    #create "adversity index" based on health score percentages
    adv_no_norm_labels = ["very low", "low", "average", "high", "very high"]
    adv_bins_no_norm = np.linspace(df["agg_health"].min(), 
                                   df["agg_health"].max(), num=6)
    df["adv_no_norm"] = pd.cut(df["agg_health"], bins=adv_bins_no_norm,
                               labels=adv_no_norm_labels,
                               include_lowest=True, right=True)

    #normalize the data to mean zero and set up the "adversity index"
    mean_agg = df["agg_health"].mean()
    std_agg = df["agg_health"].std()
    #multiply by negative 1 so the lower values are worse
    df["agg_health_norm"] = -1 * ((df["agg_health"] - mean_agg) / std_agg)

    adv_norm_labels = ["very high", "high", "average", "low", "very low"]
    adv_bins_norm = np.linspace(df["agg_health_norm"].min(), 
                                df["agg_health_norm"].max(), num=6)

    df["adv_norm"] = pd.cut(df["agg_health_norm"], bins=adv_bins_norm,
                               labels=adv_norm_labels,
                               include_lowest=True, right=True)
