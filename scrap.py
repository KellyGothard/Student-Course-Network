import processing as prcss
import network as nwk
import plotting as p
import matplotlib.pyplot as plt


#for i in range(5):
name = 'test_big'
df = prcss.fake_data(n = 500, course_dev = 10, major_range = range(0,1000,10))
partition, projection = nwk.bipartite_to_projection(df, name = name, b_plot = True, l_plot = True, color_l_plot = False, induced = False)
#    nwk.measure_connectivity(projection, name = name, plots = True)

#for i in range(len(partition)-1):
#    l_filter = prcss.filter_l(projection, by = 'partition', partition = partition, partition_counter = i)
#    if len(l_filter.nodes) > 10:
#        print('Community '+str(i)+': \n')
#        nwk.measure_connectivity(l_filter, name = 'test', plots = True)
#


#    plt.hist(['course'],bins = len(df['course'].unique()))
#    plt.savefig('images/course_dist.png')