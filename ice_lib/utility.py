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
# Date: 06/06/2017
# Cont:
#	Func:
#       1) print_dict_entries               2) save_json_obj
#       3) load_json_obj                    4) use_type_1_font
#       4) plot_pdf_legend                  5) plot_pdf_figure
#       6) plot_venn_diagram

import json
import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib_venn



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


def use_type_1_font():
    """ Set Matplotlib to generate .pdf in Type 1 font instead of the default
        Type 3 font.
    Note:
        1) Manually set text in functions using Matplotlib will overwrite the
            default LaTeX font. Enclose text with '$' to ensure uniform font.
        2) Used before any Matplotlib functions.
    """
    matplotlib.rcParams['ps.useafm'] = True
    matplotlib.rcParams['pdf.use14corefonts'] = True
    matplotlib.rcParams['text.usetex'] = True # use LaTeX for all text handling
   

def plot_legend(path, label_list, style_list):
    """ Plot legend by itself without figure for easier processing.
    Param:
        param1 [string] path to save the legend.
        param2 [list] of string line labels.
        param3 [list] of string line style specifications.
    Note:
        1) Plot with Type 1 font to accomodate all platforms by default.
    """
    fig = plt.figure(path)
    plt.axis('off') # remove ticks

    ax = fig.add_subplot(111)
    for label, style in zip(label_list, style_list):
        ax.plot(0, 0, style, label=label) # dummy plot

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width*0.5, box.height*0.5])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig(path)
    plt.clf()


def plot_figure(path, title, xl, yl, xt_list, yl_list, style_list):
    """ Plot figure by itself without legend for easier processing.
    Param:
        param1 [string] path to save the figure.
        param2 [string] figure title.
        param3 [string] x-axis label.
        param4 [string] y-axis label.
        param5 [list] of string x-axis ticks.
        param6 [list] of lists of y-coordinates for each line.
        param7 [list] of string line style specifications.
    Note:
        1) Plot with Type 1 font to accommodate all platforms by default.
    """
    fig = plt.figure(path)
    
    ax = fig.add_subplot(111)
    ax.set_title(title)
    ax.set_xlabel(xl, style='italic')
    ax.set_ylabel(yl)
    
    x_list = range(0, len(xt_list))
    plt.xticks(x_list, ['$' + str(x_tick) + '$' for x_tick in xt_list])
    for y_list, style in zip(yl_list, style_list):
        ax.plot(x_list, y_list, style)
    
    plt.savefig(path)
    plt.clf()


def plot_venn_diagram(path, set_list, size_list, empty_area=0.0):
    """ Plot two or three circle Venn diagram. Suport manually setting display
        size for empty sets.
    Param:
        param1 [list] path to save the figure.
        param2 [list] of string set labels correspond to each circle.
        param3 [list] of sizes ordered by Venn diagram subregion encoding.
        param4 [float] area for an empty circle. Default=0.0.
    Note:
        1) param3 is ordered by binary countup from the left starting from 1 to
            encode each Venn diagram subregion.
            Ex: For venn2, '10'='Ab'="A and NOT B", '01'='aB'="Not A and B", and
            '11'='AB'="A and B".
        2) param4 should be in [0,1), as a non-empty set has size at least 1.
        3) Venn diagram is restricted to 2 or 3 sets.
    """
    # Step 1: Retrieve Venn function wrt the number of sets.
    set_num = len(set_list)
    venn_func = getattr(matplotlib_venn, 'venn'+str(set_num))
    
    # Step 2: Set minimum area for empty sets for cosmetic reason.
    dec_id_list = []
    if empty_area != 0:
        for set_id in range(set_num): # set id denotes digit position
            is_empty = True
            carry = pow(2,set_id) # every digit-flip by carry is a half cycle
            for half_cyc_id in range(int(pow(2, set_num-1)/carry)):
                for offset in range(carry):
                    if size_list[carry+2*half_cyc_id*carry+offset-1] != 0:
                        is_empty = False
            if is_empty: # all subregions of current set's circle are empty
                size_list[carry-1] = empty_area # min size for display
                dec_id_list.append(carry) # carry = idx+1
    
    # Step 3: Plot Venn diagram:
    fig = venn_func(subsets=size_list, set_labels=tuple(set_list))
    
    # Step 4: Label empty sets as '0'.
    for dec_id in dec_id_list:
        bin_id = ("{0:0"+str(set_num)+"b}").format(dec_id)[::-1] # Note 1)
        fig.get_label_by_id(bin_id).set_text('0')

    plt.savefig(path)
    plt.clf()
