
############################# Imports #############################

import pandas as pd
import argparse
import networkx as nx
import numpy as np
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt
from networkx.algorithms import community
import random
from community import community_louvain
from community import generate_dendrogram
from community import partition_at_level
from community import induced_graph
from networkx.algorithms import approximation as approx

def make_args():
    description = 'Generalized jobs submitter for PBS on VACC. Tailored to jobs that can be chunked based on datetime.' \
                  ' Scripts to be run MUST have -o output argument. \n Output will be saved in log files with the first 3' \
                  ' characters of args.flexargs and the start date for the job'
    parser = argparse.ArgumentParser(description=description,formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i',
                        '--inputdir',
                        help='input directory',
                        required=True,
                        type=str)
    parser.add_argument('-o',
                        '--outdir',
                        help='output directory (will be passed to args.script with -o argument)',
                        required=True,
                        type=str)
    parser.add_argument('-d',
                        '--datadir',
                        help='data directory (Student-Course-Network/data/edgelist)',
                        required=True,
                        default=None,
                        type=str)
    parser.add_argument('-s',
                        '--starttime',
                        help='semester to start (S1,S2,...,SN)',
                        required=False,
                        default=None,
                        type=str)
    parser.add_argument('-e',
                        '--endtime',
                        help='semester to end (S1,S2,...,SN)',
                        required=False,
                        default=None,
                        type=str)
    parser.add_argument('-f',
                        '--fraction',
                        help='fraction of data to use',
                        required=False,
                        default=None,
                        type=float)
    return parser.parse_args()

def read_df(path,starttime,endtime,frac):
    start = int(starttime[-1])
    end = int(endtime[-1])
    if start == end:
        path= str(path)+'S'+str(start)+'.csv'
        df = pd.read_csv(path,header = 0)
    else:
        r = list(range(start,end))
        df = pd.DataFrame(columns = ['student','course','major','semester'])
        for sem in r:
            path= str(path)+'S'+str(sem)+'.csv'
            print(path)
            semfile = pd.read_csv(path,skiprows = 0)
            df.append(semfile)
    df = df.sample(frac = frac)
    return df

def create_edgelist(df,col1,col2):
    nodelist1 = []
    nodelist2 = []
    edgelist = []
    for index, row in df.iterrows():
        node1 = row[col1]
        node2 = row[col2]
        nodelist1.append(node1)
        nodelist2.append(node2)
        edgelist.append([node1,node2])
    return nodelist1, nodelist2, edgelist

def comm_to_df(df,partition,colname):
    group = []
    for index,row in df.iterrows():
        s = row['student']
        for c in partition:
            if s in c:
                group.append(partition.index(c))
                break
    df[colname] = group
    return df


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
    pos_communities = nx.spring_layout(hypergraph, **kwargs)

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
        pos_subgraph = nx.spring_layout(subgraph, **kwargs)
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
        if length > 3:
            size = length**magnitude
            community_sizes[comm] = size
        else:
            community_sizes[comm] = 1
    
    for node in g.nodes(data=True):
        node_sizes.append(community_sizes[nodes_communities[node[0]]])

    return node_sizes
    
def get_bip_proj(df,starttime,endtime,n1,n2,edgelist,out):
    if starttime != endtime:
        timechunk = starttime
    else:
        timechunk = starttime + '-' + endtime  
    
    B = nx.Graph()
    B.add_nodes_from(set(n1), bipartite=0)
    B.add_nodes_from(set(n2), bipartite=1)
    B.add_edges_from(edgelist)
    
#    node_color = []
#    for node in B.nodes(data=True):
#        if node[1]['bipartite'] == 0:
#            node_color.append('blue')
#        else:
#            node_color.append('red')
#    
#    plt.axis('off')
#    pos = nx.drawing.layout.bipartite_layout(B, set(n2))
#    nx.draw_networkx(B,node_size = 3, with_labels = False, node_color = node_color, edge_color = 'black', width = 0.3, pos = pos)
#    plt.savefig(out+'bipartite.png')
#    plt.close()
    
    l=bipartite.weighted_projected_graph(B,n1) 
    
    return l

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
    
    return comm_length[topn]

def df_to_zipf(df,column,counter,dfname,loglog,out):
    counts = df.groupby([column]).count()
    counts["rank"] = counts[counter].rank(method = 'average',ascending = False) 
    counts = counts.sort_values(by = [counter],ascending = False)
    if loglog:
        plt.loglog(counts[counter],counts['rank'])
    else:
        plt.plot(counts[counter],counts['rank'])
    plt.title(str(dfname)+': Zipf of '+column)
    plt.xlabel('Rank')
    plt.ylabel('Count')
    plt.savefig(out+'zipf_'+str(dfname)+'_'+column+'.png')
    plt.close()
    
def measure_connectivity(G,out,grouping = None):
#    overall_conn = approx.node_connectivity(G)
#    print('Minimum number of nodes that must be removed to disconnect studets: '+str(overall_conn))
    pairwise_conn = approx.all_pairs_node_connectivity(G)
    plt.title('Distribution of Min Removed Nodes to Disconnect Pair')
    connlist = []
    for subdict in pairwise_conn.values():
        avgconn = sum(list(subdict.values()))/len(subdict.values())
        connlist.append(avgconn)
    temp = pd.DataFrame(connlist,columns = ['pairwise_conn'])
    temp = temp.reset_index()
    temp["rank"] = temp['pairwise_conn'].rank(method = 'average',ascending = False) 
    temp = temp.sort_values(by = ['index'],ascending = False)
    plt.scatter(y = temp['pairwise_conn'],x = temp['rank'],alpha = 0.7)
    plt.xlabel('Rank')
    plt.ylabel('Count')
    plt.savefig(out+'zipf_pairwiseconnrank.png')
    plt.close()
    
    avg_cluster = approx.average_clustering(G)
    print('Mean of the fraction of triangles that actually exist over all possible triangles in each neighborhood: '+str(avg_cluster))

def network_plots(l,partition,out,temp):
    # Projection colored and sized by communitu
    pos = community_layout(l, partition)
    min_comm_size = get_top_comm_len(partition, 3)
    print('MIN COMM SIZE: '+str(min_comm_size))
    c = _color_nodes(l,partition,min_comm_size)
    s = _size_nodes(l,partition,3)
    nx.draw(l, pos, node_color = c, node_size = s, width = 0.3, alpha = 0.7)
    plt.savefig(out+'02_comms_projection.png')
    plt.close()
    
    # Induced network of communities
    ind = induced_graph(partition, l)
    node_size = []
    for comm_node in ind.nodes:
        size = temp[temp['community'] == comm_node]['nodecount'].values[0]
        if size == 1:
            node_size.append(0)
        else:
            node_size.append(np.exp(size))
        
    nx.draw(ind,node_size = node_size, node_color = 'black', alpha = 0.7, width = 0.5)
    plt.savefig(out+'induced_projection.png')
    plt.close()
    
    pos = nx.spring_layout(l,k = 0.50)
    plt.axis('off')
    nx.draw_networkx(l,node_size = 7, with_labels = False, node_color = c, edge_color = 'black', width = 0.3, alpha = 0.7, pos = pos)
    plt.savefig(out+'projection.png')
    plt.close()   

def zipfs(df,temp,out):
    # Plot distribution of community sizes to assess quality of community detection    
    temp["rank"] = temp['nodecount'].rank(method = 'average',ascending = False) 
    temp = temp.sort_values(by = ['community'],ascending = False)
    plt.scatter(y = temp['nodecount'],x = temp['rank'],alpha = 0.7)
    plt.xlabel('Rank')
    plt.ylabel('Count')
    plt.savefig(out+'zipf_noderank.png')
    plt.close()
    
    df_to_zipf(df,'student','semester','fakedata',loglog=False,out=out)
    df_to_zipf(df,'course','semester','fakedata',loglog=False,out=out)
    df_to_zipf(df,'major','semester','fakedata',loglog=False,out=out)
    
def scatters(df,out):
    plt.scatter(x = df['student'],y = df['course'])
    plt.savefig(out+'studentcourse_scatter.png')
    plt.close()
    
    plt.scatter(x = df['student'],y = df['major'])
    plt.savefig(out+'studentmajor_scatter.png')
    plt.close()
    
    plt.scatter(x = df['major'],y = df['course'])
    plt.savefig(out+'studentmajor_scatter.png')
    plt.close()
    
def hists(df,out):
    plt.hist(df['major'])
    plt.savefig(out+'majorhist.png')
    plt.close()
    
    plt.hist(df['student'])
    plt.savefig(out+'studenthist.png')
    plt.close()
    
    plt.hist(df['course'])
    plt.savefig(out+'coursehist.png')
    plt.close()


def main():
    
    # Input args
    args = make_args()
    out = args.outdir
    path = args.datadir
    starttime = args.starttime
    endtime = args.endtime
    frac = args.fraction

    # Read in data as csv, get edgelist, get projection
    df = read_df(path,starttime,endtime,frac)
    print(len(df))
    n1,n2,edgelist = create_edgelist(df,'student','course')
    l = get_bip_proj(df,starttime,endtime,n1,n2,edgelist,out)
    measure_connectivity(l,out)
    
#    # Get communities at various levels
#    partitions = generate_dendrogram(l)
#    partition = partition_at_level(partitions,-1)
#
#    # Partition descriptives
#    print('NUMBER OF PARTITIONS: '+str(len(partitions)))
#    print('NUM ROWS: '+str(len(df)))
#    
#    # DF to track size of communities
#    temp = pd.DataFrame.from_dict(partition,orient = 'index')
#    temp = temp.reset_index()
#    temp = temp.groupby([0]).count()
#    temp = temp.reset_index()
#    temp.columns = ['community','nodecount']


    
if __name__=="__main__":
    main()
