Documentation for CAPP-30122 Project
Roberto Barroso, Hana Passen, Charmaine Runes

Python Version: 
    3.7.4

External libraries: Please run the following commands, in order: 
-python3.7 -m venv env
-source env/bin/activate
-sudo pip install --upgrade pip
-sudo apt-get install libgeos++-dev
-sudo apt-get install libproj-dev
-sudo apt install python3-rtree
-sudo pip3.7 install -r requirements.txt

To Run the Software: in terminal, run: 
- python3.7 text_ui.py
    NOTE: if it fails to run in the virtual environment, run in outside the 
    virtual environment in the VM

    NOTE: You may see this error message: 
    /usr/local/lib/python3.7/site-packages/geopandas/plotting.py:335: 
    UserWarning: The GeoSeries you are attempting to plot is empty. Nothing has 
    been displayed.
    If so, the plot has still been created - this is the automated warning for
    any NaN values, which we have coded gray in our plots. 


Python Libraries: see requirements.txt

Files: 
    - requirements.txt: a txt file containing the requirements for the virtual
                        environment
    - cta_classes.py: a module containing the methods for constructing MetroLine
                      and MetroStop classes, generating shapefiles for each 
                      MetroLine, and plotting the lines
    - cta_data_wrangle.py: a module containing the functions to request CTA stop
                           data through an API, and process that data
    - line_scraper.py: a module for webscraping CTA line data for the ordered
                       list of stops
    - health_wrangle.py: a module for collecting City of Chicago public health
                         indicator data from the City Health Portal API, and 
                         cleaning that data
    - census_data_wrangle.py: a module for loading and cleaning a CSV with the
                              demographic data for each census tract downloaded
                              from the Census Bureau website
    - acs_ph_combine.py: a module that merges the public health and demographic
                         dataframes, and uses indicators from each to calculate
                         an aggregated health score, and an adversity index for
                         each census tracts
    - make_figures.py: a module that plots the figures, based on the dataframes
                       and shapefiles from the CTA classes
    - context.py: a module that contains methods to construct and represent
                  MapContext objects, which store the information to
                  create a plot
    - text_ui.py: a module that runs a text-based user interface, allowing the
                  user to choose what MetroLines, public health indicator, and
                  socioeconomic/demographic indicator to use to construct and
                  plot a MapContext object

Directory:
    - data: a directory containing the ACS data downloaded from Census Bureau


API Key Information

Chicago City Health Dashboard API Key: 
- User Name: hpassen
- Key: 4633880de801584e97b3650ac2eb1a53


City of Chicago CTA Data API Key
- User Name: CAPP30122
- User ID: 7o4n0hg6q12fvnn1az6ly9ctu
- User Secret: 539rolgsr8qyun4dny6feie1q483rh7ttvymieeahjqcowvci4
    
- API Token: sJyI5hpZy8dZHJBbMhrhdBkyi
- API Secret: MLhl9HDGfVIimTxv-lXnTorwipMm499xhjTI
 
