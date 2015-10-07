# ScaleFreeTest.py

import igraph
import math
import random

m0 = 2
ex_v = m0
m = 1
N = 100

# initialize the graph with full connections
g = igraph.Graph.Full(m0)

print "Starting graph:"
print g
print ""

# begin adding vertices one at a time
for i in range(m0, N):
	g.add_vertices(1)	# the i-th vertex

	# determine prob of all potential connections
	p = [0.0 for x in range(0, ex_v)]
	tot_degree = 2 * len(g.get_edgelist())
	for k in range(0, ex_v):
		p[k] = 1.0 * g.degree(k) / tot_degree
		if k > 0:
			p[k] += p[k-1]

	# randomly generate m new connections
	r = random.random()
	
	# check all potential vertices for a match
	for j in range(0, ex_v):
		if r <= p[j]:
			# connect to node k2
			g.add_edges([(i, j)])
			break

	# update num existing c
	ex_v +=1


print g
print ""

print "Degree distribution:"
print g.degree_distribution()
print ""

avg_path_expected = math.log(N) / math.log(math.log(N))
print "Average path length (Expected: %1.2f)" % (avg_path_expected)
print g.average_path_length()

