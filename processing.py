# IMPORTS
import pandas as pd
import random as rand



def df_from_csv(path = None, frac = 1):
    '''
    Read a csv, take a sample, get dataframe.
    '''
    
    df = pd.read_csv(path).sample(frac = frac)
    return df


def create_edgelist(df, col1, col2):
    '''
    Take in a dataframe and 2 specified columns, create an edgelist
    to be used with networkx.
    '''
    
    nodelist1 = list(df[col1].unique())
    nodelist2 = list(df[col2].unique())
    edgelist = []
    for index, row in df.iterrows():
        node1 = row[col1]
        node2 = row[col2]
        edgelist.append([node1,node2])
    return edgelist, nodelist1, nodelist2
    

def fake_student(df, major_range, course_dev, semester_n, n_classes):
    '''
    Create 1 'fake' student complete with a major, n courses, and a semester.
    All values are encoded as integers (ranges can be toggled for increased overlap
    between students).
    
    Function takes in a dataframe and appends rows associate with the new fake student
    to the dataframe.
    '''
    
    # Initialize student
    ## Generate student number
    if len(df)==0:
        studentnum = 1 + 10000
    else:
        studentnum = df.tail(1)['student'].values[0] + 1 + 10000

    ## Generate major number
    majornum = rand.choice(list(major_range))
    
    ## Generate course number
    coursenum = int(rand.uniform(majornum-course_dev,majornum+course_dev)//1)
    
    if majornum > max(list(major_range))//3 and majornum < max(list(major_range)) - max(list(major_range))//3:
        r = rand.random()
        if r < 0.5:
            coursenum = coursenum + (r*coursenum)//1
    
    ## Generate semester number
    semnum = rand.randint(1,semester_n)
    
    ## Add first student to dataframe
    temp = pd.DataFrame({'student':[studentnum],'major':[majornum],'course':[coursenum],'semester':[semnum]})
    df = pd.concat([df,temp])
    
    # Add n more classes associated with student
    for i in range(n_classes):
        ## Generate course number
        coursenum = int(rand.uniform(majornum-course_dev,majornum+course_dev)//1)
        if majornum > max(list(major_range))//3 and majornum < max(list(major_range)) - max(list(major_range))//3:
            r = rand.random()
            if r < 0.5:
                coursenum = coursenum + (r*coursenum)//1
        
        ## Check to see if student is already taking this course - try again
        prev_courses = df[df['student']==studentnum]['course'].values
        if coursenum in prev_courses:
            coursenum = int(rand.uniform(majornum-course_dev,majornum+course_dev)//1)
        
        ## Add to dataframe
        temp = pd.DataFrame({'student':[studentnum],'major':[majornum],'course':[coursenum],'semester':[semnum]})
        df = pd.concat([df,temp])
        
    return df


def fake_data(n, major_range = range(0,1000,10), course_dev = 5, semester_n = 1, n_classes = 4):
    '''
    A fake dataset of students, courses, majors, and semesters is created using the fake_student
    function.  An empty dataframe, initialized in this function, is populated with fake students.
    
    The result is returned as a dataframe.
    '''
    
    df = pd.DataFrame(columns=['student','major','course','semester'])
    for i in range(n):
        df = fake_student(df, major_range, course_dev, semester_n, n_classes)
        
        
    return df


def filter_l(l, by, mindeg = 0, maxdeg = 9999999, partition = None, partition_counter = 0):
    
    if by == 'degree':
        to_keep = []
        outdeg = l.degree()
        for (node,deg) in outdeg:
            if deg > mindeg and deg < maxdeg:
                to_keep.append(node)
                
        filtered_l = l.subgraph(to_keep)
        
    if by == 'partition':
        communities = dict()
        for node, c in partition.items():
            try:
                communities[c] += [node]
            except KeyError:
                communities[c] = [node]
        comms = list(communities.keys())
        to_keep = communities[comms[partition_counter]]
        filtered_l = l.subgraph(to_keep)
            
    return filtered_l


def get_avg_conn_from_pairwise(pairwise_conn):
    avg_conn_dict = {}
    for node in pairwise_conn:
        pairs = pairwise_conn[node]
        avg_conn = sum(pairs.values())/len(pairs.values())
        avg_conn_dict[node] = avg_conn
    return avg_conn_dict





