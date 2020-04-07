''' 
An application module that allows a user to create a plot of two side-by-side
maps of the city of Chicago: one map with a public health indicator that is of
interest, and another with a socioeconomic or demographic indicator that is of
interest. Both maps will highlight the census tracts underlying one or more 
elevated ('L') train lines. The application will save the plot to the user's
working directory.  

Hana Passen, Charmaine Runes, Roberto Barroso

'''

import sys
import argparse
import matplotlib.pyplot as plt
import make_figures as make

from context import MapContext
from make_figures import UNITS
from cta_classes import MetroLine


LINES = set(["red", "brown", "green", "orange", "purple", "pink", "blue", 
             "yellow"])

PUBLIC_HEALTH = ["diabetes", "high_bp", "lead_risk", "life_expectancy",
                 "uninsured", "agg_health_norm"]

SOCIOECONOMIC = ["poverty_pct", "nhblack_pct", "nhwhite_pct", "hisp_pct", 
                 "poc_pct", "median_rent", "65over_pct"]


MENU = '''
********* Taking the 'L' on Public Health *********
Welcome to the mapping public health by CTA 
application! This application maps public health
and socioeconomic indicators by Census tracts along
an L train line. You can use this application to
find, for example, the healthiest areas to live in
under a certain budget.

Please choose an option to start.

(1) Map indicators by L line
(2) Quit the program
'''

START = 1
END = 2


def print_options(valid_list):
    '''
    Prints all possible valid arguments

    Inputs:
        - valid_list (list): list of valid string_arguments

    Returns: None, but prints a dictionary of valid arguments and a brief
             description
    '''

    print("\n\nChoose ONE of the following indicators:\n{}\n".format(valid_list))
    print('\n'.join("   - {}: {}".format(k, v) for k, v in UNITS.items()
                                                   if k in valid_list))


def check_if_valid(user_input, valid_list):
    '''
    Checks to see if the user input is valid

    Inputs:
        - user_input (str): a string arguments
        - valid_list (list): list of valid string arguments

    Returns: True if the user input a valid argument, False otherwise
    '''

    if not user_input or user_input not in valid_list:
        print("\nSorry, {} is not a valid option.".format(user_input))
        print("Please try again using one of the above indicators")
        return False

    return True


def request_input_vars():
    '''
    Requests user input to create a MapContext object

    Inputs: None

    Returns: a tuple of (1) the list of lines, (2) the public health indicator,
             and (3) the socioeconomic indicator that the user is interested in
    '''

    line_list = None
    ph_indicator = None
    se_indicator = None

    print("\n---Public Health by MetroLine---")
    while True:
        line_input = input("\nREQUIRED - Enter one or more MetroLines: ")
        line_list = [line.lower().strip() for line in line_input.split(",")]

        invalid = False
        for val in line_list:
            if val not in LINES:
                invalid = True
                break

        if invalid:
            print("\nPlease make sure you choose only from the following:")
            print("\n".join("    - {}".format(name for name in LINES)))
        else:
            break

    print_options(PUBLIC_HEALTH)
    while True:
        ph_indicator = input("\nREQUIRED - Enter a public health indicator: ")
        if not check_if_valid(ph_indicator, PUBLIC_HEALTH):
            continue
        else:
            break

    print_options(SOCIOECONOMIC)  
    while True:       
        se_indicator = input("\nREQUIRED - Enter a socioeconomic indicator: ")
        if not check_if_valid(se_indicator, SOCIOECONOMIC):
            continue
        else:
            break

    if line_list and ph_indicator and se_indicator:
        return (line_list, ph_indicator, se_indicator)


def retrieve_task():
    '''
    Requests user input on whether to they want to use the application or quit
    the program. If the user provides an invalid option, raises an error.
    '''

    option = -1
    while True:
        print(MENU)
        option = int(input("Option: "))
        if option >= START and option <= END:
            break
        else:
            print("Invalid option {}".format(option))
    return option


def main():
    '''
    Pulls it all together: runs the UI, requests user input, builds a
    MapContext object, creates a plot, and saves it in the users directory.
    '''

    while True:
        option = retrieve_task()
        if option == 2:
            print("Quitting the program. Thanks for visiting our application!")
            break

        else:
            lines, ph_var, se_var = request_input_vars()
            cxt = MapContext(lines, ph_var, se_var)
            plot = make.plot_indicator_line(cxt.colors, cxt.ph_var, cxt.se_var)
            if plot:
                plt.savefig("CTA_FIGURE")
                plt.close(plot)
                print("\nA figure (CTA_FIGURE) has been saved in your folder.")
                print("Thanks for using our application!\n")
            else:
                print("ERROR: No information for {} or {} \
                    for {} train(s)".format(cxt.ph_var, cxt.se_var, cxt.colors))


if __name__ == "__main__":
    # This is the entry point into the application
    main()
