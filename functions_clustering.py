import igraph
import random

def get_Partition_Class(ig_network, resolution, random_seed=0):
    """Creates an Igraph representation of the network

    Parameters
    ----------
    ig_network : igraph.Graph object
        Igraph representation of the network with edge weight = 1.
        
    resolution: float
        Resolution to be used in the Leiden algorithm clustering.
        
    random_seed: int, optional
        Random seed of the Leiden algorithm clustering.
        
    Returns
    -------
    partition : igraph.clustering.VertexClustering object
        Partition of the nodes into clusters acording to the Leiden algorithm. The clustering is hard-clustering and it can contain singletons.

    Notes
    -------
    Requires the igraph module.
    Requires the random module
    The purpose of the function is to fix the random seed of the Leiden algorihm so the results of the clustering
    become replicable.
    """
    igraph.set_random_number_generator(random)
    random.seed(random_seed)
    partition = ig_network.community_leiden(resolution_parameter=resolution)
    return partition

def c_Cluster_D(partition):
    """Creates clusters dictionary

    Parameters
    ----------
    partition : igraph.clustering.VertexClustering object.
        Partition of the nodes into clusters.

    Returns
    -------
    cluster_d : dict of tuple
        Dictionary where the first level is the name of the cluster and the second level is the list of the name of the nodes in the cluster.

    Notes
    -------
    The main purpose of this function is to get the name of the nodes.
    cluster_i = Is the cluster index obtained from enumerating the clusters list. I dont know another way of obtaining the cluster index. It becomes the de-facto cluster name.
    cluster_nodes_i = Cluster nodes indices list.
    node_i = Node index.
    """
    cluster_d = {}
    for cluster_i, cluster_nodes_i in enumerate(list(partition)):
        cluster_d[cluster_i] = set()
        for node_i in cluster_nodes_i:
            node_name = partition.graph.vs[node_i]['name']  # This is the critical part of the function
            cluster_d[cluster_i].add(node_name)
    return cluster_d

def c_Connections_D(partition):
    """Creates connections dictionary

    Parameters
    ----------
    partition : igraph.clustering.VertexClustering object
        Partition of the nodes into clusters.

    Returns
    -------
    con_d: dict of dict of int
        Dictionary where the first level is the index of a given cluster, the second level is the index of another given cluster and the third level
        is the number of edges between the clusters. It does not includes pairs of clusters with no conections. The dictionary anotates the number
        of edges for both orders of clusters (e.g. both conn_d[1][2] = 3 and conn_d[2][1] = 3). It does not anotates edges from a cluster to itself.

    Notes
    -------
    The function uses igraph.clustering.VertexClustering.cluster_graph() to efficienly obtain the number of edges between the clusters.
    The parameter cluster_graph(combine_edges=sum) sums the attributes of the edges. The atrribute of the edges is 'weight', and
    the value is '1'. Therefore, the attrribute 'weight' will tell you hom many edges there were originaly.
    The index of the clusters is the same as in the c_Cluster_D function output. It becomes the de-facto cluster name.
    c_1_i = Cluster 1 index
    c_2_i = Cluster 2 index
    """
    con_d = {}
    cluster_g = partition.cluster_graph(combine_edges=sum)  # This is the critical part of the function.
    for edge in cluster_g.es:
        c_1_i = edge.source
        c_2_i = edge.target
        n_conn = edge['weight']
        if c_1_i != c_2_i:  # Don't anotate conections from the cluter to itself.
            if c_1_i not in con_d:
                con_d[c_1_i] = {}
            if c_2_i not in con_d:
                con_d[c_2_i] = {}
            con_d[c_1_i][c_2_i] = n_conn
            con_d[c_2_i][c_1_i] = n_conn
    return con_d