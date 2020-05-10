import sys
import json
import networkx as nx
import itertools

infile = sys.argv[1]
outfile = sys.argv[2]

with open(infile, "r") as f:
	page_graph = nx.json_graph.cytoscape_graph(json.loads(f.read())).to_undirected()

co_citation_graph = nx.Graph()
co_citation_graph.add_nodes_from(page_graph.nodes)
for node in co_citation_graph.nodes(): 
	for u, v in itertools.combinations(page_graph.neighbors(node), 2):
		try:
			co_citation_graph.edges[u, v]["weight"] += 1
		except KeyError:
			co_citation_graph.add_edge(u, v, weight=1)
co_citation_graph_dict = nx.json_graph.cytoscape_data(co_citation_graph)

with open(outfile, 'w') as jf:
	json.dump(co_citation_graph_dict, jf)
