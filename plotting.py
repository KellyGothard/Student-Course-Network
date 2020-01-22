import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import comm_plot as cp
from community import induced_graph
from networkx.algorithms import approximation as approx
import processing as pss
from itertools import count
import numpy as np
import matplotlib.colors as colors


def dict_to_hist(d,column,grouping = None):
    plt.hist(d.values())
    plt.savefig('images/'+column+'_hist.png')
    plt.close()
    

def descriptives(G,grouping = None):
    degree = nx.degree_histogram(G)
    plt.bar(x = range(len(degree)), height = degree)
    plt.savefig('images/degree_hist.png')
    plt.close()
    
    neighbor_degree = nx.average_neighbor_degree(G)
    dict_to_hist(neighbor_degree,'neighbor_degree')
    degree_conn = nx.average_degree_connectivity(G)
    dict_to_hist(degree_conn,'degree_conn')
    
    
def pairwise_conn_dist(pairwise_conn, name):
    connlist = []
    for subdict in pairwise_conn.values():
        avgconn = sum(list(subdict.values()))/len(subdict.values())
        connlist.append(avgconn)
    
    plt.figure(figsize=(8,12)) 
    plt.title(name + ' Pairwise Connectivity Distribution')
    plt.xlabel('Connectivity')
    plt.ylabel('Count')
    plt.hist(connlist)
    plt.savefig(name+'_pairwiseconn_dist.png')
    plt.close()    
    
    plt.figure(figsize=(8,12)) 
    plt.title('Distribution of Min Removed Nodes to Disconnect Pair')
    temp = pd.DataFrame(connlist,columns = ['pairwise_conn'])
    temp = temp.reset_index()
    temp["rank"] = temp['pairwise_conn'].rank(method = 'average',ascending = False) 
    temp = temp.sort_values(by = ['index'],ascending = False)
    plt.scatter(y = temp['pairwise_conn'],x = temp['rank'],alpha = 0.7)
    plt.xlabel('Rank')
    plt.ylabel('Count')
    plt.savefig(name+'_pairwiseconn_zipf.png')
    plt.close()

    
def bipartite_plot(B, n1, name):
    node_color = []
    for node in B.nodes(data=True):
        if node[1]['bipartite'] == 0:
            node_color.append('peachpuff')
        else:
            node_color.append('lightcyan')
    
    pos = nx.drawing.layout.bipartite_layout(B, set(n1))  
    plt.figure(figsize=(8,12))      
    plt.axis('off')
    nx.draw_networkx(B,node_size = 4, with_labels = False, 
                     node_color = node_color, width = 0.1, 
                     edge_color = 'black', pos = pos, font_size = 7, alpha = 0.7)
#    nx.draw_networkx(B,node_size = 600, with_labels = True, 
#                     node_color = node_color, width = 2, 
#                     edge_color = 'black', pos = pos, font_size = 18)
#    ax = plt.gca() # to get the current axis
#    ax.collections[0].set_edgecolor("#000000") 
    plt.savefig(name+'_bipartite.png')
    plt.close()

    
def projection_plot(l, partition, name):  
    
    plt.figure(figsize=(14,16))
    plt.axis('off')
    
    pos = nx.spring_layout(l,k = 0.15)
    nx.draw_networkx(l,node_size = 4, with_labels = False, 
                     node_color = 'blue', edge_color = 'black',
                     width = 0.8, pos = pos, alpha = 0.7)
    
#    pos = nx.spring_layout(l, k = 2.5)
#    nx.draw_networkx(l,node_size = 3500, with_labels = True, 
#                     node_color = 'peachpuff', edge_color = 'black',
#                     width = 2, pos = pos, font_size = 48, alpha = 0.7)
    
#    ax = plt.gca() # to get the current axis
#    ax.collections[0].set_edgecolor("#000000") 
    plt.savefig(name+'_projection.png')
    plt.close()
    
    
    plt.figure(figsize=(14,16))
    plt.axis('off')
    c = cp._color_nodes(l,partition,0)
    s = cp._size_nodes(l,partition, 2)
    nx.draw_networkx(l,node_size = s, with_labels = False, 
                     node_color = c, edge_color = 'black',
                     width = 0.1, pos = pos, alpha = 0.7)
#    ax = plt.gca() # to get the current axis
#    ax.collections[0].set_edgecolor("#000000") 
    plt.savefig(name+'_communities_projection.png')
    plt.close()
    
    
    plt.figure(figsize=(14,16))
    plt.axis('off')
    pairwise_conn = approx.all_pairs_node_connectivity(l)
    avg_conn_dict = pss.get_avg_conn_from_pairwise(pairwise_conn)
    nx.set_node_attributes(l, avg_conn_dict, 'avg_connectivity')
    
    cmap = plt.get_cmap('Purples')
    cmap = truncate_colormap(cmap, 0.2, 0.9)
    groups = set(nx.get_node_attributes(l,'avg_connectivity').values())
    mapping = dict(zip(sorted(groups),count()))
    nodes = l.nodes()
    colors = [mapping[l.node[n]['avg_connectivity']] for n in nodes]
    nc = nx.draw_networkx(l, pos = pos, nodelist=nodes, node_color=colors, 
                                with_labels=False, node_size=4, cmap=cmap, 
                                alpha = 0.7, edge_color = 'black', width = 0.1)

#    nc = nx.draw_networkx(l, pos = pos, nodelist=nodes, node_color=colors, 
#                                with_labels=True, node_size=3500, cmap=cmap, 
#                                alpha = 0.7, edge_color = 'black', width = 2, font_size = 48)
#    plt.colorbar(nc)
#    ax = plt.gca() # to get the current axis
#    ax.collections[0].set_edgecolor("#000000") 
    plt.savefig(name+'_connectivity_projection.png')
    plt.close()
    


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap


def color_projection(l, partition, name):
#    pos = cp.community_layout(l, partition)
    pos = nx.spring_layout(l, k = 1.4)
    min_comm_size = cp.get_top_comm_len(partition, -1)
#    print('MIN COMM SIZE: '+str(min_comm_size))
    
#    c = cp._color_nodes(l,partition,min_comm_size)
#    s = cp._size_nodes(l,partition, 2)
#    plt.figure(figsize=(18,22))
#    nx.draw(l, pos, node_color = c, node_size = s, width = 0.3, alpha = 0.6)
    print(s)
    plt.figure(figsize=(18,22))
    nx.draw(l, pos, node_color = c, node_size = s, with_labels = True)
    plt.savefig(name+'_comms_projection.png')
    plt.close()

    
def induced_graph_viz(l, partition, partition_df, name):
    partition_df = partition_df.reset_index()
    partition_df = partition_df.groupby([0]).count()
    print(partition_df.head())
    partition_df = partition_df.reset_index()
    print(partition_df.head())
    partition_df.columns = ['community','nodecount']
    # Induced network of communities
    ind = induced_graph(partition, l)
    node_size = []
    for comm_node in ind.nodes:
        size = partition_df[partition_df['community'] == comm_node]['nodecount'].values[0]
        if size == 1:
            node_size.append(0)
        else:
            node_size.append(size**2)
            
    plt.figure(figsize=(14,16))
    nx.draw(ind,node_size = node_size, alpha = 0.7)
    plt.savefig(name+'_induced_projection.png')
    plt.close()
    
    return ind