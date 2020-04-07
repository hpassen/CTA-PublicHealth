'''
This a module contains a class that manages the inputs to our application. 

Hana Passen, Charmaine Runes, Roberto Barroso

'''

from make_figures import UNITS


class MapContext:
    '''
    A MapContext manages the loading and querying of MetroLines.
    '''

    def __init__(self, line_list, ph_indicator, se_indicator):
        '''
        Initializes the map context
        '''
        self.colors = line_list
        self.ph_var = ph_indicator
        self.se_var = se_indicator


    def __str__(self):
        '''
        String representation of a MapContext object
        '''
        lines = ", ".join(self.colors[:-1]) + " and " + self.colors[-1]
        cxt_str = ("Mapping Census tracts near the " + lines + " line(s), by " + 
                   UNITS[self.ph_var] + " and " + UNITS[self.se_var])

        return cxt_str
        