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
# File: table_6.py
# Date: 03/15/2017

from ice_lib.utility import *
from ice_lib.preprocess import *
from ice_lib.retrieve import *
from ice_lib.survey import *
from ice_lib.evaluate import *

#	SECTION 1: Setup.
graph_path = "/home/LyricsRec/datasplit-700030/graph/"
repr_path = graph_path + "all_repr/"
survey_path = "/home/LyricsRec/survey/"
source_path = "/home/LyricsRec/sourcefile/"     # for reading source files

# Step 0: Declare constant components.
mod_list = ["rand", "km", "w2v_", "sl_", "sll_", "sll_exp_"]
top_list = ["top1", "top3", "top5", "top8", "top10"]
syn_list = ["", "x3"]
quo_list = [10, 50, 100]

# Step 1: Specify settings for the retrieval task.
mod = mod_list[5] # retrieval method
top = top_list[4] # number of top-tfidf words to rep a song
syn = syn_list[1] # number of context-similar words
quo = quo_list[2] # quota of retrieved items

# Step 2: Set survey & representation paths.
if mod==mod_list[0] or mod==mod_list[1]:    # rand or km
    fname = mod
elif mod==mod_list[2]:
    fname = mod + top + syn
elif mod==mod_list[3]:
    fname = "unorm_2-undir_" + mod + top
elif mod==mod_list[4]:
    fname = "unorm_2-undir_" + mod + top + "x3"
else:
    fname = "unorm_2-dir_" + mod + top + "x3"
   
survey_path += "survey-" + fname + "_" + str(quo) + ".json"
repr_path += fname + ".embd"


#	SECTION 2: Load resources.
# Step 1: Set paths.
metadata_path = source_path + "song_infos_20151116.tsv" 
lyric_path = source_path + "lyrics-cut.json"
latest_song_path = graph_path + "top1/post_uniq/sl_top1.edge" # top1 has most songs
synonym_path = graph_path + top + "/" + "post_uniq/" + "ll_" + top + "x3.edge" 


# Step 2: Load dicts.
print("\nLoad metadata:")
metadata_dict = load_song_metadata_dict(metadata_path, 's')
print("Load lyric dict:")
lyric_dict = load_lyric_dict(lyric_path, 's')
print("Load available songs:")
avail_song_list = list(load_el_by_tag(latest_song_path, 's', True).keys())
print("Load synonym dict:")
syn_dict = load_el_by_tag(synonym_path, 'w', True) # load LL edge list

# Load repr dicts.
if mod!=mod_list[0] and mod!=mod_list[1]:
    if mod==mod_list[5]: # SLL exp 
        repr_tag = 'exp_w'
    else: 
        repr_tag = 'w'

    print("Loading lyric repr:")
    lyric_repr_dict = load_repr_by_tag(repr_path, repr_tag, 1)
    print("Loading song repr:")
    song_repr_dict = load_repr_by_tag(repr_path, 's', 1)
    rec_mat = generate_indexed_matrix(list(song_repr_dict.keys()), song_repr_dict)


#	SECTION 3: Conduct the retrieval task.
query_list = ['w失落', 'w心痛', 'w想念', 'w深愛', 'w難過', 'w回家', 'w房間',
        'w海邊', 'w火車', 'w花園', 'w夕陽', 'w日出', 'w日落', 'w月亮', 'w黑夜']

rl_list = [] # list of rec list
for query in query_list:
    # Step 1: Random.
    if mod == "rand":
         songs = retrieve_by_random(quo, avail_song_list)
        
    # Step 2: Keyword-matching.
    elif mod == "km":
        songs = retrieve_by_keyword(quo, [query], avail_song_list, lyric_dict)

    # Step 3: Representation, i.e. w2v, sl, sll, sll_exp, sll_nxm, w2v_exp
    else:
        if mod=="sll_exp_":
            query = "exp_w" + query[1:] # replace 'w' tag with 'exp_w' tag
        if query in lyric_repr_dict: # Rec ONLY if repr exists.
            songs = retrieve_by_repr(quo, [query], lyric_repr_dict, rec_mat)
        else:
            songs = []

    rl_list.append(songs)

survey_dict = generate_survey_dict(rl_list, query_list, lyric_dict, metadata_dict, syn_dict)
save_json_obj(survey_dict, survey_path)


#	SECTION 4: Evaluate results.
query_num = len(query_list)
avail_sl_list = [avail_song_list]*query_num # list of lists of available songs
tp_fp_list = [quo]*query_num
copy_friendly = False

# 5-1: Evaluate query relevance.
ql_list = [[q] for q in query_list] # list of lists of queries
tp_list = count_keyword_containment(ql_list, rl_list, lyric_dict, "w" )
tp_fn_list = count_keyword_containment(ql_list, avail_sl_list, lyric_dict, "w")

pretty_print_all(ql_list, tp_list, tp_fp_list, tp_fn_list, copy_friendly)

# 5-2: Evaluate query extension relevance.
ql_list = []
for q in query_list:
    try:
        ql_list.append(syn_dict[q])
    except KeyError:
        print("Keyword:" + q + "does NOT have synonym!", end="\n")

tp_list = count_keyword_containment(ql_list, rl_list, lyric_dict, "w")
tp_fn_list = count_keyword_containment(ql_list, avail_sl_list, lyric_dict, "w")

pretty_print_all(ql_list, tp_list, tp_fp_list, tp_fn_list, copy_friendly)

