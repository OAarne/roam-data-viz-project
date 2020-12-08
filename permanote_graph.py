from page_graph import find_links, find_tags
import networkx as nx
import json
import sys

def traverse_block_tree(node, links, parent_permanotes):
	if "title" in node:
		node_links = find_links(node["title"]) + find_tags(node["title"])

	elif "string" in node:
		node_links = find_links(node["string"]) + find_tags(node["string"])
	if is_permanote(node):


def main(infile, outfile):
	# graph_dict = initialize_cy_js_graph_dict()
	graph = nx.Graph()

	with open(infile, "r") as f:
		roam_json_string = f.read()
	pagelist = json.loads(roam_json_string)

	for raw_page in pagelist:


	graph_dict = nx.json_graph.cytoscape_data(graph)
	with open(outfile, 'w') as jf:
		json.dump(graph_dict, jf)

if __name__ == "__main__":
	main(sys.argv[1], sys.argv[2])