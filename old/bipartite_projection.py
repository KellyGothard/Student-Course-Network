
############################# Imports #############################

import pandas as pd
import argparse
import networkx as nx
from networkx.algorithms import approximation as approx
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt
import pickle

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
    return parser.parse_args()

def read_df(path,starttime,endtime):
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
    print(df.head())
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
    
def get_bip_proj(df,starttime,endtime):
    if starttime != endtime:
        timechunk = starttime
    else:
        timechunk = starttime + '-' + endtime
    
    n1,n2,edgelist = create_edgelist(df,'student','course')   
    B = nx.Graph()
    B.add_nodes_from(set(n1), bipartite=0)
    B.add_nodes_from(set(n2), bipartite=1)
    B.add_edges_from(edgelist)
    
    l=bipartite.weighted_projected_graph(B,n1)
    try: pos = pickle.load(open('projection_pos.sav','rb'))
    except: pos = nx.spring_layout(l,k = 0.05)

    plt.axis('off')
    nx.draw_networkx(l,node_size = 2, with_labels = False, node_color = 'red', edge_color = 'black', width = 0.05, alpha = 0.4, pos = pos)
    plt.savefig('images/'+timechunk+'_projection.png')
    plt.close()
    
    return l
    

def measure_connectivity(G,grouping = None):
    overall_conn = approx.node_connectivity(G)
    print('Minimum number of nodes that must be removed to disconnect studets: '+str(overall_conn))
    pairwise_conn = approx.all_pairs_node_connectivity(G)
    plt.title('Distribution of Min Removed Nodes to Disconnect Pair')
    plt.hist(pairwise_conn.values())
    avg_cluster = approx.average_clustering(G)
    print('Mean of the fraction of triangles that actually exist over all possible triangles in each neighborhood: '+str(avg_cluster))

def descriptives(G,grouping = None):
    degree = nx.degree_histogram(G)
    plt.bar(x = range(len(degree)), height = degree)
    plt.savefig('images/degree_hist.png')
    plt.close()
    neighbor_degree = nx.average_neighbor_degree(G)
    dict_to_hist(neighbor_degree,'neighbor_degree')
    degree_conn = nx.average_degree_connectivity(G)
    dict_to_hist(degree_conn,'degree_conn')

def dict_to_hist(d,column,grouping = None):
    plt.hist(d.values())
    plt.savefig('images/'+column+'_hist.png')
    plt.close()
    

def main():
    args = make_args()
    
    path = args.datadir
    starttime = args.starttime
    endtime = args.endtime

    df = read_df(path,starttime,endtime)
    l = get_bip_proj(df,starttime,endtime)
#    descriptives(l)
    measure_connectivity(l)

if __name__=="__main__":
    main()
