'''
Wrangling ACS data to extract poverty and race

Charmaine Runes, Hana Passen, Roberto Barroso Luque

'''

import pandas as pd


RACE_ETHN_VARS = ["HD01_VD01", "HD01_VD03", "HD01_VD04", "HD01_VD05",
                  "HD01_VD06", "HD01_VD07", "HD01_VD08", "HD01_VD10",
                  "HD01_VD12"]

POVERTY_VARS = ["HC01_EST_VC01", "HC02_EST_VC01"]

RENT_VARS = ["HD01_VD01"]

SEX_VARS = ["HD01_VD01", "HD01_VD02", "HD01_VD26"]

AGE_VARS = ["HD01_VD01", "HD01_VD03", "HD01_VD04", "HD01_VD05", "HD01_VD06",
            "HD01_VD07", "HD01_VD08", "HD01_VD09", "HD01_VD10", "HD01_VD11",
            "HD01_VD12", "HD01_VD13", "HD01_VD14", "HD01_VD15", "HD01_VD16",
            "HD01_VD17", "HD01_VD18", "HD01_VD19", "HD01_VD20", "HD01_VD21",
            "HD01_VD22", "HD01_VD23", "HD01_VD24", "HD01_VD25", "HD01_VD27",
            "HD01_VD28", "HD01_VD29", "HD01_VD30", "HD01_VD31", "HD01_VD32",
            "HD01_VD33", "HD01_VD34", "HD01_VD35", "HD01_VD36", "HD01_VD37",
            "HD01_VD38", "HD01_VD39", "HD01_VD40", "HD01_VD41", "HD01_VD42",
            "HD01_VD43", "HD01_VD44", "HD01_VD45", "HD01_VD46", "HD01_VD47",
            "HD01_VD48", "HD01_VD49"]

race_ethn_csv = "data/acs/race-ethn/ACS_17_5YR_B03002_with_ann.csv"
poverty_csv = "data/acs/poverty/ACS_17_5YR_S1701_with_ann.csv"
rent_csv = "data/acs/rent/ACS_17_5YR_B25064_with_ann.csv"
age_sex_csv = "data/acs/age_sex/ACS_17_5YR_B01001_with_ann.csv"

CENSUS_DICT = {"age": (age_sex_csv, AGE_VARS),
               "poverty": (poverty_csv, POVERTY_VARS),
               "race": (race_ethn_csv, RACE_ETHN_VARS),
               "rent": (rent_csv, RENT_VARS),
               "sex": (age_sex_csv, SEX_VARS)}


def extract_cols(csv, list_col):
    '''
    Wrangles CSV to return a pandas DataFrame with the specified column names

    Inputs:
    - filename (string): name of CSV
    - list_col (list): column names

    Returns: a pandas DataFrame with just the columns of interest
    '''

    relevant_cols = ["GEO.id2"]
    relevant_cols.extend(list_col)
    df = pd.read_csv(csv, usecols=relevant_cols, skiprows=[1, 2])

    return df


def aggregate_by_sex(df, list_col):
    '''
    Combines columns based on sex - assumes that the first column is a total
    e.g., total_pop, and that there are only two sex categories, with the male
    values listed first.

    Inputs:
    - df (pandas DataFrame)
    - list_col (list of strings): column headers

    Returns: an new DataFrame with combined columns 
    '''

    split_index = int((len(list_col) - 1) / 2)
    male = list_col[1:split_index + 1]
    female = list_col[split_index + 1:]

    for i in range(split_index):
        temp_col_name = "aggregate" + str(i)
        df[temp_col_name] = df[male[i]] + df[female[i]]

    keep_cols = ["GEO.id2", "HD01_VD01"]
    pct_cols = [col for col in df.columns if col[:9] == "aggregate"]
    keep_cols.extend(pct_cols)

    df_agg = df[keep_cols]

    return df_agg


def rename_cols(df, topic):
    '''
    Renames columns in a pandas DataFrame to be more descriptive, and creates a
    new variable "tract_code" to use as a unique ID when linking public health
    records

    Inputs:
    - df: a pandas DataFrame
    - names (str): a string describing the dataframe

    Returns: None (updates the DataFrame in place)
    '''

    col_names = ["geoid"]

    if topic == "race":
        col_names.extend(["total_pop", "nhwhite_pop", "nhblack_pop",
                          "nhaian_pop", "nhasian_pop", "nhpi_pop",
                          "nhother_pop", "nhmultiracial_pop", "hisp_pop"])

    elif topic == "poverty":
        col_names.extend(["total_pop", "poverty_pop"])

    elif topic == "rent":
        col_names.extend(["median_rent"])

    elif topic == "sex":
        col_names.extend(["total_pop", "male_pop", "female_pop"])

    elif topic == "age":
        col_names.extend(["total_pop", "under5_pop", "5-9_pop", "10-14_pop",
                          "15-17_pop", "18-19_pop", "20_pop", "21_pop",
                          "22-24_pop", "25-29_pop", "30-34_pop", "35-39_pop",
                          "40-44_pop", "45-49_pop", "50-54_pop", "55-59_pop",
                          "60-61_pop", "62-64_pop", "65-66_pop", "67-69_pop",
                          "70-74_pop", "75-79_pop", "80-84_pop", "85+_pop"])

    df.columns = col_names
    df["geoid"] = df["geoid"].apply(lambda x: str(x))
    df["tract_code"] = df["geoid"].str.slice(start=5)


def compute_percentages(df):
    '''
    Given a pandas DataFrame with total counts (i.e., pop), creates variables
    with corresponding percentages and then drops columns with estimates. 

    Inputs:
    - df: a pandas DataFrame

    Returns: a new pandas DataFrame with just tract_code and columns with
             percentages
    '''
    
    col_names = [col for col in df.columns \
                   if col not in ["total_pop", "geoid", "tract_code"]]

    for col in col_names:
        col_prefix = col[:-3]
        col_pct = col_prefix + "pct"
        df[col_pct] = (df[col] / df["total_pop"]) * 100

    keep_cols = ["tract_code"]
    pct_cols = [col for col in df.columns if col[-3:] == "pct"]
    keep_cols.extend(pct_cols)

    df_pct = df[keep_cols]

    return df_pct


def create_topic_df(filename, cols, topic, aggregate=False, compute_pct=True):
    '''
    Puts it all together: takes a CSV file and returns a clean pandas DataFrame

    Inputs:
    - filename (str): file path to CSV
    - topic (str): description of topic e.g., "race", "sex"
    - compute_pct (bool): whether or not the columns need to be converted to
                          percentages

    Returns: a topic-specific pandas DataFrame
    '''

    topic_df = extract_cols(filename, cols)
    if aggregate:
        topic_df = aggregate_by_sex(topic_df, cols)

    rename_cols(topic_df, topic)

    if compute_pct:
        topic_df = compute_percentages(topic_df)

    return topic_df


def compile_acs_files():
    '''
    Merges dataframes and returns the full ACS data set.

    Returns: a final pandas DataFrame with relevant data by census tract
    '''

    list_df = []

    for topic, values in CENSUS_DICT.items():
        csv_name, constants = values

        if topic == "age":
            df = create_topic_df(csv_name, constants, topic,
                                       aggregate=True, compute_pct=True)
        
        elif topic == "rent":
            df = create_topic_df(csv_name, constants, topic,
                                       aggregate=False, compute_pct=False)

            # Clean the rent string and convert to integer
            df["median_rent"] = df["median_rent"].replace("-", None)
            df["median_rent"] = df["median_rent"].str.replace(",", "")
            df["median_rent"] = df["median_rent"].str.strip("+")

            df["median_rent"] = pd.to_numeric(df["median_rent"])
        
        else:
            df = create_topic_df(csv_name, constants, topic,
                                       aggregate=False, compute_pct=True)
        
        list_df.append(df)

    left_most = list_df[0]
    for i in range(len(list_df) - 1):
        next_df = list_df[i + 1]
        merged = left_most.merge(next_df, on='tract_code')
        left_most = merged

    # Create and/or keep appropriate columns
    merged["65over_pct"] = merged["65-66_pct"] + merged["67-69_pct"] + \
                          merged["70-74_pct"] + merged["75-79_pct"] + \
                          merged["80-84_pct"] + merged["85+_pct"]

    merged["poc_pct"] = 100 - merged["nhwhite_pct"]

    overall_keep = ["geoid", "nhwhite_pct", "nhblack_pct", "hisp_pct",
                    "nhasian_pct", "poc_pct", "under5_pct", "65over_pct",
                    "median_rent", "poverty_pct"]

    merged = merged[overall_keep]

    return merged
