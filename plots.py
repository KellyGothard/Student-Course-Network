
############################# Imports #############################
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import argparse
import imageio

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
                        required=False,
                        default=None,
                        type=str)
    parser.add_argument('-m',
                        '--imagedir',
                        help='image directory to create gif of communities',
                        required=False,
                        default=None,
                        type=float)
    return parser.parse_args()
    
def valid_date(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d")

    except ValueError:
        msg = "Invalid date format in provided input: '{}'.".format(d)
        raise argparse.ArgumentTypeError(msg)



########################## Read in Data ##########################

def read_df(path,timechunk):
    # Add to this function once you find out more about the dataset
    if timechunk == 'all':
        df = pd.read_csv(str(path))
    else:
        pass
        #only read time chunk - unsure if its all in one file or not-tbd
    return df

###################### Descriptives of Data ######################

def df_to_zipf(df,column,counter,dfname):
    user_counts = df.groupby([column]).count()
    user_counts["rank"] = user_counts[counter].rank(method = 'average',ascending = False) 
    user_counts = user_counts.sort_values(by = [counter],ascending = False)
    plt.loglog(user_counts[counter],user_counts['rank'])
    plt.title(str(dfname)+': Zipf of '+column)
    plt.xlabel('Rank')
    plt.ylabel('Count')
    plt.savefig('zipf_'+str(dfname)+'_'+column+'.png')
    plt.close()

def plots_to_gif(imagedir):
    images = []
    for image in imagedir:
        images.append(imageio.imread(image))
    imageio.mimsave('communities.gif', images)

def create_timeseries_groups(df):
    timeseries_groups = []
    for index,row in df.iterrows():
        timeseries_groups.append(datetime.strptime(row['datetime'],'%Y-%m-%d %H:%M:%S').replace(minute=0, second=0, microsecond=0))
    df['timeseries_groups'] = timeseries_groups
    return df

def timeseries(df,attribute):
    timeseries = pd.DataFrame(df.loc[df[attribute] == subreddit,:].groupby(['timeseries_groups']).count()['body'])
    if max(timeseries['body']) > 20:
        plt.plot(timeseries.index,timeseries['body'])
        plt.xlim(min(df['datetime']),max(df['datetime']))
        plt.title(subreddit)
        plt.savefig(subreddit+'_timeseries.png')
        plt.close()

def main():
    
    args = make_args()
    
    path = args.datadir
    sample = args.fraction
    imagedir = args.imagedir
                    
    df,health_df,nonhealth_df = read_df(path,sample)
    
    df_to_zipf(df,'author','body','allposts')
    df_to_zipf(df,'subreddit','body','allposts')    
    
    df_to_zipf(health_df,'author','body','healthposts')
    df_to_zipf(health_df,'subreddit','body','healthposts')
    df_to_zipf(nonhealth_df,'author','body','nonhealthposts')
    df_to_zipf(nonhealth_df,'subreddit','body','nonhealthposts')

    health_df = create_timeseries_groups(health_df)
        
    for subreddit in list(health_df.subreddit.unique()):
        timeseries(health_df,subreddit)
        
    plots_to_gif(imagedir)
    
    
            
if __name__=="__main__":
    main()
