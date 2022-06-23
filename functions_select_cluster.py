# As I see it, I need a different function for the f-score greedy algorithm and the recall and precision greedy algorithm
# The reason is that, when i have a conditon (e.g. recall = 0.2), i explore AND stop in the same function.
# Also, I believe it is better to get the clustering solutions first, as the greedy algorithm especification can change acordiong to my meetings
# For now, I will only do the greedy algorithm for the F-scores

def select_By_X(cluster_m_d, beta):
    """Selects the highest cluster acording to the provided metrics

    Parameters
    ----------
    cluster_m_d : dict
        First level is the cluster, second level is the metrics of the cluster.
        
    beta_name : str
        Main critera for selecting a cluster. It is an F-score.

    Returns
    -------
    s_cluster_d : dict
        Dictionary with the selected cluster and its data. It reports the id of the cluster,
        the value of metric 1 of the cluster, recall, precision, and if there was a tie when selecting the cluster.
    
    Notes
    -------
    The purpose of this function is tu prepare the data so it can be used by c_Selected_Cluster_D().
    It does so that the clusters are sorted by fscore, then by recall and then by prescion. It also adds the recall
    and precision of the selected cluster.
    """
    cluster_pepared_m_d = {}
    for c in cluster_m_d:
        fscore = cluster_m_d[c]['fscore'][beta]
        recall = cluster_m_d[c]['recall']
        precision = cluster_m_d[c]['precision']
        cluster_pepared_m_d[c] = (fscore, recall, precision)  # The priority of recall and precision are given by their order in the tuple 
    s_cluster_d = c_Selected_Cluster_D(cluster_pepared_m_d)
    s_c = s_cluster_d['cluster']
    s_cluster_d['recall'] = cluster_m_d[s_c]['recall']
    s_cluster_d['precision'] = cluster_m_d[s_c]['precision']
    return s_cluster_d

def c_Selected_Cluster_D(cluster_tuple_d):
    """Select the cluster with the highest value

    Parameters
    -------
    cluster_tuple_d : dict
        First level is the cluster, second level is a tuple that contain the metrics of the cluster

    Returns
    -------
    s_cluster_d : dict
        Dictionary with the selected cluster and its data. It reports the id of the cluster,
        the first metric of the tuple of the cluster, and if there was a tie.
    
    Notes
    -------
    The function sorts the tuples from the highest to the lowest value, giving priority to the first values in the tuple.
    If there is a tie (i.e. more than one cluster with the higest value) then the function selects one of the highest clusters arbirarily
    and reports in selected_cluster_d that there was a tie.
    """
    sorted_clusters = sorted(cluster_tuple_d.keys(), key=lambda x: cluster_tuple_d[x], reverse=True)
    max_cluster = sorted_clusters[0]
    max_values = cluster_tuple_d[max_cluster]
    tie = False
    if len(sorted_clusters) > 1:
        second_max_cluster = sorted_clusters[1]
        second_max_values = cluster_tuple_d[second_max_cluster]
        if max_values == second_max_values:
            tie = True
    max_value_1 = max_values[0]
    s_cluster_d = {'cluster': max_cluster, 'value': max_value_1, 'tie': tie}
    return s_cluster_d

def c_T_Greedy_D(level_data, topic_l, beta_l):
    """Creates the greedy dictionary of selected clusters

    Parameters
    ----------
    level_data : dict
        Dictionary with the data of the clustering solution of the current level.
        
    topic_l : list
        List of topics
        
    beta_l : list
        List of the betas to use for the F-score.

    Returns
    -------
    t_m_greedy_d : dict of dict
        Dictionary with clusters selected by the greedy algorithm. First level is the topics
    """
    t_m_greedy_d = {}
    for t in topic_l:
        t_m_greedy_d[t] = {}
        for beta in beta_l:
            beta_name = 'by_beta_' + str(beta)
            t_m_greedy_d[t][beta_name] = {}
            t_m_greedy_d[t][beta_name]['all_levels'] = recursive_T_Greedy_D(t, {}, level_data, beta)
            t_m_greedy_d[t][beta_name]['stoping_level'] = choose_Stoping_Level(t_m_greedy_d[t][beta_name]['all_levels'])
    return t_m_greedy_d

def recursive_T_Greedy_D(topic, greedy_d, level_data, beta):
    """Recursive function of c_T_Greedy_D()

    Parameters
    ----------
    topic : int
        Topic over which apply the greedy algrotihm
        
    greedy_d : dict
        Dictionary with the selected clusters. The first level is the level of the selected cluster. Only
        one cluster per level.
    
    level_data : dict
        Dictionary with the data of the clustering solution of the current level.
        
    beta : float
        Beta of the F-score.

    Returns
    -------
    greedy_d : dict
        Dictionary with the selected clusters. The first level is the level of the selected cluster. Only
        one cluster per level.
        
    Notes
    -------
    The condition " if 'children_clusters' in level_data.keys() " is the stop condition, and asks if there are more levels under
    the current level.
    """
    level = level_data['level']
    greedy_d[level] = select_By_X(level_data['t_cluster_metrics'][topic], beta)
    greedy_d[level]['level'] = level
    if 'children_clusters' in level_data.keys():
        s_cluster = greedy_d[level]['cluster']
        s_cluster_level_data = level_data['children_clusters'][s_cluster]
        greedy_d = recursive_T_Greedy_D(topic, greedy_d, s_cluster_level_data, beta)
    return greedy_d

def choose_Stoping_Level(all_levels_d):
    """Selects the stoping level from the clusters selected by the greedy algorithm

    Parameters
    ----------
    all_levels_d : dict
        Contains the data of the cluster selected at each level
        
    Returns
    -------
    stop_level_d : dict
        Containes the data of the selected level.
    """
    stop_level_d = None
    max_depth = max(all_levels_d)
    max_value = 0
    for level in range(1, max_depth + 1):
        level_d = all_levels_d[level]
        level_value = level_d['value']
        if level_value >= max_value:
            max_value = level_value
            stop_level_d = level_d
        else:
            break
    return stop_level_d

def c_T_Universal_Fscore_D(topic_l, beta_l, level_data):
    """Creates dictionary with all the fscores found in the clustering solution
    Parameters
    ----------
    topic_l : list
        List of topics
        
    beta_l : list
        List of the betas to use for the F-score.
    
    level_data : dict
        Dictionary with the data of the clustering solution of the current level.

    Returns
    -------
    universal_fscore_d : dict of dict
        The first level is the topics and the second level is the betas
    """
    universal_fscore_d = {}
    for topic in topic_l:
        beta_d = {beta: set() for beta in beta_l}
        universal_fscore_d[topic] = recursive_Universal_Fscore_D(topic, beta_d, level_data)
    return universal_fscore_d
        
def recursive_Universal_Fscore_D(topic, beta_d, level_data):
    """Recursive function of c_T_Universal_Fscore_D()
    
    Parameters
    ----------
    topic : int
        Topic over which to run the function
        
    beta_d : dict of set
        Contains the acumulated fscores of each beta
    
    level_data : dict
        Dictionary with the data of the clustering solution of the current level.
        
    Returns
    -------
    beta_d : dict of set
        Contains the acumulated fscores of each beta
    
    Notes
    -------
    The condition " if 'children_clusters' in level_data.keys() " is the stop condition, and asks if there are more levels under
    the current level.
    """
    topic_clusters = level_data['t_cluster_metrics'][topic]
    for cluster in topic_clusters:
        for beta in beta_d:
            fscore = topic_clusters[cluster]['fscore'][beta]
            beta_d[beta].add(fscore)
    if 'children_clusters' in level_data.keys():
        for cluster in level_data['children_clusters']:
            children_level_data = level_data['children_clusters'][cluster]
            beta_d = recursive_Universal_Fscore_D(topic, beta_d, children_level_data)
    return beta_d