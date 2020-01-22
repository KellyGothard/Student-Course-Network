# Student-Course-Network Documentation

## scrap.py
A script for testing things out.  No specific use, other than a place to test functions from other scripts.

## processing.py

### df_from_csv(path = None, frac = 1)
Read a csv, specified via its path, into a pandas dataframe, option to take a sample using the frac attribute.

### create_edgelist(df, col1, col2)
Take in a pandas dataframe and 2 specified column names, create an edgelist to be fed into a bipartite network in networkx.  Function returns an edgelist (nx2 matrix) and a nodelist associated with each column.  

### fake_student(df, major_range, course_dev, semester_n, n_classes)
Create 1 'fake' student complete with a major, n courses, and a semester.  All values are encoded as integers (ranges can be toggled for increased overlap between students).  Function takes in a dataframe and appends rows associate with the new fake student to the dataframe.

### fake_data(n, major_range = range(0,1000,10), course_dev = 5, semester_n = 1, n_classes = 4):
A fake dataset of students, courses, majors, and semesters is created using the fake_student function.  An empty dataframe, initialized in this function, is populated with fake students.  The result is returned as a dataframe.

### filter_l(l, by, mindeg = 0, maxdeg = 9999999, partition = None, partition_counter = 0):
Function takes in a network and filters nodes by degree or by community.

### get_avg_conn_from_pairwise(pairwise_conn)
Takes in a list of dictionaries where each key is a node and each value is a list of the pairwise connectivity between the key node and all other nodes.  Function returns a dictionary of the average pairwise connectivity for each node in the network.
