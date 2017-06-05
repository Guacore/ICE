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
# File: preprocess.py
# Seri: 2/6
# Date: 03/15/2016
# Cont:
#	Func:
#		1) load_el_by_tag                   2) load_song_metadata_dict
#		3) load_lyric_dict                  4) join_dictionary
#		5) load_song_tfidf_dict             6) filter_song_tfidf_dict
#		7) generate_global_tfidf_dict       8) load_repr_by_tag

import json

def load_el_by_tag(path, tag, directed):
    """ Load and return a tagged_node-associated_node dictionary.
    Param:
        param1 [string] path to the edge list file.
        param2 [string] tag for identifying nodes used as keys.
        param3 [bool] whether one-direction or two-way loadng.
    Return:
        return1 [dict] where key=tagged node & val=list of assoc nodes.
    """
    ta_dict = {} # return1

    print("Loading edge list:\t",path)
    def add_tagged_assoc(tagged, assoc): # update tagged_node-assoc_node dict
        if tagged in ta_dict and assoc not in ta_dict[tagged]:
            ta_dict[tagged].append(assoc)
        else:
            ta_dict[tagged] = [assoc]

    with open(path) as f:
        for edge in f:
            entry = edge.strip().split(" ")
            
    # Step 1: Check the left node.
            if entry[0][:len(tag)] == tag: 
                tagged = entry[0]
                assoc = entry[1]
                add_tagged_assoc(tagged, assoc)
    
    # Step 2: Check the right node.
            if not directed and entry[1][:len(tag)] == tag:
                tagged = entry[1]
                assoc = entry[0]
                add_tagged_assoc(tagged, assoc)

    print("Number of "+ tag + "-nodes:\t", len(ta_dict), end='\n\n')

    return ta_dict


def load_song_metadata_dict(path, tag):
    """ Load and return a song-metadata dictionary.
    Param:
        param1 [string] path to load the song-metadata file.
        param2 [string] tag for prefixing to song ID.
    Return:
        return1 [dict] where key=song & val=list of metadata item.
    Note:
        1) return1 val format: [song_name, ?, artist, ?, track_name, generes,
            release_date]
    """
    metadata_dict = {} # return1
   
    print("Loading metadata:\t", path)
    with open(path) as f:
        for line in f:
            metadata = line.split('\t') # metadata delimiter='\t'
            
            key = tag + metadata[0]
            metadata[6] = metadata[6].split(',') # genere delimiter = ','
            metadata_dict[key] = metadata[1:]
    
    print("Number of metadata:\t", len(metadata_dict), end='\n\n')
    return metadata_dict


def load_lyric_dict(path, tag):
    """ Load and return a song-lyric dictionary.
    Param:
        param1 [string] path to song-lyric JSON file.
        param2 [string] tag for prefixing to song ID.
    Return:
        return1 [dict] where key=song & val=lyric.
    """
    lyric_dict = {} # return1
    
    print("Loading lyric dict:\t", path)
    with open(path) as f:
        dict_list = json.load(f)
        for d in dict_list:
            lyric_dict[tag + str(d['id'])] = d['lyrics']
    
    print("Number of lyrics:\t", len(lyric_dict), end='\n\n')
    return lyric_dict


def join_dictionary(item12_dict, item23_dict):
    """ Join an item1-item2 dictionary to an item2-item3 dictionary to
        form and return an item1-item3 dictionary.
    Param:
        param1 [dict] where key=item1 & val=list of item2
        param2 [dict] where key=item2 & val=list of itme3
    Return:
        return1 [dict] where key=itme1 & val=list of item3.
    """
    item13_dict = {} # return1
    
    for item1 in item12_dict:
        item2_list = item12_dict[item1]
        for item2 in item2_list:
            if item2 in item23_dict:
                if item1 not in item13_dict:
                    item13_dict[item1] = item23_dict[item2]
                else:
                    item13_dict[item1] += item23_dict[item2]

                item13_dict[item1] = list(set(item13_dict[item1])) # remove dup
        
    return item13_dict


def load_song_tfidf_dict(path, tag):
    """ Load and return a dictionary where key=song & val=2-tuple of the list of
        lyric keywords and the list of associated tfidf scores.
    Param:
        param1 [string] path to load the JSON file of a list of dict storing
                song id, tfidf-picked lyric keywords, and tfidf scores.
        param2 [string] tag for prefixing to song ID.
    Return:
        return1 [dict] where key=song & val=2-tuple of the list of tfidf-picked
                lyric keywords and the list of associated tfidf scores.
    """
    tfidf_dict = {} # return1

    with open(path) as f:
        dict_list = json.load(f)
        for iks_dict in dict_list:
            song = tag + str(iks_dict['id'])
            keywords = ['w' + k for k in iks_dict['keywords']]
            scores = iks_dict['scores']
            tfidf_dict[song] = (keywords, scores)
        
    return tfidf_dict



def filter_song_tfidf_dict(st_dict, sl_dict):
    """ Filter out lyric words that do NOT exist in the current song-lyric graph
        from the tfidf dictionary.
    Param:
        param1 [dict] where key=song & val=2-tuple of the list of tfidf-picked
            lyric keywords and the list of associated tfidf scores.
        param2 [dict] where key=song & val=list of lyric keywords.
    Return:
        return1 [dict] where key=song & val=2-tuple of the list of tfidf-picked
            lyric keywords and the list of associated tfidf scores.
    Note:
        1) return1 will contain less keywords if filtering happened.
        2) return1 may contain less songs than param1 if their keywords only
            exist in param2's missing songs; hence, all keywords are filtered.
        3) In-program filtering of the tfidf dict eliminates saving tailor-made
            tfidf dict files for diff SL graphs.
        4) @@@ should we support "exp_w"?
    """
    tfidf_dict = {} # return1
    
    # Step 1: Collect valid lyric words from the current song-lyric graph.
    valid_words = set()
    for song in sl_dict:
        valid_words |= set(sl_dict[song])
    
    # Step 2: Construct the tfidf dict which contains ONLY valid words.
    for song, (words,scores) in st_dict.items():
        for word, score in zip(words, scores):
            if word in valid_words:
                if song in tfidf_dict:
                    tfidf_dict[song][0].append(word)
                    tfidf_dict[song][1].append(score)
                else:
                    tfidf_dict[song] = ([word],[score])
    
    return tfidf_dict


def generate_global_tfidf_dict(st_dict):
    """ Generate a dictionary of lyrical word and its global tfidf score.
    Param:
        param1 [dict] where key=song & val=2-tuple of the list of lyrical
        keywords and the list of assoc local tfidf scores.
    Return:
        return1 [dict] where key=keyword & val=tfidf score summed across all
        songs.
    """
    global_tfidf_dict = {} # key=word & val=global tfidf score
    
    for (words,scores) in st_dict.values():
        for word, score in zip(words, scores):
            if word in global_tfidf_dict:
                global_tfidf_dict[word] += score
            else:
                global_tfidf_dict[word] = score
    
    return global_tfidf_dict


def load_repr_by_tag(path, tag, header=0):
    """ Load and return a tagged_data-representation dictionary.
    Param:
        param1 [string] path to the repr file.
        param2 [string] tag for identifying data whose repr should be loaded.
        param3 [int] number of header lines to skip. Default=0.
    Return:
        return1 [dict] where key=tagged data & val=repr vector
    """
    tr_dict = {} # return1

    print("Loading repr file:\t", path)
    with open(path) as f: 
        for i, line in enumerate(f.readlines()[header:]):
            tagged = line.split(" ")[0]
            if tagged[:len(tag)] == tag:
                tr_dict[tagged] = line.strip().split(" ")[1:]

    print("Number of " + tag + "-repr:\t", len(tr_dict), end='\n\n')

    return tr_dict


