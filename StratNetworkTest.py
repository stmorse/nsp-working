# StratNetworkTest.py

import igraph
import itertools
import math


def test_strat_nets(num_nodes, delta, cij, wij):
	
	all_g = []

	print "Testing all graphs size ", num_nodes
	print "Delta=%.2f, Cost=%.2f, Wij=%1.1f" % (delta, cij, wij)

	edge_list = list(itertools.combinations(range(0, num_nodes), 2))

	# add all permutations of network

	# first empty graph
	empty_g = igraph.Graph()
	empty_g.add_vertices(num_nodes)
	all_g.append(empty_g)

	# all graphs with edges
	for s in range(1, len(edge_list) + 1):
		eid_list = list(itertools.combinations(range(0,len(edge_list)), s))

		for el in eid_list:
			gn = igraph.Graph()
			gn.add_vertices(num_nodes)
			add_edges = [edge_list[a] for a in el]
			gn.add_edges(add_edges)
			all_g.append(gn)

	print "Total graphs: ", len(all_g)
	print ""

	# compute utility values for all graphs
	for g in all_g:
		total_value = 0
		for v in g.vs:
			dsum = 0
			csum = 0
			for n in g.vs:
				if v == n: continue
				spl = g.shortest_paths_dijkstra(v, n, None, "ALL")
				dsum += math.pow(delta, spl[0][0])
				if spl[0][0] == 1:
					csum += cij
			v["u"] = dsum - csum
			total_value += v["u"]
		g["value"] = total_value

	# compare efficiency of all graphs
	best_value = 0
	best_index = -1
	for k, g in enumerate(all_g):
		if g["value"] >= best_value:
			best_value = g["value"]
			best_index = k

	if best_value > 0 and best_index > -1:
		print "Efficient graph: "
		print "- es: ", all_g[best_index].get_edgelist()
		print "- ui: ", [round(u, 2) for u in all_g[best_index].vs["u"]]
	else:
		print "Error. No efficient graph found."

	print ""

	# measure stability of all graphs
	for g in all_g:
		stable1, stable2 = False, True
		
		# look at each edge
		for e in g.get_edgelist():
			# find graph that is missing this edge
			# temporarily delete the edge (we'll add back)
			g.delete_edges([e])
			for g2 in all_g:
				if g.get_edgelist() == g2.get_edgelist():

					if g.vs[e[0]]["u"] >= g2.vs[e[0]]["u"] and \
					   g.vs[e[1]]["u"] >= g2.vs[e[0]]["u"]:
						stable1 = True
						break
			g.add_edges([e])

		if len(g.get_edgelist()) == 0:
			stable1 = True

		# look at each non-edge
		for i in range(0, num_nodes):
			for j in range(0, num_nodes):
				if i == j: continue
				if (i, j) not in g.get_edgelist() and (j, i) not in g.get_edgelist():
					# temporarily add to find the adjacent graph
					g.add_edges([(i, j)])
					for h2 in all_g:
						if g == h2: continue
						if set(g.get_edgelist()) == set(h2.get_edgelist()):
							# adjacent graph!
							if h2.vs[i]["u"] > g.vs[i]["u"]:
								if h2.vs[j]["u"] < g.vs[j]["u"]:
									break
								else:
									stable2 = False
					g.delete_edges([(i, j)])

		# is it stable?
		if stable1 and stable2:
			print "Stable graph:"
			print "- es: ", g.get_edgelist()
			print "- ui: ", [round(u, 2) for u in g.vs["u"]]

if __name__ == "__main__":
	# run tester for values n=3, 4, 5 (for now)

	for n in range(3, 5):
		test_strat_nets(n, .5, .3, 1)
		print ""

	print "Complete."