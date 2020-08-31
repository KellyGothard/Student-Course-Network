import random as rand
import pandas as pd

df = pd.DataFrame(columns=['student','major','course','semester'])

def add_student(df):
    if len(df)==0:
        studentnum = 1
    else:
        studentnum = df.tail(1)['student'].values[0] + 1
    majornum = rand.choice(list(range(0,1000,10)))
    coursenum = rand.normal(majornum-3,majornum+3)
    
    temp = pd.DataFrame({'student':[studentnum],'major':[majornum],'course':[coursenum],'semester':['S1']})
    df = pd.concat([df,temp])
    
    for i in range(4):
        coursenum = rand.normal(majornum-5,majornum+5)
        for i in range(5):
            prev_courses = df.tail(5)['course'].values
            if coursenum in prev_courses:
                coursenum = rand.normal(majornum-5,majornum+5)
                
        temp = pd.DataFrame({'student':[studentnum],'major':[majornum],'course':[coursenum],'semester':['S1']})
        df = pd.concat([df,temp])
        
    return df

for i in range(10000):
    df = add_student(df)

df.to_csv('fake_edgelistS1.csv')