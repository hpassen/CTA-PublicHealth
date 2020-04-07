'''
Setting up Classes to hold data about CTA Metro Lines and Stops

Hana Passen, Charmaine Runes, Roberto Barroso

Health data retrieved from: https://www.cityhealthdashboard.com
'''

import numpy as np
import pandas as pd
import cta_data_wrangle as cta
import MetroLine_scraper as scraper
import acs_ph_combine as data
import geopandas as gpd 
import shapely

CENSUS_TRACTS = gpd.read_file('data/ChicagoShapefiles/Chi_census_tract.shp')
INDICATOR_DATA = data.build_acs_health_df()


class MetroLine(object):
    '''
    Object representing the attributes of a single metro line in the CTA system

    See constructor for parameters
    '''
    def __init__(self, name):
        """
        Constructor for the MetroLine Class

        Inputs: 
            - name: (str) the name of the metro line

        Attributes: 
            - name: string color of CTA
            - stops: (list) a list of all metro stops associated with the
                            line
            - line_shape
            - stops_shape
            - census_tracts
        """
        self.__line_name = name
        self._assign_stops()
        stop_info = pd.DataFrame(self._prep_stops_for_plot())

        self._generate_stops_shape_file(stop_info)
        self._generate_line(stop_info)
        self._get_line_census_tracts(CENSUS_TRACTS, INDICATOR_DATA)

    def get_name(self):
        '''
        Returns the private name of a MetroLine object
        '''
        return self.__line_name

    @property
    def stops(self):
        return self._stops


    def _assign_stops(self):
        '''
        Assigns MetroStop objects in order to a MetroLine object, based on data
        from a web scraper

        Inputs:
            - none: uses name attribute from MetroLine object

        Returns:
            - none: updates MetroLine in place
        '''
        self._stops = scraper.scrape_line_url(self.__line_name)
        line_name = self.__line_name.capitalize()

        cta_df = cta.import_clean_cta_data()
        line_filter = cta_df["descriptive_name"].str.contains(line_name)
        line_stops = cta_df[line_filter].sort_values(by = "map_id")

        seen_names = []
        for stop in self.stops:
            short_name = stop.get_name()[0]

            name_elem = short_name.split() 
            name_elem = [elem.strip("()") for elem in name_elem]

            for row in line_stops.itertuples():
                index, desc_name, lat, lon, map_id, name = row
                if all(x in desc_name for x in name_elem) and (
                    short_name in name.strip() or name.strip() in
                    short_name) and (short_name not in seen_names):
                        stop.assign_non_health_attrs(row)
                        seen_names.append(short_name)


    def _prep_stops_for_plot(self):
        '''
        Returns a dictionary where the keys are "name", "lat", "lon" and the
        values for each is list containing that attribute from each stop, in 
        order, on the line

        Inputs:
            - none

        Returns:
            - plot_prep: (dict) dictionary with the names, lats, lons of every 
                          stop in a metro line
        '''
        plot_prep = {"name": [], "lat": [], "lon": []}
        
        for stop in self._stops:
            plot_prep["name"].append(stop.get_name()[1])
            plot_prep["lat"].append(stop.get_location()[0])
            plot_prep["lon"].append(stop.get_location()[1])

        return plot_prep


    def _generate_stops_shape_file(self, stop_info):
        '''
        Generate ggeopandas data frame with all the MetroStops for this line.
        Name of stops, shapely geometry point. Assign it to shape attribute.

        Input:
        - stop_info: pandas data frame with the names, lats, lons of every 
                          stop in a metro line
        '''
        stop_info["geometry"] = stop_info.apply(lambda row: 
                                                shapely.geometry.Point(
                                                row.lon, row.lat), axis = 1)
        geo_shape = gpd.GeoDataFrame(stop_info)
        geo_shape.crs = CENSUS_TRACTS.crs
        self.stops_shape = geo_shape


    def _generate_line(self, stop_info):
        '''
        Create line_string object and convert it into a 
        geopandas dataframe. Assign it to line_shape attribute.

        Input:
        - stop_info: pandas data frame with the names, lats, lons of every 
                          stop in a metro line
        '''
        line_st = []
        for _, _, lat, lon, _ in stop_info.itertuples():
            line_st.append((lon, lat))
        line_st = shapely.geometry.LineString(line_st)
        line_shape = gpd.GeoDataFrame(geometry=[line_st])
        line_shape.crs = CENSUS_TRACTS.crs
        self.line_shape = line_shape


    def _get_line_census_tracts(self, CENSUS_TRACTS, INDICATOR_DATA):
        '''
        Finds census tracts in CENSUS_TRACTS shapefile that are underneath
        this cta line merge with dataframe containing 

        Inputs:
        - CENSUS_TRACTS: geopandas df with all Chicago census tracts from
          Chicago city data portal shapefile.

        Returns:
         - geopandas data with census tracts underneath this line.
        '''

        tracts = gpd.sjoin(CENSUS_TRACTS ,self.line_shape, op="intersects")
        tracts = tracts.loc[:, ["geoid10","geometry"]] 
        tracts.columns = ["geoid", "geometry"] 

        merged_df = pd.merge(left=tracts, right=INDICATOR_DATA,
                             left_on='geoid', right_on='geoid') 

        self.census_tracts = merged_df


    def find_healthiest_under_budget(self, budget):
        '''
        Returns the healthiest metro stops at or below a certain rental budget

        Inputs: 
            - dataframe: (pandas dataframe) a pandas dataframe with public health,
                      demographic, and budget information
            - budget: (int) a monthly rental budget amount

        Returns:
            - tracts: (list) geoids of the top 5 healthist census tracts below the
                   input monthly rental budget
        '''
        cheap = self.census_tracts[self.census_tracts["median_rent"] <= budget]
        cheap = cheap.sort_values("agg_health", ascending=True)

        cheapest_under_budget = cheap.iloc[:5, :]


    def __repr__(self):
        '''
        Represents the MetroLine object.
        '''
        line_obj = "<MetroLine Object, {} Line with {} stops>"
        line_obj = line_obj.format(self.__line_name.capitalize(), len(self._stops))

        return line_obj


    def __str__(self):
        '''
        String representation of a MetroLine's attributes.
        '''
        line_obj = "\n{} Line \n"
        line_obj = line_obj.format(self.__line_name.capitalize())
        line_obj += ("=============\n" +
                     "=============\n\n")

        for stop in self.stops:
            line_obj += stop.__str__() +"\n"

        line_obj += ("=============\n" +
                     "=============\n")

        return line_obj


class MetroStop(object):
    """
    Object representing the attributes of a single metro stop in the CTA system

    See constructor for parameters
    """
    def __init__(self, name, line):
        """
        Constructor for the MetroStop Class

        Inputs: 
            - name: (str) the name of the metro stop
            - row: (itertuple) a row from a pandas dataframe 

        Attributes: 
            - stop_name: (str) the name of the metro stop
            - data: (numpy array) an array storing all the public health 
                     indicators associated with the stop
            - lat: (float) latitude coordinate for the stop
            - lon: (float) longitude coordinate for the stop
            - lines: (list) list of strings of the metro lines on which the stop
                     lies
            - score: (float) an aggregate measure of health constructed from the
                      public health indicators
        """
        self.__short_name = name
        self.__desc_name = None
        self.__data = None
        self.__map_id = None
        self.__lat = None
        self.__lon = None
        self._lines = [line]
        self.__score = None
        self.__geoID = None


    def get_name(self):
        '''
        Returns the private short name and descriptive name for a metro stop
        '''
        return self.__short_name, self.__desc_name


    def get_location(self):
        '''
        Returns the string representation of a metro stop's location
        '''
        return self.__lat, self.__lon


    def assign_non_health_attrs(self, row):
        '''
        Assigns non-health indicators to a given metro stop

        Inputs: 
            - row: (itertuple) a row from a pandas dataframe 

        Returns:
            - none: updates the stop object in place
        '''
        _, desc_name, lat, lon, map_id, _ = row

        self.__desc_name = desc_name
        self.__map_id = map_id
        self.__lat = lat
        self.__lon = lon


    def __repr__(self):
        '''
        Represents the MetroStop object.
        '''
        stop_obj = "<MetroStop Object, {}>"
        stop_obj = stop_obj.format(self.__desc_name)

        return stop_obj


    def __str__(self):
        '''
        String representation of a MetroStop's attributes.
        '''
        if self.__desc_name:
            stop_obj = self.__desc_name
            stop_obj += "\n-------------\n"
        else:
            stop_obj = self.__short_name
            stop_obj += "\n-------------\n"

        if self.__lat and self.__lon:
            lat_lon = "({:8} N, {:8} W)\n"
            lat_lon = lat_lon.format(self.__lat, self.__lon)
        else:
            lat_lon = ""

        stop_obj += lat_lon + lines
        return stop_obj
