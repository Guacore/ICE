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
# File: evaluate.py
# Seri: 6/6
# Date: 03/15/2017
# Cont:
#       Func:
#	        1) count_keyword_containment	2) calculate_micro_precision
#	        3) calculate_micro_recall	    4) calculate_macro_precision
#	        5) calculate_macro_recall	    6) calculate_f1_score
#	        7) calculate_all_micro          8) calculate_all_macro
#           9) pretty_print_eval


def count_keyword_containment(kl_list, sl_list, lyric_dict, tag=""):
    """ Count the number of songs which contain any of the keywords for each
        keyword set.
    Param:
	param1 [list] of lists of keywords.
	param2 [list] of lists retrieved songs.
	param3 [dict] where key=song & val=lyric.
	parma4 [string] tag used to de-tag keywords during matching. Default="".
    Return:
	return1 [list] of the number of songs which contain any of the keywords.
    """
    count_list = [] # return1

    for keyword_list, song_list in zip(kl_list, sl_list):
        count = 0

        for song in song_list:
            for keyword in keyword_list:
                if keyword[len(tag):] in lyric_dict[song]:
                    count += 1
                    break

        count_list.append(count)
            
    return count_list


def calculate_micro_precision(tp_list, tp_fp_list):
    """ Calculate the micro average precision.
    Param:
	param1 [list] of true positives.
	param2 [list] of the sum of true positives and false positives.
    Return:
	return1 [float] micro average precision.
    """
    return sum(tp_list) / sum(tp_fp_list)


def calculate_micro_recall(tp_list, tp_fn_list):
    """ Calculate the micro average recall.
    Param:
        param1 [list] of true positives.
	param2 [list] of the sum of true positives and false negatives.
    Return:
	return1 [float] micro average recall.
    """
    return sum(tp_list) / sum(tp_fn_list)


def calculate_macro_precision(tp_list, tp_fp_list):
    """ Calculate the macro average precision.
    Param:
 	param1 [list] of true positives.
	param2 [list] of the sum of true positives and false positives.
    Return:
	return1 [float] macro average precision.
    """
    precision_list = [n/d for n,d in zip(tp_list, tp_fp_list)]
	
    return sum(precision_list) / len(precision_list)


def calculate_macro_recall(tp_list, tp_fn_list):
    """ Calculate the macro average recall.
    Param:
	param1 [list] of true positives.
	param2 [list] of the sum of true positives and false negatives.
    Return:
	return1 [float] macro average recall.
    """
    recall_list = [n/d for n,d in zip(tp_list, tp_fn_list)]

    return sum(recall_list) / len(recall_list)


def calculate_f1_score(precision, recall):
    """ Calculate the average F1 score.
    Param:
        param1 [float] micro/macro precision.
        param2 [float] micro/macro recall.
    Return:
        return1 [float] micro/macro average F1 score.
    """
    return 2 * (precision*recall) / (precision+recall)


def calculate_all(tp_list, tp_fp_list, tp_fn_list):
    """ Calculate all relevance measurements.
    Param:
        param1 [list] of true positives.
        param2 [list] of the sum of true positives and false positives.
        param3 [list] of the sum of true positives and false negatives.
    Return:
        return1 [float] micro average precision.
        return2 [float] micro average recall.
        return3 [float] micro average F1 score.
        return4 [float] macro average precision.
        return5 [float] macro average recall.
        return6 [float] macro average F1 score.
    """
    mi_p = calculate_micro_precision(tp_list, tp_fp_list)
    mi_r = calculate_micro_recall(tp_list, tp_fn_list)
    mi_f = calculate_f1_score(mi_p, mi_r)

    ma_p = calculate_macro_precision(tp_list, tp_fp_list)
    ma_r = calculate_macro_recall(tp_list, tp_fn_list)
    ma_f = calculate_f1_score(ma_p, ma_r)

    return mi_p, mi_r, mi_f, ma_p, ma_r, ma_f


def pretty_print_all(kl_list, tp_list, tp_fp_list, tp_fn_list, copy_friendly):
    """ Pretty print all relevance measurements.
    Param:
        param1 [list] of lists of keywords.
        param2 [list] of true positives.
        param3 [list] of the sum of true positives and false positives.
        param4 [list] of the sum of true positives and false negatives.
        param5 [bool] whether to print in a way that is easy to copy and paste.
    """
    # Step 1: Setup constants.
    kl_num = len(kl_list) 
    separator = (kl_num+2)*8*'-'
    end_char = '\t'
    if copy_friendly:
        end_char = '\n'

    # Step 2: Print the numbering for each query set.
    print('No:\t', end='\t')
    for idx in range(0, kl_num):
        print(str(idx+1), end='\t')
    print('\n' + separator)

    # Step 3: Print each query set.
    print('Query:', end='')
    if copy_friendly:
        print()
        for k in [k for kl in kl_list for k in kl]:
            print(k)
    else: 
        for kl in zip(*kl_list):
            print('\t', end='')
            for keyword in kl:
                print(end_char + keyword, end='')
            print()
    print(separator)

    # Step 4: Print the individual relevance measures.
    print("Precision:", end='')
    for tp, tp_fp in zip(tp_list, tp_fp_list):
        print(end_char + '{0:.3f}'.format(tp/tp_fp), end='') 

    print(end_char + "\nRecall:\t", end='')
    for tp, tp_fn in zip(tp_list, tp_fn_list):
        print(end_char + '{0:.3f}'.format(tp/tp_fn), end='')
    print('\n' + separator)

    # Step 5: Print the components used to calculate precision & recall.
    print("TP:\t", end='')
    for tp in tp_list:
        print(end_char + str(tp), end='')
    
    print(end_char + "\nTP+FP:\t", end='')
    for tp_fp in tp_fp_list:
        print(end_char + str(tp_fp), end='')

    print(end_char + "\nTP+FN:\t", end='')
    for tp_fn in tp_fn_list:
        print(end_char + str(tp_fn), end='')
    print('\n' + separator)

    # Step 6: Print the sum of each components.
    print("TP sum:\t\tTP+FP:\t\tTP+FN:")
    print(3*("%d"+end_char+end_char) % (sum(tp_list), sum(tp_fp_list), sum(tp_fn_list)))
    print(separator)

    # Step 7: Print all micro & macro relevance measures.
    result_tuple = calculate_all(tp_list, tp_fp_list, tp_fn_list)
    print("Micro prec:\tMicro recall:\tMicro F1:\tMacro prec:\tMacro recall:\tMacro F1:")
    print(6*("%f"+end_char) % result_tuple)
    print()
