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
# File: retrieve.py
# Seri: 4/6
# Date: 03/15/2016
# Cont:
#	Clas:
#		1) IndexedMatrix
#	Func:
#       1) retrieve_by_random               2) retrieve_by_popularity
#		3) retrieve_by_keyword              4) retrieve_by_repr
#		5) generate_indexed_matrix          6) calculate_repr_distance


import numpy as np
from random import shuffle
from collections import Counter
from sklearn.metrics import pairwise_distances


class IndexedMatrix():
    """
    Store items and their respective representations.
    """
    
    def __init__(self, items, repr_matrix):
        """ Constructor for IndexedMatrix.
        Param:
            param0 [self] reference to this object.
            param1 [list] of items.
            param2 [list] of lists of item-associated repr.
        """
        self.items = np.array(items)
        self.repr_matrix = np.array(repr_matrix).astype(np.float32)


def retrieve_by_random(quota, cand_list):
    """ Randomly retrieve k items.
    Param:
        param1 [int] number of items to retrieve.
        param2 [list] of candidate songs.
    Return:
        return1 [list] of randomly retrieved items.
        """
    # Step 1: Shuffle to prevent sequential sampling.
    shuffle(cand_list)
    
    # Step 2: Retrieve the first k random items.
    result_list = cand_list[:quota] # return1
    
    return result_list


def retrieve_by_popularity(quota, cand_list, popularity_dict):
    """ Retrieve the top-k most popular items.
    Param:
        param1 [int] number of items to retrieve.
        param2 [list] of candidate items.
        param3 [dict] where key=item & val=popularity.
    Return:
        return1 [list] of retrieved items ordered descendingly by popularity.
    """
    result_list = [] # return1
    
    # Step 1: Descendingly sort the songs by popularity.
    item_list = [i for (i,_) in Counter(popularity_dict).most_common()]

    # Step 2: Retrieve the top-k most popular items.
    for item in item_list:
        if len(result_list) >= quota:
            break
        if item in cand_list:
            result_list.append(item)
        
    return result_list


def retrieve_by_keyword(quota, query_list, cand_list, content_dict):
    """ Retrieve the top-k items with the most query occurrences counts.
    Param:
        param1 [int] number of items to retrieve.
        param2 [list] of queries.
        param3 [list] of candidate items.
        param4 [dict] where key=retrieved item & val=textual content.
    Return:
        return1 [list] of retrieved items ordered descendingly by the number of
                query occurrences.
    Note:
        1) Similarity calculated by counting query occurrences in the textual
            content without segmentation.
    """
    # Step 1: Construct the occurrence count look-up table.
    inv_idx = {}
    for cand in cand_list:
        if cand in content_dict: # textual content exists
            inv_idx[cand] = 0
            
            for query in query_list:
                inv_idx[cand] += content_dict[cand].count(query[1:])

    # Step 2: Retrieve the top-k items with the most keyword-matching frequency.
    result_list = [i for (i,_) in Counter(inv_idx).most_common(quota)] # return1
        
    return result_list


def retrieve_by_repr(quota, query_list, qr_dict, rec_mat, metric="cosine"):
    """ Retrieve the top-k items most similar to the query in terms of
        representation.
    Param:
        param1 [int] number of items to retrieve.
        param2 [list] of queries.
        param3 [dict] where key=query & val=representation.
        param4 [IndexedMatrix] of items.
        param5 [string] distance metric from sklearn.metrics, e.g. "cosine" &
                "euclidean". Default="cosine".
    Return:
        return1 [list] of retrieved items ordered descendingly by representation
                similarity.
    """
    result_list = [] # return1
    
    query_mat = generate_indexed_matrix(query_list, qr_dict)
        
    # Step 1: Calculate the distance b/t user queries and candidate items.
    dist_mat = calculate_repr_distance(query_mat, rec_mat, metric)

    # Step 2: Order each query's candidate items by disance.
    order_mat = np.asarray([sl.argsort() for sl in dist_mat])

    # Step 3: Order same-level candidate items across queries by distance.
    for col_indices in order_mat.T: # move horizontally across rec items
        col_scores = np.asarray([dist_mat[idx][rec_idx] for idx, rec_idx in enumerate(col_indices)])
        query_order = col_scores.argsort()
        
    # Step 4: Levelwise retrieve the top-k items closest to queries.
        for query_idx in query_order: # move vertically across queries
            if len(result_list) >= quota: # handle neg top_k
                break
                
            rec_idx = col_indices[query_idx]
            rec_item = rec_mat.items[rec_idx]
	
            if rec_item not in result_list:
                result_list.append(rec_item)
            
    return result_list


def generate_indexed_matrix(items, repr_dict):
    """ Initialize an IndexedMatrix object with specified item list and provided
        representation dictionary.
    Param:
        param1 [list] of specified items.
        param2 [dict] where key=item & val=repr.
    Return:
        return1 [IndexedMatrix] obj.
    """
    repr_matrix = [repr_dict[item] for item in items]
    return IndexedMatrix(items, repr_matrix)


def calculate_repr_distance(query_mat, rec_mat, metric="cosine"):
    """ Calculate the distance between queries and candidate items.
    Param:
        param1 [IndexedMatrix] of queries.
        param2 [IndexedMatrix] of rec candidates.
        param3 [string] distance metric. Default="cosine".
    Return:
        return1 [ndarray] of distances b/t every query and candidate items.
    Note:
        1) Smaller distance indicates higher similarity.
        2) return1 rows are indexed by queries and columns are indexed by rec
            candidates.
    """
    if metric == "dot_product":
        dist_mat = -np.dot(query_mat.repr_matrix, rec_mat.repr_matrix.T)
    else:
        dist_mat = pairwise_distances(query_mat.repr_matrix, rec_mat.repr_matrix, metric)

    return dist_mat


