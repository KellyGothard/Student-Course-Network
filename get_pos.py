
############################# Imports #############################

import pandas as pd
import argparse
import networkx as nx
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
                        help='directory that data lives in',
                        required=True,
                        default=None,
                        type=str)
    parser.add_argument('-t',
                        '--timechunk',
                        help='day to use',
                        required=True,
                        default=None,
                        type=str)
    return parser.parse_args()

def read_df(path,timechunk):
    # Add to this function once you find out more about the dataset
    if timechunk == 'all':
        df = pd.read_csv(str(path))
    else:
        pass
        #only read time chunk - unsure if its all in one file or not-tbd
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
    
def get_bip_proj(df,timechunk):
        
        n1,n2,edgelist = create_edgelist(df)   
        
        B = nx.Graph()
        B.add_nodes_from(set(n1), bipartite=0)
        B.add_nodes_from(set(n2), bipartite=1)
        B.add_weighted_edges_from(edgelist)
        
        l=bipartite.weighted_projected_graph(B,n1)
        plt.axis('off')
        
        pos = nx.spring_layout(l,k = 0.17)
        path = 'projection_pos.sav'
        outfile  = open(path,'wb')
        pickle.dump(pos,outfile)

def main():
    args = make_args()
    
    path = args.datadir
    timechunk = args.timechunk

    df = read_df(path,timechunk)
    get_bip_proj(df,timechunk)

if __name__=="__main__":
    main()