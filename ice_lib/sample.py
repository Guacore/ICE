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
# File: sample.py
# Seri: 3/6
# Date: 03/15/2017
# Cont: 
#	Func:	
#       1) sample_queries                   2) convert_query_local_tfidf
#       3) convert_query_global_tfidf       4) split_joint_queries
#       5) save_joint_queries               6) load_joint_queries


import numpy as np
from collections import Counter
from random import shuffle
from preprocess import *


def sample_queries(user_quota, query_dict_list, query_quota, train_dict):
    """ Sample queries s.t. every user has sufficient samples for each type of
        queries.
    Param:
        param1 [int] num of user to sample.
        param2 [list] of dict corresponding to different types of queries, where
                key=user & val=list of query candidates. 
        param3 [int] num of queries to sample per user.
        param4 [dict] where key=user & val=list of user's training items.
    Return:
        return1 [list] of dict corresponding to different types of queries,
                where key=user & val=2-tuple of the list of queries and the list
                of blacklist items.
    """
    ut_dict_list = [] # return1
    
    # Step 1: Remove users with insufficient queries for any query type.
    sampled_users = list(query_dict_list[0].keys())
    for s_user in sampled_users:
        for query_dict in query_dict_list: # across query types
            if len(query_dict[s_user]) < query_quota: # insufficient queries
                sampled_users.remove(s_user)
                break
    
    # Step 2: Sample users.
    shuffle(sampled_users) # avoid seq sampling
    sampled_users = sampled_users[:user_quota]
        
    # Step 3: Sample queries for each user.
    for query_dict in query_dict_list:
        ut_dict = {} # return1
        for s_user in sampled_users:
            query_list = query_dict[s_user]
            shuffle(query_list) # avoid seq sampling
            ut_dict[s_user] = (query_list[:query_quota],train_dict[s_user])
            
        ut_dict_list.append(ut_dict)
    
    return ut_dict_list


def convert_query_local_tfidf(query_quota, ut_dict, st_dict):
    """ Ensure every query makes contribution by converting song queries to word
        queries via selecting top-tfidf word within the song across all songs 
        and moving down to the next top-tfidf word.                         
    Param:
        param1 [int] num of queries to sample per user.
        param2 [dict] where key=user & val=2-tuple of the list of query songs
                and the list of training songs.
        param3 [dict] where key=song & val=2-tuple of the list of lyric words
                and the list of assoc tfidf scores.
    Return:
        return1 [dict] where key=user & val=2-tuple of the list of local
                top-tfidf lyric-word queries and the list of training songs.
    Note:
        1) Query words are ordered basing on tfidf scores within respective
            songs and then across all query songs for selection.
        2) Different songs may have different numbers of assoc lyric words.
    """
    conv_ut_dict = {}
    
    for user, (query_songs, train_songs) in ut_dict.items():

        words_list = [st_dict[qs][0] for qs in query_songs]
        scores_list = [st_dict[qs][1] for qs in query_songs] 
        
        # Step 1: Pad score lists to the same length.
        max_len = max(len(wl) for wl in words_list)
        score_mat = -np.array([scores + (max_len-len(scores))*[float('-inf')] for scores in scores_list])

        # Step 2: Generate order for each song's lyric words.
        order_mat = np.asarray([sl.argsort() for sl in score_mat])
                                                          
        # Step 3: Order same-level words across songs by tfidf score.
        query_words = []
        for col_indices in order_mat.T: # move horizontally across words
            col_scores = np.asarray([score_mat[idx][word_idx] for idx, word_idx in enumerate(col_indices)])
            song_order = col_scores.argsort()

        # Step 4: Select local top-tfidf words level-wise as queries.
            for song_idx in song_order: # move vertically across songs
                if len(query_words) >= query_quota: # handle neg param1
                    break
                        
                word_idx = col_indices[song_idx]
                if score_mat[song_idx][word_idx] != float('inf'): # skip padding
                    query_word = words_list[song_idx][word_idx]
                    if query_word not in query_words:
                        query_words.append(query_word)
                    
        conv_ut_dict[user] = (query_words, train_songs)

    return conv_ut_dict


def convert_query_global_tfidf(query_quota, ut_dict, st_dict):
    """ Convert song queries to word queries by selecting their lyrical words
        with the highest tfidf score summed across all available songs.
    Param:
        param1 [int] num of queries to sample per user.
        param2 [dict] where key=user & val=2-tuple of the list of query songs
                and the list of training songs.
        param3 [dict] where key=song & val=2-tuple of the list of lyric words
                and the list of assoc tfidf scores.
    Return:
        return1 [dict] where key=user & val=2-tuple of the list of global
                top-tfidf lyric-word queries and the list of training songs.
    Note:
        1) Query words are ordered basing on tfidf scores across all available
            songs and then across all query songs for selection.
        2) Different songs may have different numbers of assoc lyric words.
    """
    conv_ut_dict = {}
    
    # Step 1: Construct dict of word & global tfidf score sum.
    tfidf_dict = generate_global_tfidf_dict(st_dict) # @ may be done outside
    
    # Step 2: Collect all words from query songs.
    for user, (query_songs,train_songs) in ut_dict.items():
        word_list = []
        for query_song in query_songs:
            word_list += st_dict[query_song][0]
        word_list = list(set(word_list)) # remove dup
        
    # Step 3: Select global top-tfidf words as queries.
        filt_tfidf_dict = {w:tfidf_dict[w] for w in word_list}
        query_words = [w for (w,_) in Counter(filt_tfidf_dict).most_common(query_quota)]
        conv_ut_dict[user] = (query_words, train_songs)
        
    return conv_ut_dict


def split_joint_queries(ut_dict_list, split_num):
    """ Split joint queries to specified number of chunks.
    Param:
        param1 [list] of dict where key=user & val=2-tuple of the list of
            queries and the list of training items.
        param2 [int] number of chunks to split a query dict.
    Return:
        return1 [list] of lists of dict where key=user & val=2-tuple of the
            list of queries and the list of training itmes.
    Note:
        1) Joint queries are sampled from the same set of users.
        2) param1's members share the same set of keys.
        3) param1's members are different types of queries from the same
            sampling process for each retrievals.
    """
    ut_dl_list = [] # return1
    
    # Step 1: Split query dict keys.
    users = list(ut_dict_list[0].keys())
    user_chunks = [users[idx::split_num] for idx in range(split_num)]
    user_chunks[:] = (uc for uc in user_chunks if uc != []) # rm empty chunks
    
    # Step 2: Split query dict by chunked keys:
    for user_chunk in user_chunks:
        chunked_ut_dict_list = []

        for ut_dict in ut_dict_list: # split diff queries w/ the same user chunk
            chunked_ut_dict = {user:ut_dict[user] for user in user_chunk}
            chunked_ut_dict_list.append(chunked_ut_dict)
                
        ut_dl_list.append(chunked_ut_dict_list)
                
    return ut_dl_list
    

def save_joint_queries(ut_dl_list, name_list, path):
    """ Save joint-split queries as auto-numbered JSON files.
    Param:
        param1 [list] of lists of dict where key=user & val=2-tuple of the list
            of queries and the list of training items.
        param2 [list] of names for the query files.
        param3 [string] path to the directory to save the JSON query files.
    Note:
        1) Joint queris are sampled from the same set of users.
    """
    for serial_num, ut_dict_list in enumerate(ut_dl_list):
        for name, ut_dict in zip(name_list, ut_dict_list):
            with open(path + name + str(serial_num), 'w') as f:
                json.dump(ut_dict, f, indent=4, sort_keys=True) # pprint JSON


def load_joint_queries(name_list, path, lb, ub):
    """ Load joint-split JSON query files between specified bounds and combine
        them into a single query dictionary.
    Param:
        param1 [list] of names of query files (w/o serial number) to combine.
        param2 [string] path to load the JSON query files.
        param3 [int] lower bound serial number to start loading query files.
        param4 [int] upper-bound serial number to end loading query files.
    Return:
        return1 [list] of dict where key=user & val=2-tuple of the list of 
            queries and the list of training items.
    Note:
        1) Joint queries are sampled from the same set of users.
        2) param4 is inclusive.
    """
    ut_dict_list = [] # return1: query-dictionary list
    
    load_num = ub-lb+1 # find inclusive interval
    for name in name_list:
        ut_dict = {}

        for idx in range(load_num):
            with open(path + name + str(lb+idx)) as f:
                ut_dict.update(json.load(f)) # combine query dict

        ut_dict_list.append(ut_dict)
    
    return ut_dict_list
