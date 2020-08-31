import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import networkx as nx

import processing
import network

import warnings
warnings.filterwarnings("ignore")

overlapped_data = processing.fake_data(n = 500, course_dev = 20, n_classes = 10, major_range=range(0,200,10))
overlapped_data.head()

majors = sorted(list(overlapped_data.major.unique()))

major2colleges = {}
for major in majors:
    if major <= 190: major2colleges[major] = 1
    if major >= 200 and major <= 400: major2colleges[major] = 2
    if major >= 400 and major <= 600: major2colleges[major] = 3
    if major >= 600 and major <= 800: major2colleges[major] = 4
    if major >= 800 and major <= 1000: major2colleges[major] = 5

# Assign colleges and sort by college
assigned_colleges = []
for index, row in overlapped_data.iterrows():
    assigned_college = major2colleges[row['major']]
    assigned_colleges.append(assigned_college)
overlapped_data['college'] = assigned_colleges

#overlapped_data = overlapped_data.sort_values(['major','college'])
overlapped_data = overlapped_data.sort_values(['major'])

student_list = list(overlapped_data.student.unique())

# Get student-student weighted edgelist
partition, g = network.bipartite_to_projection(overlapped_data, name = 'heatmap_test', col1 = 'student', col2 = 'course')
A = nx.to_numpy_matrix(g, nodelist = student_list)

fig = go.Figure(data=go.Heatmap(z = A))
fig.show()