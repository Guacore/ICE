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
# File: survey.py
# Seri: 5/6
# Date: 03/15/2017
# Cont:
#	Func:
#       1) generate_survey_dict

def generate_survey_dict(sl_list, query_list, lyric_dict, metadata_dict, syn_dict):
    """ Generate a survey dictionary for each method by manually filter
        retrieved songs.
    Param:
        param1 [list] of rec song list.
        parma2 [list] of responsible contextual query assoc w/ param1.
        param3 [dict] where key=song & val=lyric.
        param4 [dict] where key=song & val=list of metadata items.
        param5 [dict]
    Return:
        return1 [dict] where key= query & val=list of 5-tuple of rec song,
            metadata, lyric, whether its lyric contains the query, and the
            list of the query's distinct synonyms contained in the song.
    Note:
        1) param4 val format: [song_name, ?,artist, ?,track_name, generes,
            release_date]
        2) @@@ Need annotation
    """
    survey_dict = {}
    
    for song_list, query in zip(sl_list, query_list):
        for song in song_list:
            lyric = lyric_dict[song]
            
            try:
                syn_list = syn_dict[query]
            except KeyError:
                print("Keyword: \'" + query + "\' does not have synonym!", end = "\t")
                continue
            
            clean_syn_list = []
            for syn in syn_list:
                if syn[1:] in lyric:
                    clean_syn_list.append(syn)
            
            song_tup = (song, metadata_dict[song], lyric, query[1:] in lyric, clean_syn_list)
            if query not in survey_dict:
                survey_dict[query] = [song_tup]
            else:
                survey_dict[query].append(song_tup)
        
    return survey_dict

