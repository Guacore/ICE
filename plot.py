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
# File: plot.py
# Date: 06/06/2017

from ice_lib.utility import *

label_path_list = ["plot/figure_5_label.json", "plot/figure_6_label.json"]
stat_path_list = ["plot/figure_5_stat.json", "plot/figure_6_stat.json"]

# Step 1: Set to output Type 1 font .pdf.
use_type_1_font()

# Step 2: Plot legends.
for label_path in label_path_list:
    label_dict = load_json_obj(label_path)

    for legend_path in label_dict:
        plot_legend(legend_path, *label_dict[legend_path])

# Step 3: Plot figures.
for stat_path in stat_path_list:
    stat_dict = load_json_obj(stat_path)
    
    for figure_path in stat_dict:
        plot_figure(figure_path, *stat_dict[figure_path])
