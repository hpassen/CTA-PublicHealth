'''
This module is to scrape Chicago metro line web-pages and extract
ordered metro stops associated with each line.
Written by: Hana Passen, Charmaine Runes and Roberto Barroso
as part of their final project for CAPP30122, winter 2020
'''

import bs4
import requests as rq
import cta_classes as metro

color_lines = ["red", "blue", "brown", "green", "orange", "pink", 
               "purple", "yellow"]

def scrape_line_url(line):
    '''
    This function scraps the webpage for a specific L-line, to extract ordered
    metro stops and create MetroStop objects as it iterates through stops.

    Input:
    - line: (string) specific line to scrape i.e. red,blue,green,etc
    Returns:
    - stop_list: (list) list of MetroStop objects.
                 please see constructor in cta_classes 
                 for MetroStop object details.
    '''
    assert line.lower() in color_lines, "This line does not currently exist in the CTA"
    
    url = "https://www.transitchicago.com/" + line.lower() + "line/"
    req_obj = rq.get(url)
    soup = bs4.BeautifulSoup(req_obj.text, "html.parser")

    stopnames = soup.find_all('p', class_="rld-stopname")

    stops_list = []
    for stops in stopnames:
        stops_list.append(metro.MetroStop(stops.text, line.capitalize()))
    return stops_list

