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
# File: figure_5.py
# Date: 06/02/2017

from ice_lib.utility import *
from ice_lib.preprocess import *
from ice_lib.retrieve import *
from ice_lib.evaluate import *


title = "Word-to-Song Retrieval Task (Keyword)"
xl = "$|W|$" # '$' to compensate for Type 1 Fonts
xt_list = ['1', '3', '5', '8', '10']
style_list = ['c*-', 'bo-', 'ys-', 'r^-']

#	SECTION 1: Setup.
graph_path = "/home/LyricsRec/datasplit-700030/graph/"
lyric_path = "/home/LyricsRec/sourcefile/lyrics-cut.json"
latest_song_path = graph_path + "top1/post_uniq/sl_top1.edge" # top1 has the most abundant songs

lyric_dict = load_lyric_dict(lyric_path, 's')
avail_song_list = list(load_el_by_tag(latest_song_path, 's', True).keys())

# Step 0: Declare constant components.
mod_list = ["rand", "w2v_", "sl_", "sll_exp_"]
top_list = ["top1", "top3", "top5", "top8", "top10"]
quo_list = [10, 50, 100]


query_list = ['w失落', 'w心痛', 'w想念', 'w深愛', 'w難過', 'w回家', 'w房間',
    'w海邊', 'w火車', 'w花園', 'w夕陽', 'w日出', 'w日落', 'w月亮', 'w黑夜']


# Step 1: Generate plot label.
label_list = ["RAND", "AVGEMB", "BPT", "ICE (exp-3)"]

label_dict = dict()
label_dict["plot/keyword_legend.pdf"] = (label_list, style_list)
save_json_obj(label_dict, "plot/figure_5_label.json")

# Step 2: 
stat_dict = dict()
rand_done = False
rand_mi_p = 0

for quo in quo_list:
    print("At quota=", quo)

    yl = "Precision@" + str(quo)
    path = "plot/keyword_p@" + str(quo) + ".pdf"
    yl_list = []
    for mod in mod_list:
        print("At quota:mod=%s:%s" % (quo, mod))

        y_list = []
        for top in top_list:
            print("At quota:mod:top=%s:%s:%s" % (quo, mod, top))

            # Step 2: Set survey & representation paths.
            if mod=="rand": # run random baseline only ONCE
                if rand_done:
                    continue
                else:
                    rand_done = True
                fname = mod
            elif mod=="km":
                fname = mod
            elif mod=="w2v_":
                fname = mod + top
            elif mod=="sl_":
                fname = "unorm_2-undir_" + mod + top
            elif mod=="sll_":
                fname = "unorm_2-undir_" + mod + top + "x3"
            else:
                fname = "unorm_2-dir_" + mod + top + "x3"
               
            repr_path = graph_path + "all_repr_api/" + fname + ".embd"


            #	SECTION 2: Load resources.
            # Step 1: Set paths.
            synonym_path = graph_path + top + "/" + "post_uniq/" + "ll_" + top + "x3.edge" 
            syn_dict = load_el_by_tag(synonym_path, 'w', True) # load LL edge list

            # Load repr dicts.
            if mod!="rand" and mod!="km":
                if mod=="sll_exp_": # SLL exp 
                    repr_tag = 'exp_w'
                else: 
                    repr_tag = 'w'

                lyric_repr_dict = load_repr_by_tag(repr_path, repr_tag, 1)
                song_repr_dict = load_repr_by_tag(repr_path, 's', 1)
                rec_mat = generate_indexed_matrix(list(song_repr_dict.keys()), song_repr_dict)


            #	SECTION 3: Conduct the retrieval task.
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


            #	SECTION 4: Evaluate results.
            query_num = len(query_list)
            avail_sl_list = [avail_song_list]*query_num # list of lists of available songs
            tp_fp_list = [quo]*query_num
            copy_friendly = False

            # 5-1: Evaluation query relevance.
            ql_list = [[q] for q in query_list] # list of lists of queries
            tp_list = count_keyword_containment(ql_list, rl_list, lyric_dict, "w" )
            mi_p = calculate_micro_precision(tp_list, tp_fp_list)

            y_list.append(mi_p) # top

            if mod=="rand":
                rand_mi_p = mi_p

        if mod=="rand": # random baseline is run only ONCE
            y_list = len(top_list)*[rand_mi_p]
        yl_list.append(y_list) # mod

    stat_dict[path] = (title, xl, yl, xt_list, yl_list, style_list)

save_json_obj(stat_dict, "plot/figure_5_stat.json")

