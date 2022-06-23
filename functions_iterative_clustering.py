import functions_clustering as clustering
import functions_merging as merging

def level_Data(graph, resolution, clusters_per_level, t_references_d):
    """Create the dictionary of positive clusters
    
    Parameters
    ----------
    graph : igraph.Graph
        Graph over which do the clustering
        
    resolution : float
        Resolution of the clustering algorithm
        
    clusters_per_level : int
        Maximum number of clusters per branch per level (including the initial level).
        
    t_references_d : dict of set
        The key is the topic and the value is the set of references of the topic. The references are int type.
    
    Returns
    -------
    level_data : dict
        Dictionary with the data of the clustering solution of the current level.
    """
    partition = clustering.get_Partition_Class(graph, resolution)
    clu_d = clustering.c_Cluster_D(partition)
    con_d = clustering.c_Connections_D(partition)
    merging_data = merging.join_Clusters(clu_d, con_d, clusters_per_level, resolution)
    t_positive_clusters_d = t_Positive_Clusters_Dict(t_references_d, merging_data['jclu_d'])
    all_positive_clusters_id = all_Positive_Clusters_Id(t_positive_clusters_d)
    level_data = {'merging_data': merging_data, 't_positive_clusters_d': t_positive_clusters_d, 'all_positive_clusters_id': all_positive_clusters_id}
    return level_data

def t_Positive_Clusters_Dict(t_references_d, clu_d):
    """Create the dictionary of positive clusters

    Parameters
    ----------
    t_references_d : dict of set
        The key is the topic and the value is the set of references of the topic. The references are int type.
    
    clu_d : dict of set
        The key is the cluster id and the value is the set of nodes in the cluster. The nodes are int type.

    Returns
    -------
    t_positive_clusters_d : dict of dict
        The first key is the topic, the second key is the cluster id and the third key is the set of intersected documents.
        There are no recorded clusters with empty intersections in the dictionary.

    Notes
    -------
    The function intersects the references of each topic with the nodes of each cluster. If a cluster have no intersection,
    then it is not recorded in t_positive_clusters_d.
    """
    t_positive_clusters_d = {}
    for t in t_references_d:
        t_positive_clusters_d[t] = {}
        references_set = t_references_d[t]
        for c in clu_d:
            cluster_set = clu_d[c]
            intersection_set = references_set.intersection(cluster_set)
            if len(intersection_set) > 0:
                t_positive_clusters_d[t][c] = intersection_set
    return t_positive_clusters_d

def all_Positive_Clusters_Id(t_positive_clusters_d):
    """Create a set of positive clusters id

    Parameters
    ----------
    t_positive_clusters_d : dict of dict
        The first key is the topic, the second key is the cluster id and the third key is the set of intersected documents.
        There are no recorded clusters with empty intersections in the dictionary.

    Returns
    -------
    t_positive_clusters_d : dict of dict
        The first key is the topic, the second key is the cluster id and the third key is the set of intersected documents.
        There are no recorded clusters with empty intersections in the dictionary.
    """
    all_positive_clusters_id = set()
    for t in t_positive_clusters_d:
        for c in t_positive_clusters_d[t]:
            all_positive_clusters_id.add(c)
    return all_positive_clusters_id
    
def c_Clus_Recursion(parent_graph, resolution, parent_level, max_depth, clusters_per_level, t_references_d, resolution_factor, ITERATIONS_COUNT):
    """Create a set of positive clusters id

    Parameters
    ----------
    parent_graph : igraph.Graph
        Graph of the parent cluster.
    
    resolution : float
        Resolution of the clustering of the current level.
    
    parent_level : int
        Level of the parent cluster.
    
    max_depth : int
        Lowest level of the clustering
        
    clusters_per_level : int
        Maximum number of clusters.
        
    t_references_d : dict of set
        The key is the topic and the value is the set of references of the topic. The references are int type.
        
    resolution_factor : float
        Factor by which the value of the resolution increases at each level.

    Returns
    -------
    level_data : dict
        Dictionary with the data of the level.
        
    Notes
    -------
    The only parameters that change their value in each iteration is parent_graph, resolution, and parent_level.
    The parameters max_depth, clusters_per_level, t_references_d and resolution_factor are constant.
    The parameter parent_level is used to stop the iterations.
    """
    ITERATIONS_COUNT += 1
    level_data = level_Data(parent_graph, resolution, clusters_per_level, t_references_d)
    level_data['level'] = level = parent_level + 1
    if level < max_depth:
        assert (len(level_data['all_positive_clusters_id']) > 0), 'Level ' + str(level) + ' Iteration ' + str(ITERATIONS_COUNT) # Report if there are no positive clusters
        level_data['children_resolution'] = children_resolution = resolution*resolution_factor
        level_data['children_clusters'] = {}
        for cluster_id in level_data['all_positive_clusters_id']:
            cluster_nodes_l = level_data['merging_data']['jclu_d'][cluster_id]
            cluster_subgraph = create_Subgraph(parent_graph, cluster_nodes_l)
            level_data['children_clusters'][cluster_id], ITERATIONS_COUNT = c_Clus_Recursion(cluster_subgraph, children_resolution, level, max_depth, clusters_per_level, t_references_d, resolution_factor, ITERATIONS_COUNT)
    return level_data, ITERATIONS_COUNT

def create_Subgraph(grahph, nodes_l):
    """Create a subgraph

    Parameters
    ----------
    grahph : igraph.Graph
        Graph from which to create the subgraph.
    
    nodes_l : list
        List of the name of the nodes of the subgraph

    Returns
    -------
    subgraph : igraph.Graph
        Dictionary with the data of the level.
        
    Notes
    -------
    The name of the nodes is not the same as the index of the nodes. This functon transform the list of node names into a list of nodes indices
    (vertex_l, whose data type is igraph.VertexSeq but it is also an iterable list of indices) so it can be used in the grahph.subgrpah() function.
    """
    vertex_l = grahph.vs.select(name_in=nodes_l)
    subgraph = grahph.subgraph(vertex_l)
    return subgraph