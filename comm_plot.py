import networkx as nx
import random
from community import induced_graph
import numpy as np
import matplotlib.pyplot as plt

def community_layout(g, partition):
    """
    Compute the layout for a modular graph.

    Arguments:
    ----------
    g -- networkx.Graph or networkx.DiGraph instance
        graph to plot

    partition -- dict mapping int node -> int community
        graph partitions

    Returns:
    --------
    pos -- dict mapping int node -> (float x, float y)
        node positions
    """

    pos_communities = _position_communities(g, partition, scale=3.)

    pos_nodes = _position_nodes(g, partition, scale=1.)

    # combine positions
    pos = dict()
    for node in g.nodes():
        pos[node] = pos_communities[node] + pos_nodes[node]

    return pos

def _position_communities(g, partition, **kwargs):

    # create a weighted graph, in which each node corresponds to a community,
    # and each edge weight to the number of edges between communities
    between_community_edges = _find_between_community_edges(g, partition)

    communities = set(partition.values())
    hypergraph = nx.DiGraph()
    hypergraph.add_nodes_from(communities)
    for (ci, cj), edges in between_community_edges.items():
        hypergraph.add_edge(ci, cj, weight=len(edges))

    # find layout for communities
    pos_communities = nx.spring_layout(hypergraph, k = 10, **kwargs)

    # set node positions to position of community
    pos = dict()
    for node, c in partition.items():
        pos[node] = pos_communities[c]

    return pos

def _find_between_community_edges(g, partition):

    edges = dict()

    for (ni, nj) in g.edges():
        ci = partition[ni]
        cj = partition[nj]

        if ci != cj:
            try:
                edges[(ci, cj)] += [(ni, nj)]
            except KeyError:
                edges[(ci, cj)] = [(ni, nj)]

    return edges

def _position_nodes(g, partition, **kwargs):
    """
    Positions nodes within communities.
    """

    communities = dict()
    for node, c in partition.items():
        try:
            communities[c] += [node]
        except KeyError:
            communities[c] = [node]

    pos = dict()
    for ci, nodes in communities.items():
        subgraph = g.subgraph(nodes)
        pos_subgraph = nx.spring_layout(subgraph, k = 0.3, **kwargs)
        pos.update(pos_subgraph)

    return pos


def _color_nodes(g, partition, smallestcomm, **kwargs):
    """
    Colors nodes within communities.
    """
    communities = dict()
    nodes_communities = dict()
    community_colors = dict()
    node_colors = []
    for node, c in partition.items():
        try:
            communities[c] += [node]
        except KeyError:
            communities[c] = [node]
        nodes_communities[node] = c
    
    for comm in communities:
        if len(communities[comm]) > smallestcomm:
            color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
            community_colors[comm] = color
        else:
            community_colors[comm] = '#000000'
    
    for node in g.nodes(data=True):
        node_colors.append(community_colors[nodes_communities[node[0]]])
            
    return node_colors

def _size_nodes(g, partition, magnitude, **kwargs):
    """
    Sizes nodes within communities.
    """
    communities = dict()
    nodes_communities = dict()
    community_sizes = dict()
    node_sizes = []
    for node, c in partition.items():
        try:
            communities[c] += [node]
        except KeyError:
            communities[c] = [node]
        nodes_communities[node] = c
    
    for comm in communities:
        length = len(communities[comm])
        if length > 0:
            size = length**magnitude
            community_sizes[comm] = size
        else:
            community_sizes[comm] = 1
    
    for node in g.nodes(data=True):
        node_sizes.append(community_sizes[nodes_communities[node[0]]])

    return node_sizes

def get_top_comm_len(partition, topn):
    '''
    Returns integer of minimum number of items in a community
    for the top n communities
    '''
    communities = dict()
    for node, c in partition.items():
        try:
            communities[c] += [node]
        except KeyError:
            communities[c] = [node]
            
    comm_length = []
    for comm in communities:
        comm_length.append(len(communities[comm]))
    
    comm_length = list(set(comm_length))
    comm_length = sorted(comm_length)
    
    return comm_length[topn]