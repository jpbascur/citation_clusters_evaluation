import copy

def join_Clusters(clu_d, con_d, n_desired, resolution): # No more need for the resolution argument, discontinue in the future
    """Creates dictionary of joined clusters

    Parameters
    ----------
    clu_d : dict of tuple
        Dictionary where the first level is the name of the cluster and the second level is the list of the name of the nodes in the cluster.
    
    con_d: dict of dict of int
        Dictionary where the first level is the name of a given cluster, the second level is the name of another given cluster and the third level
        is the number of edges between the clusters.
    
    n_desired: int
        How many clusters you want to have after the joining process.
    
    resolution: float
        Resolution to be used in the Leiden algorithm clustering. It is used to calculate the score of the connections between clusters.
    
    Returns
    -------
    merge_dict: dict of dict
        Dictionary with the output of the merging.
        Keys:
        
        jclu_d: dict of tuple
            Dictionary where the first level is the name of the cluster and the second level is the list of the name of the nodes in the cluster.
            The clusters contain the nodes after mergin. The number of cluster is the desired number of clusters (n_desired).
        
        jrem_d: dict of tuple
            Dictionary where the first level is the name of the cluster and the second level is the list of the name of the nodes in the cluster.
            The clusters contain the nodes after mergin. When a cluster can't be merged, it is placed in this dictionary. The conditions for not merging a
            cluster are: It is not in the connections dict or the number of connections to other clusters sum 0.
        
        jcon_d: dict of dict
             Dictionary where the first level is the name of a given cluster, the second level is the name of another given cluster and the third level
            is the number of edges between the clusters. It contains the connections between the merged clusters. All the clusters are included, and if
            they have no connections, then the connections number is 0.

    Notes
    -------
    Requires de copy module.
    The purpose of the function is to merge the clusters until you have a desired number of clusters.
    The merging process is:
        1- If you have enought clusters, stop.
        2- Identify the smallest cluster.
        3- Calculate the connectivity score between the smallest cluster and the other clusters.
        4- Merge the smallest cluster with the cluster with the best connectivity score.
        5- Go to step 1.
    There are 2 optimized steps in this function:
        A- Identify the smallest cluster: To identify the smallest cluster, I sort a list of the sizes of the clusters. However, the size of the clusters
        changes after merging, so I have create a list of the sizes of the clusters and sort it after each merging. The optimization is that most of the 
        time the smallest cluster of the list will be the same before and after merging. This happens because the clusters usually merge with some of the
        bigger clusters, therefore the size of the smaller clusters tend to not change. This is relevant because the vast mayority of the clusters are very
        small. I take advantage if this fact in the get_Smallest_Cluster function. It uses te ranking and jclu_s variables to chec if the size of the cluster
        to merge is the same since the last time the list was sorted. Because the clusters can't get smaller, the fact that the cluster to merge is the same
        size as the last time the list was sorted means that it is time to merge the cluster to merge. If the cluster to merge is not of the same size, it
        meanse that there may be another smaller cluster in the list and so the list of clusters sizes has to be created again and sorted to find the smallest
        cluster. This list is now the one that will be used in the following evaluations of the cluster to merge.
        B- Calculate the connectivity score between the smallest cluster and the other clusters: I already calculated the number of conections between 
        the clusters once in the con_d variable. Therefore, to not calculate the number of conections again, I add the conections with the other clusters of 
        the smaller merged to the connections with the other clusters of the bigger merged cluster. I have to be carfull to not add self-connections.
    c_m: Name of the cluster to merge
    c_b: Name of the cluster with the best score
    c_m_c: Name of a given cluster that is also conected to c_m
    jclu_s: Dictionary of the size of the clusters. The purpose of this variable is to save the size of the clusters so to not calculate them again each time they are needed.
    """
    jclu_d = copy.deepcopy(clu_d)
    jcon_d = copy.deepcopy(con_d)
    jrem_d = {}
    jclu_s = {c: len(jclu_d[c]) for c in jclu_d}  # clusters size list, used for finding the smallest cluster in an optimized way, see get_Smallest_Cluster function
    ref_jclu_s = dict_As_Sorted_Tuples(jclu_s) # Reference size list, used for finding the smallest cluster in an optimized way, see get_Smallest_Cluster function
    while len(jclu_d) > n_desired:  # Main loop, stops once you have the number of desired clusters
        ref_jclu_s, c_m = get_Smallest_Cluster(ref_jclu_s, jclu_s)  # Which is the smallest cluster? (Optimized)
        if c_m in jcon_d:  # If the cluster to merge is in the connections dictionary, procede, else, add the cluster to merge to the rem_d
            score_d = {}
            for c_m_c in jcon_d[c_m]:
                n_con = jcon_d[c_m][c_m_c]
                if n_con != 0:  # The importance of this line is that merging with no conections may have better scores than mergins with some conections, and I want to avoid that by omiting clusters with no conections
                    score_d[c_m_c] = get_Merging_Resolution(n_con, jclu_s[c_m], jclu_s[c_m_c])
            if len(score_d) != 0:  # If the cluster to merge has any connection to the other clusters, procede, else, add the cluster to merge to the rem_d
                c_b = max_Key_By_Value(score_d)
                jclu_d, jclu_s, jcon_d = upd_Merge(c_m, c_b, jclu_d, jclu_s, jcon_d)  # Merge the clusters
            else:
                jclu_d, jclu_s, jcon_d, jrem_d = upd_Remove(c_m, jclu_d, jclu_s, jcon_d, jrem_d)  # This line removes the cluster
        else:
            jclu_d, jclu_s, jcon_d, jrem_d = upd_Remove(c_m, jclu_d, jclu_s, jcon_d, jrem_d)  # This line removes the cluster
        del(ref_jclu_s[0])  # Remove the cluster from the ranking list
    jcon_d = clean_Con_D(jcon_d, jclu_d)
    merge_dict = {'jclu_d': jclu_d, 'jrem_d': jrem_d, 'jcon_d': jcon_d}
    return merge_dict

def upd_Remove(c_m, jclu_d, jclu_s, jcon_d, jrem_d):
    """Updates the dictionaries when you have to remove a cluster

    Parameters
    ----------
    c_m : int
        Name of the cluster to merge
    
    jclu_d: dict of tuple
        Dictionary of clusters merged and clusters to merge where the first level is the name of the cluster and the second level
        is the list of the name of the nodes in the cluster.
        
    jclu_s: dict of int
        Dictionary of the size of the clusters

    jcon_d: dict of dict
        Dictionary where the first level is the name of a given cluster, the second level is the name of another given cluster and the third level
        is the number of edges between the clusters.
        
    jrem_d: dict of tuple
        Dictionary of removed clusterswhere the first level is the name of the cluster and the second level is the list of the name 
        of the nodes in the cluster.
    
    Returns
    -------
    jclu_d: dict of tuple
        Updated jclu_d parameter.
        
    jclu_s: dict of int
        Updated jclu_s parameter.
    
    jcon_d: dict of dict
        Updated jcon_d parameter.
    
    jrem_d: dict of tuple
        Updated jrem_d parameter (c_m cluster name and nodes added).
        
    Notes
    -------
    It removes the values of c_m from jclu_s and jclu_d, but before removing the values of c_m from jcon_d it checks if the c_m exists in jcon_d. It also removes the c_m conection from the value of other clustes conected to c_m.
    c_m_c: Name of a given cluster that is also conected to c_m
    """
    jrem_d[c_m] = jclu_d[c_m]
    del(jclu_s[c_m])
    del(jclu_d[c_m])
    if c_m in jcon_d:
        for c_m_c in jcon_d[c_m]:
            del(jcon_d[c_m_c][c_m]) # Remove c_m conection from the value of c_m_c
        del(jcon_d[c_m])  # Remove c_m value
    return jclu_d, jclu_s, jcon_d, jrem_d

def upd_Merge(c_m, c_b, jclu_d, jclu_s, jcon_d):
    """Updates the dictionaries when you have to merge a cluster

    Parameters
    ----------
    c_m : int
        Name of the cluster to merge
        
    c_b : int
        Name of the cluster with the best conectivity score
    
    jclu_d: dict of tuple
        Dictionary of clusters merged and clusters to merge where the first level is the name of the cluster and the second level
        is the list of the name of the nodes in the cluster.
        
    jclu_s: dict of int
        Dictionary of the size of the clusters

    jcon_d: dict of dict
        Dictionary where the first level is the name of a given cluster, the second level is the name of another given cluster and the third level
        is the number of edges between the clusters.

    Returns
    -------
    jclu_d: dict of tuple
        Updated jclu_d parameter.
        
    jclu_s: dict of int
        Updated jclu_s parameter.
    
    jcon_d: dict of dict
        Updated jcon_d parameter.
    """
    jclu_d = merge_Clu_D(c_m, c_b, jclu_d)
    jclu_s = merge_Clu_S(c_m, c_b, jclu_s)
    jcon_d = merge_Con_D(c_m, c_b, jcon_d)
    return jclu_d, jclu_s, jcon_d

def merge_Clu_D(c_m, c_b, jclu_d):
    """Update jclu_d so that c_m and c_b are merged

    Parameters
    ----------
    c_m : int
        Name of the cluster to merge
        
    c_b : int
        Name of the cluster with the best conectivity score
    
    jclu_d: dict of tuple
        Dictionary of clusters merged and clusters to merge where the first level is the name of the cluster and the second level
        is the list of the name of the nodes in the cluster.

    Returns
    -------
    jclu_d: dict of tuple
        Updated jclu_d parameter.
    """
    jclu_d[c_b].update(jclu_d[c_m])
    del(jclu_d[c_m])
    return jclu_d

def merge_Clu_S(c_m, c_b, jclu_s):
    """Update jclu_s so that c_m and c_b are merged

    Parameters
    ----------
    c_m : int
        Name of the cluster to merge
        
    c_b : int
        Name of the cluster with the best conectivity score
    
    jclu_s: dict of int
        Dictionary of the size of the clusters

    Returns
    -------
    jclu_s: dict of tuple
        Updated jclu_s parameter.
    """
    jclu_s[c_b] += jclu_s[c_m]
    del(jclu_s[c_m])
    return jclu_s

def merge_Con_D(c_m, c_b, jcon_d):
    """Update jclu_s so that c_m and c_b are merged

    Parameters
    ----------
    c_m : int
        Name of the cluster to merge
        
    c_b : int
        Name of the cluster with the best conectivity score
    
    jcon_d: dict of dict
        Dictionary where the first level is the name of a given cluster, the second level is the name of another given cluster and the third level
        is the number of edges between the clusters.

    Returns
    -------
    jcon_d: dict of tuple
        Updated jcon_d parameter.
        
    Notes
    -------
    c_m_c:  Name of a given cluster that is also conected to c_m
    """
    for c_m_c in jcon_d[c_m]:  # Remove all conections (c_m_c to c_m), and add that value to the conections (c_b to c_m_c)
        if c_m_c != c_b:  # This prevents the cluster for creating a conection with itself.
            if c_m_c not in jcon_d[c_b]:  # If the conection does not already exists, create it
                jcon_d[c_b][c_m_c] = 0
                jcon_d[c_m_c][c_b] = 0
            jcon_d[c_b][c_m_c] += jcon_d[c_m][c_m_c]  # Add the value of the conection (c_m to c_m_c) to the conection (c_b to c_m_c)
            jcon_d[c_m_c][c_b] += jcon_d[c_m][c_m_c]  # Same as above
        del(jcon_d[c_m_c][c_m])  # Remove all conections (c_m_c to c_m)
    del(jcon_d[c_m])   # Remove the conections (c_b to any)
    return jcon_d

def get_Smallest_Cluster(ref_jclu_s, jclu_s):
    """Get the smallest cluster in an optimized way

    Parameters
    ----------
    ref_jclu_s : list of tuples
        Ordered list of tuples of (cluster name,  cluster size), serves as references for jclus_s. The first tuple is the smallest one.
        
    jclu_s : dict of int
        Dictionary of the size of the clusters

    Returns
    -------
    out_ref_jclu_s:  list of tuples
        Updated ref_jclu_s parameter (or the original one if nothing changed).
    
    out_c_m: int
        Name of the cluster to merge
        
    Notes
    -------
    To optimize the proces, the function tries to find the smallest cluster without sorting the sizes in jclu_s.
    To do this, it checks if the size of the cluster to merge in jclu_s is the same as it was the last time the list was sorted (i.e. ref_jclu_s)
    If it is, then there is no need to sort the list again. Otherwise, it sortes again and upgrades the refference list.
    """
    ref_c_m, ref_c_size = ref_jclu_s[0]  # Get the smallest cluster size and name acording to the reference cluster sizes list
    c_size = jclu_s[ref_c_m]  #  Get the size of the cluster from the clusters sizes dict
    if c_size == ref_c_size:  #  If the size of the cluster from the actuall cluster list is the same as the size of that cluster in the cluster list, then that is the cluster to merge, if not, you have you sort the list again to find the cluster to merge
        out_ref_jclu_s = ref_jclu_s
    else:
        out_ref_jclu_s = dict_As_Sorted_Tuples(jclu_s)
    out_c_m = out_ref_jclu_s[0][0]
    return out_ref_jclu_s, out_c_m

def get_Merging_Resolution(n_con, c_1_size, c_2_size):
    """Get the resolution at which the change in the clustering score after merging the clusters is 0

    Parameters
    ----------
    n_con : int
        Number of conections between the clusters
        
    c_1_size : int
        Size of one cluster
        
    c_2_size : int
        Size of the other cluster

        
    Returns
    -------
    resolution:  float
        The resolution at which the chnage in score is 0
        
    Notes
    -------
    This is the merging technique that uses the Leiden algorithm. You should merge the pairs of clusters where the resolution is the highest.
    The reason is that the highest resolution will be the closest one to the resolution that you are already using. The merging resolution will be
    lower than the resolution you are already using because otherwise you would had already merged the clusters.
    """
    pos_n_con = c_1_size*c_2_size # All the positble pairs of nodes in the new cluster
    resolution = n_con/pos_n_con
    return resolution

def get_Score(n_con, c_1_size, c_2_size, resolution): # Discontinued use in the current pipeline
    """Get the change in the clustering score after merging the clusters

    Parameters
    ----------
    n_con : int
        Number of conections between the clusters
        
    c_1_size : int
        Size of one cluster
        
    c_2_size : int
        Size of the other cluster
        
    resolution: float
        Resolution value of the Leiden algorithm
        
    Returns
    -------
    score:  float
        Change in the clustering score after merging the clusters
        
    Notes
    -------
    Returns the score, as used by the Leiden Algorihtm (https://onlinelibrary.wiley.com/doi/full/10.1002/asi.22748, equation 4).
    The score is calculated only for the new pairs of nodes that apear after merging the clusters. The non conected pairs add (-resolution) to the score,
    while connected pairs add (1-resolution) to the score.
    """
    pos_n_con = c_1_size*c_2_size # All the positble pairs of nodes in the new cluster
    score = n_con*(1-resolution) - (pos_n_con-n_con)*resolution  # This works the followin way: For each pair of nodes in the cluster, if they are conected then add (1-resolution), else add (0-resolution)
    return score

def clean_Con_D(jcon_d, jclu_d):
    """Makes a connection dictionary that only contains the joined clusters and and have conection values for all of them (i.e. a clean version of jcon_d)

    Parameters
    ----------
    jcon_d: dict of dict
        Dictionary where the first level is the name of a given cluster, the second level is the name of another given cluster and the third level
        is the number of edges between the clusters.
    
    jclu_d: dict of tuple
        Dictionary of clusters merged and clusters to merge where the first level is the name of the cluster and the second level
        is the list of the name of the nodes in the cluster.

    Returns
    -------
    cjcon_d: dict of dict
        Clean jcon_d.
        
    Notes
    -------
    This step is necesary so jcon_d can be used in follow up clusterings.
    """
    cjcon_d = {}
    for c_1 in list(jclu_d):  # Use the keys of jclu_d to make the keys in cjcon_d
        cjcon_d[c_1] = {}
        for c_2 in list(jclu_d):
            if c_1 != c_2:  # Make sure you are not anotation links from the cluster to itself
                if c_1 not in jcon_d:  # If the cluster is not in jcon_d, then anotate it in cjcon_d with conection value 0 to the other clusters
                    cjcon_d[c_1][c_2] = 0
                else:
                    if c_2 not in jcon_d[c_1]: # Same as above
                        cjcon_d[c_1][c_2] = 0
                    else:
                        cjcon_d[c_1][c_2] = jcon_d[c_1][c_2]
    return cjcon_d

def max_Key_By_Value(dictionary):
    """Find the maximum key in a dict acorting to its value

    Parameters
    ----------
    dictionary: dict
        A given dictionary

    Returns
    -------
    max_key: any
        The maximum key acorting to its value.
        
    Notes
    -------
    max_value: The maximum value of the dictionary
    """
    max_value = max([value for value in dictionary.values()])
    max_key = max([key for key in dictionary if dictionary[key] == max_value])
    return max_key

def dict_As_Sorted_Tuples(jclu_s):
    """Turns jclu_s into a sorted list of tuples

    Parameters
    ----------
    jclu_s : dict of int
        Dictionary of the size of the clusters

    Returns
    -------
    sorted_tuples: list of tuples
         Ordered list of tuples of (cluster name,  cluster size).

    """
    list_of_tuples = list(jclu_s.items())
    sorted_tuples = sorted(list_of_tuples, key=lambda x: x[1])
    return sorted_tuples