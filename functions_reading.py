import igraph

def read_Any(filename, encoding=None, errors=None):
    """Reads a file
    
    Parameters
    ----------
    filename : str
        Name of the file
        
    encoding : str, optional
        Parameter of open()
        
    errors : str, optional
        Parameter of open()

    Returns
    -------
    read_string : str
        The file as a string
    """
    file = open(filename, 'r', encoding=encoding, errors=errors)
    read_string = file.read()
    file.close()
    return read_string

def p_Tab_Delimited(filename, encoding=None, errors=None):
    """Parse tab delimited file

    Parameters
    ----------
    filename : str
        Name of the file. The columns in the file must be tab-delimited.
        
    encoding : str, optional
        Parameter of read_Any().
        
    errors : str, optional
        Parameter of read_Any().
        
    Returns
    -------
    parsed_string : list of list
        The file as a list of lists of strings, where the first level is the rows and the second level is the columns
    """
    read_string = read_Any(filename, encoding=encoding, errors=errors)
    parsed_string = [row.split('\t') for row in read_string.split('\n')] #  Create list of lists like file[rows[columns]]
    while parsed_string[-1] == ['']: #  Remove lingering line breaks
        parsed_string = parsed_string[:-1]
    return parsed_string

def parse_2_Level_D(tab_delimited, i_lvl_1=0, i_lvl_2=1, i_lvl_3=2):
    """Parse a two level dictionary

    Parameters
    ----------
    tab_delimited : list of list
        List of lists

    Returns
    -------
    d : dict of dict of list
    """
    d = {}
    for row in tab_delimited:
        lvl_1 = row[i_lvl_1]
        lvl_2 = row[i_lvl_2]
        lvl_3 = row[i_lvl_3]
        if lvl_1 not in d:
            d[lvl_1] = {}
        if lvl_2 not in d[lvl_1]:
            d[lvl_1][lvl_2] = []
        d[lvl_1][lvl_2].append(lvl_3)
    return d

def parse_Network(tab_delimited):
    """Parse the network

    Parameters
    ----------
    tab_delimited : list of list
        List of lists of strings, where the first level is the rows and the second level is the columns.
        Each row contains the network id of two nodes, and each pair represents an edge. The row does not includes the weight.
        
    Returns
    -------
    network : list of tuple
        The first level is a network edge, and the second level is the network id of the nodes in the edge.

    Notes
    -------
    The purpose of the function is to represent the nework using Int and Tuple data structures, which
    saves memory and is compatible with the igraph.Graph().TupleList() function.
    """
    network = set()
    for row in tab_delimited:
        n_1 = int(row[0])
        n_2 = int(row[1])
        edge = (n_1, n_2)
        network.add(edge)
    return network

def create_Igraph_Network(network):
    """Creates an Igraph representation of the network

    Parameters
    ----------
    network : list of tuple
        The first level is a network edge, and the second level is the network id of the nodes in the edge.
        
    Returns
    -------
    ig_network : igraph.Graph object
        Igraph representation of the network with edge weight = 1

    Notes
    -------
    Requires the igraph module.
    The purpose of the function is to add weights to the network so the connections dictonary can be
    latter created from the cluster_graph function.
    """
    ig_network = igraph.Graph().TupleList(network)
    ig_network.es['weight'] = 1
    return ig_network