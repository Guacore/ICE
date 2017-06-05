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
# File: table_3.py
# Date: 04/07/2017

import copy
from ice_lib.utility import *
from ice_lib.preprocess import *
from ice_lib.retrieve import *
from ice_lib.survey import *
from ice_lib.evaluate import *

#       SECTION 1: Setup.

# Step 0: Declare constant components.
mod_list = ["sl_", "sll_exp_"]
top_list = ["top1", "top3", "top5", "top8", "top10"]

# Step 1: Specify settings for the retrieval task.
mod = mod_list[1] # retrieval method
top = top_list[0] # number of top-tfidf words to rep a song

# Step 2: Set survey & representation paths.
graph_path = "/home/LyricsRec/datasplit-700030/graph/" + top + "/post_uniq/"
sl_path = graph_path + "sl_" + top + ".edge"
sl_dict = load_el_by_tag(sl_path, 's', True)
sl_assoc_nodes = [w for wl in sl_dict.values() for w in wl]

# Step 3: Find stats on graph structure.
song_num = len(sl_dict)
sl_edge_num = len(sl_assoc_nodes)

if mod==mod_list[0]:
    word_num = len(set(sl_assoc_nodes))
    ll_edge_num = "-"
    exp_edge_num = "-"
    avg_deg = 2*sl_edge_num/(song_num+word_num)
else:
    ll_path = graph_path + "ll_" + top + "x3.edge"
    ll_dict = load_el_by_tag(ll_path, 'w', True)
    ll_assoc_nodes = [w for w_list in ll_dict.values() for w in w_list]
    
    word_num = len(set(list(ll_dict.keys()) + ll_assoc_nodes)) # keyword & related words

    ll_edge_num = word_num + len(ll_assoc_nodes) # self ref + directed pointing
    for kw, rw_l in ll_dict.items(): # non-duplicated reversed directed pointing
        for rw in rw_l:
            if rw not in ll_dict or kw not in ll_dict[rw]:
                ll_edge_num += 1

    exp_edge_num = 0 
    for kw_l in sl_dict.values():
        related_words = set()
        for kw in kw_l:
            for related_w in ll_dict[kw]:
                if related_w not in kw_l: # related word is a keyword
                    related_words.add(related_w)
        exp_edge_num += len(related_words)

    avg_deg = 2*(sl_edge_num+ll_edge_num+exp_edge_num)/(song_num+word_num)
            

copy_friendly = True
end_char = '\t\t'
if copy_friendly:
    end_char = '\n'

print("|V|:\t\t|T|:\t\t|E_et|:\t\t|E_tt|:\t\t|Ē_et|:\t\td̄(·):")
print(song_num, end=end_char)       # number of songs
print(word_num, end=end_char)       # number of keywords & related words
print(sl_edge_num, end=end_char)    # number of song-keyword relations
print(ll_edge_num, end=end_char)    # number of keyword-expansion relations
print(exp_edge_num, end=end_char)   # number of song-expansion relations
print(avg_deg, end=end_char)        # average degree
print()


