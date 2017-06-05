################################################################################
#        ______                    ______                            __        #
#       /  _/ /____  ____ ___     / ____/___  ____  ________  ____  / /_       #
#       / // __/ _ \/ __ `__ \   / /   / __ \/ __ \/ ___/ _ \/ __ \/ __/       #
#     _/ // /_/  __/ / / / / /  / /___/ /_/ / / / / /__/  __/ /_/ / /_         #
#    /___/\__/\___/_/ /_/ /_/   \____/\____/_/ /_/\___/\___/ .___/\__/         #
#                                                         /_/                  #
#            ______          __             __    ___                          #
#           / ____/___ ___  / /_  ___  ____/ /___/ (_)___  ____ _              #
#          / __/ / __ `__ \/ __ \/ _ \/ __  / __  / / __ \/ __ `/              #
#         / /___/ / / / / / /_/ /  __/ /_/ / /_/ / / / / / /_/ /               #
#        /_____/_/ /_/ /_/_.___/\___/\__,_/\__,_/_/_/ /_/\__, /                #
#                                                       /____/ credit: patorjk #
################################################################################

# Proj: Item Concept Embedding (ICE)
# File: utility.py
# Seri: 1/6
# Date: 06/02/2017
# Cont:
#	Func:
#       1) print_dict_entries               2) save_json_obj
#       3) load_json_obj                    4) plot_pdf_legend
#       4) plot_pdf_figure

import json

import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def print_dict_entries(dictionary, num=3):
    """ Prints specified amount of entries instead of the full dictionary.
    Param:
        param1 [dict] to be printed.
        param2 [int] amount of entries to print. Default=3.
    """
    keys = list(dictionary.keys())[:num]

    for idx, key in enumerate(keys):
        print(str(idx+1) + ':\t' + key)
        print(dictionary[key])
        print()


def save_json_obj(json_obj, path):
    """ Save a JSON object as a JSON file.
    Param:
        param1 JSON format object.
        param3 [string] path to save the JSON object
    """
    with open(path, 'w') as f:
        json.dump(json_obj, f, indent=4, sort_keys=True) # pprint JSON

def load_json_obj(path):
    """ Load a JSON object from a JSON file.
    Param:
        param1 [string] path to load the JSON file.
    Return:
        return1 JSON object.
    """
    with open(path) as f:
        return json.load(f)


def plot_pdf_legend(path, label_list, style_list, t1f=True):
    """ Plot .pdf legend by itself without figure for easier processing.
    Param:
        param1 [string] path to save the pdf legend.
        param2 [list] of string line labels.
        param3 [list] of string line style specifications.
        param4 [bool] whether to use Type 1 or Type 3 font. Default=True.
    Note:
        1) Plot with Type 1 font to accomodate all platforms by default.
    """
    # Switch from default Type 3 to Type 1 font.
    if t1f:
        matplotlib.rcParams['ps.useafm'] = True
        matplotlib.rcParams['pdf.use14corefonts'] = True
        matplotlib.rcParams['text.usetex'] = True

    fig = plt.figure(path)
    plt.axis('off') # remove ticks

    ax = fig.add_subplot(111)
    for label, style in zip(label_list, style_list):
        ax.plot(0, 0, style, label=label) # dummy plot

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width*0.5, box.height*0.5])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()

def plot_pdf_figure(path, title, xl, yl, xt_list, yl_list, style_list, t1f=True):
    """ Plot .pdf figure by itself without legend for easier processing.
    Param:
        param1 [string] path to save the pdf figure.
        param2 [string] figure title.
        param3 [string] x-axis label.
        param4 [string] y-axis label.
        param5 [list] of string x-axis ticks.
        param6 [list] of lists of y-coordinates for each line.
        param7 [list] of string line style specifications.
        param8 [bool] whether to use Type 1 or Type 3 font. Default=True.
    Note:
        1) Plot with Type 1 font to accommodate all platforms by default.
    """
    # Switch from default Type 3 to Type 1 font.
    if t1f:
        matplotlib.rcParams['ps.useafm'] = True
        matplotlib.rcParams['pdf.use14corefonts'] = True
        matplotlib.rcParams['text.usetex'] = True

    fig = plt.figure(path)
    
    ax = fig.add_subplot(111)
    ax.set_title(title)
    ax.set_xlabel(xl, style='italic')
    ax.set_ylabel(yl)
    
    x_list = range(0, len(xt_list))
    plt.xticks(x_list, ['$' + str(x_tick) + '$' for x_tick in xt_list])
    for y_list, style in zip(yl_list, style_list):
        ax.plot(x_list, y_list, style)
    
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()
