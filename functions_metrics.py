def t_Cluster_Metrics(level_data, t_references_d, beta_l):
    """Create the metrics for each topic and each cluster

    Parameters
    ----------
    level_data : dict
        Dictionary with the data of the clustering solution of the current level.
        
    t_references_d : dict of set
        The key is the topic and the value is the set of references of the topic. The references are int type.
        
    beta_l : list
        List of the betas to use for the F-score.
    
    Returns
    -------
    t_cluster_metrics_d : dict of dict
        Dictionary three levels where the first key is the topic, the second level is the cluster id, the third level is the metrics
        and the values is the value of the metrics (except for 'fscore', whose value is another dictionary with the f-score betas and
        the value of the f-score betas).
    
    Notes
    -------
    cp = condition positive
    cr = condition retrieved
    tp = true positive
    fp = false positive
    fn = false negative
    """
    t_cluster_metrics_d = {}
    for t in t_references_d:
        t_cluster_metrics_d[t] = {}
        cp = len(t_references_d[t])
        positive_clusters_d = level_data['t_positive_clusters_d'][t]
        all_clusters = level_data['merging_data']['jclu_d']
        for cluster in all_clusters:
            cr = len(all_clusters[cluster])
            if cluster in positive_clusters_d:
                tp = len(positive_clusters_d[cluster])
            else:
                tp = 0
            fp = cr - tp
            fn = cp - tp
            recall = float(tp) / cp
            precision = float(tp) / cr
            t_cluster_metrics_d[t][cluster] = {'cp': cp, 'cr': cr, 'tp': tp, 'fp': fp, 'fn': fn,  'recall': recall, 'precision': precision, 'fscore': {}}
            for beta in beta_l:
                t_cluster_metrics_d[t][cluster]['fscore'][beta] = f_Score_From_Rec_Pre(recall, precision, beta)
    return  t_cluster_metrics_d


def f_Score_From_Rec_Pre(recall, precision, b):
    """Calculate the F-Score

    Parameters
    ----------
    recall : float
        
    precision : float
    
    b : float
        Beta of the F-score
    
    Returns
    -------
    fscore : float
        F-score for the given beta
    
    Notes
    -------
    source = https://en.wikipedia.org/wiki/F-score
    """
    if recall > 0.0 :
        b2 = b**2
        num = (1+b2) * precision * recall
        den = (b2*precision) + recall
        fscore = float(num) / den
    else:
        fscore = 0.0
    return fscore

def c_Metric_Recursion(level_data, t_references_d, beta_l):
    """Create recurcion of the metrics dictionary

    Parameters
    ----------
    level_data : dict
        Dictionary with the data of the clustering solution of the current level.
        
    t_references_d : dict of set
        The key is the topic and the value is the set of references of the topic. The references are int type.
        
    beta_l : list
        List of the betas to use for the F-score.
    
    Returns
    -------
    level_data : dict
        Dictionary with the data of the clustering solution of the current level.
    
    Notes
    -------
    The condition " if 'children_clusters' in level_data.keys() " is the stop condition, and asks if there are more levels under
    the current level.
    """
    level_data['t_cluster_metrics'] = t_Cluster_Metrics(level_data, t_references_d, beta_l)
    if 'children_clusters' in level_data.keys():
        for cluster in level_data['children_clusters']:
            level_data['children_clusters'][cluster] = c_Metric_Recursion(level_data['children_clusters'][cluster], t_references_d, beta_l)
    return level_data