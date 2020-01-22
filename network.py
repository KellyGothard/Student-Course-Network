import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms import bipartite
from community import generate_dendrogram
from community import partition_at_level
import pandas as pd
from networkx.algorithms import approximation as approx
import processing as pss
import plotting as p
import pprint
    
def bipartite_to_projection(df, name, col1 = 'student', col2 = 'course', b_plot = False, l_plot = False, color_l_plot = False, induced = False):
    
    edgelist, n1, n2 = pss.create_edgelist(df, col1, col2)
    
    n1 = sorted(n1)
    print(n1)
    n2 = sorted(n2)
    print(n2)

    B = nx.Graph()
    B.add_nodes_from(n1, bipartite=0)
    B.add_nodes_from(n2, bipartite=1)
    B.add_edges_from(edgelist)

    if b_plot:
        p.bipartite_plot(B, n1, name)

    l=bipartite.weighted_projected_graph(B, n1)
    partition = get_comms(l)
    
    temp = pd.DataFrame.from_dict(partition, orient = 'index')
    temp_save = temp.reset_index()
    temp_save.columns = ['node','community']
    temp_save.to_csv(name+'_community_members.csv')
    
    if l_plot:
        p.projection_plot(l, partition, name)
    
    if color_l_plot:
        p.color_projection(l, partition, name)
        
    if induced:
        induced = p.induced_graph_viz(l, partition, temp, name)
        measure_between_group_connectivity(induced, name, plots = True)

    return partition, l

    
def get_comms(l):
    partitions = generate_dendrogram(l)
    partition = partition_at_level(partitions,-1)
    return partition

    
def measure_connectivity(G, name = '', plots = False):
    overall_conn = approx.node_connectivity(G)
    print('Minimum number of nodes that must be removed to disconnect studets: '+str(overall_conn))
    pairwise_conn = approx.all_pairs_node_connectivity(G)
#    avg_conn_dict = pss.get_avg_conn_from_pairwise(pairwise_conn)
    avg_cluster = approx.average_clustering(G)
    print('Mean of the fraction of triangles that actually exist over all possible triangles in each neighborhood: '+str(avg_cluster))
    avg_cluster = approx.average_clustering(G)
    print('Mean of the fraction of triangles that actually exist over all possible triangles in each neighborhood: '+str(avg_cluster))
    
    if plots:
        p.pairwise_conn_dist(pairwise_conn, name)
        
        
def measure_between_group_connectivity(induced, name = '', plots = False):
    overall_conn = approx.node_connectivity(induced)
    print('Minimum number of nodes that must be removed to disconnect studets: '+str(overall_conn))
    pairwise_conn = approx.all_pairs_node_connectivity(induced)
    avg_cluster = approx.average_clustering(induced)
    print('Mean of the fraction of triangles that actually exist over all possible triangles in each neighborhood: '+str(avg_cluster))
    avg_cluster = approx.average_clustering(induced)
    print('Mean of the fraction of triangles that actually exist over all possible triangles in each neighborhood: '+str(avg_cluster))
    
    if plots:
        p.pairwise_conn_dist(pairwise_conn, name)
        
        
def measure_within_group_connectivity(partitioned, name = '', plots = False):
    overall_conn = approx.node_connectivity(partitioned)
    print('Minimum number of nodes that must be removed to disconnect studets: '+str(overall_conn))
    pairwise_conn = approx.all_pairs_node_connectivity(partitioned)
    avg_cluster = approx.average_clustering(partitioned)
    print('Mean of the fraction of triangles that actually exist over all possible triangles in each neighborhood: '+str(avg_cluster))
    avg_cluster = approx.average_clustering(partitioned)
    print('Mean of the fraction of triangles that actually exist over all possible triangles in each neighborhood: '+str(avg_cluster))
    
    if plots:
        p.pairwise_conn_dist(pairwise_conn, name)
        