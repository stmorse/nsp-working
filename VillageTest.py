# VillageTest.py

import csv
import heapq
import math
import random

import igraph

# generic function to read csv
def read_csv_data(path):
	with open(path, 'rU') as data:
		reader = csv.DictReader(data)
		for row in reader:
			yield row

HH_CLEAN = "Afghan_v3_individual.csv"

#

print "Loading village data for HESARAK..."

# village stats
vil_labels = []
vil_tot_pop = {}		# {"label": pop}
vil_HH_pop = {}			# {"label": HH_pop}
HH_coords = {}			# {"label":[(lat,long), ...], }
vil_avg_coords = {}		# {"label": [lat, long]}

# build village stats for HESARAK
for row in read_csv_data(HH_CLEAN):
	if row["District"] != "HESARAK":
		continue

	label = row["distvil"]

	# if new village, initialize all counters
	if label not in vil_labels:
		vil_labels.append(label)
		vil_tot_pop[label] = 0
		vil_HH_pop[label] = 0
		HH_coords[label] = []
		vil_avg_coords[label] = [0,0]
	
	# continue tallying population (we'll avg at end)
	if row["Village_size"] != "?":
		vil_tot_pop[label] += int(row["Village_size"])
	vil_HH_pop[label] += 1

	lat = float(row["Latitude"])
	lon = float(row["Longitude"])

	# append HH coords as (lat, long)
	HH_coords[label].append((lat, lon))

	# "center point" of village (avg at the end)
	vil_avg_coords[label][0] += lat
	vil_avg_coords[label][1] += lon

# average village populations and coordinates
for lab in vil_labels:
	vil_tot_pop[lab] /= vil_HH_pop[lab]
	vil_avg_coords[lab][0] /= vil_HH_pop[lab]
	vil_avg_coords[lab][1] /= vil_HH_pop[lab]

#

print "Building scale-free (Barabasi) village networks..."

# create scale-free network for each village
villages = []
for name in vil_labels:
	vil = igraph.Graph.Barabasi(vil_tot_pop[name], 1)
	vil["name"] = name
	vil["coords"] = vil_avg_coords[name]

	# make a list of the indices in order of # connections
	index_sorted = sorted(
		range(len(vil.degree())), 
		key=lambda k: vil.degree(k),
		reverse=True)
	
	# select top connected individuals, make them HH
	# assign coords (arbitrary)
	for i in range(0, vil_HH_pop[name]):
		vil.vs[index_sorted[i]]["type"] = "HH"
		vil.vs[index_sorted[i]]["HH-coords"] = HH_coords[name][i]

	villages.append(vil)

# 

# generate district level network 
# Step 1: compute ALL village distances
# Step 2: delete edges at prob prop to distance

# Step 1: compute all distances between villages
all_paths = igraph.Graph.Full(len(villages))
for edge in all_paths.es:
	lat1 = villages[edge.source]["coords"][0]
	lon1 = villages[edge.source]["coords"][1]
	lat2 = villages[edge.target]["coords"][0]
	lon2 = villages[edge.target]["coords"][1]
	latdist = math.pow(lat1 - lat2, 2)
	londist = math.pow(lon1 - lon2, 2)
	hyp = math.sqrt(latdist + londist)
	edge["distance"] = hyp

# Step 2: delete edges
# lambda just 1, we will scale distances
lamb = 1
district = igraph.Graph(len(villages))
for e in all_paths.es:
	rand = random.random()
	thresh = lamb * math.exp(-lamb * 40 * e["distance"])
	if rand <= thresh:
		district.add_edges([(e.source, e.target)])

print district

# default: build random small-world network

# beta value for chance of random rewiring
# ws_beta = .5

# print "Building small-world (beta=%.1f) district network..." % (ws_beta)

# district = igraph.Graph.Watts_Strogatz(
# 	1, len(villages), 1, ws_beta,
# 	loops=False, multiple=False)

#

print "Writing to file..."

# write all HESARAK villages to file
for vil in villages:
	# add nodes
	vstr = '{\"nodes\":['
	for i in range(0, len(vil.vs)):
		vstr += '{\"node\": ' + str(i) + '},'
	vstr = vstr.rstrip(',') + '],'

	# add links
	vstr += '\"links\":['
	for e in vil.get_edgelist():
		vstr += '{\"source\":' + str(e[0]) + ','
		vstr += '\"target\":' + str(e[1]) + '},'
	vstr = vstr.rstrip(',') + ']}'

	path = 'villages/' + vil["name"] + '.json'
	with open(path, 'w+') as g:
		g.write(vstr)
		g.close

# write district level data to file
jstr = '{\"type\": \"FeatureCollection\",'
jstr += '\"features\": ['

# write new district point
for vil in villages:
	jstr += '{\"type\": \"Feature\",'
	jstr += '\"properties\": {'
	jstr += '\"type\":\"village\",'
	jstr += '\"population\": ' + str(len(vil.vs)) + ','
	jstr += '\"name\": \"' + vil["name"] + '\"},'
	jstr += '\"geometry\": {\"type\":\"Point\",'
	jstr += '\"coordinates\": ['
	
	# coordinates need to be long/lat in json (????)
	jstr += str(vil["coords"][1]) + ','
	jstr += str(vil["coords"][0])
	jstr += ']}},'

# write all edges
for ed in district.get_edgelist():
	jstr += '{\"type\": \"Feature\",'
	jstr += '\"properties\": {'
	jstr += '\"type\":\"connection\",'
	jstr += '\"name1\": \"' + villages[ed[0]]["name"] + '\",'
	jstr += '\"name2\": \"' + villages[ed[1]]["name"] + '\"},'
	jstr += '\"geometry\": {\"type\":\"LineString\",'
	jstr += '\"coordinates\": [['
	jstr += str(villages[ed[0]]["coords"][1]) + ','
	jstr += str(villages[ed[0]]["coords"][0]) + '], ['
	jstr += str(villages[ed[1]]["coords"][1]) + ','
	jstr += str(villages[ed[1]]["coords"][0]) + ']]}},'

jstr = jstr.rstrip(',') + ']}'

with open('maptestdata2.json', 'w+') as g:
	g.write(jstr)
	g.close

print "Complete."

