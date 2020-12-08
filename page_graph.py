import sys
from lark import Lark, Transformer
from lark.exceptions import UnexpectedEOF, UnexpectedToken, UnexpectedCharacters
import re
import json
import networkx as nx
import copy
from typing import List, Dict
import itertools

with open("roam_parser.lark") as f:
	parser = Lark(f, start='content', lexer='standard')

def find_links(content: str) -> List[str]:
	"""Return a list of links in the content of a block"""
	try:
		tree = parser.parse(content)
	except (UnexpectedEOF, UnexpectedCharacters) as err:
		print("WARNING: Something went wrong when tokenizing this block: " + content, file=sys.stderr)
		return []
	links = []
	for link_node in tree.find_data("link"):
		pagename = ""
		for child in link_node.children:
			pagename += link_from_syntax_tree(child)
		links.append(pagename)
	return(links)

def link_from_syntax_tree(node):
	"""(recursively) return a link string constructed from a lark syntax (sub)tree"""
	pagename = ""
	if node.data == "string":
		pagename = node.children[0]
	elif node.data == "link":
		pagename += "[["
		for child in node.children:
			pagename += link_from_syntax_tree(child)
		pagename += "]]"
	else:
		for child in node.children:
			pagename += link_from_syntax_tree(child)
	return(pagename)

def find_tags(content: str) -> List[str]:
	"""Return all of the tags in the content of a block"""
	return [part[1:] for part in content.split() if part.startswith('#') and not part.startswith('#[[') and len(part) > 1]

def get_content(node) -> List[str]:
	if "children" in node:
		if "string" in node:
			contents = [node["string"]]
			for child in node["children"]:
				contents = contents + get_content(child)
			return(contents)
		else:
			contents = []
			for child in node["children"]:
				contents = contents + get_content(child)
			return(contents)
	else:
		if "string" in node:
			return([node["string"]])
		else:
			return([])

def initialize_cy_js_graph_dict(directed: bool=False) -> Dict:
	graph_dict = {}
	graph_dict["directed"] = directed
	graph_dict["data"] = {}
	graph_dict["elements"] = {}
	graph_dict["elements"]["nodes"] = []
	graph_dict["elements"]["edges"] = []
	return graph_dict

def main(infile, outfile):
	with open(infile, "r") as f:
		roam_json_string = f.read()

	pagelist = json.loads(roam_json_string)

	graph_dict = initialize_cy_js_graph_dict(directed=True)

	for raw_page in pagelist:
		if raw_page["title"] == "":
			continue
		page = {}
		page["value"] = raw_page["title"]
		graph_dict["elements"]["nodes"].append({"data": page})
		if "title" in raw_page:
			for link in find_links(raw_page["title"]):
				graph_dict["elements"]["edges"].append({"data": {"source": raw_page["title"], "target": link}})
		for block_content in get_content(raw_page):
			if len(block_content) <= 2:
				continue
			elif block_content[-1] is "]" and (not (block_content[-2:] == "]]")):
				links = find_links(block_content[0:-1])
			else:
				try:
					links = find_links(block_content)
				except UnexpectedToken:
					print("WARNING: Link parsing failure with block: " + block_content, file=sys.stderr)
					exit
			links = links + [tag for tag in find_tags(block_content) if not (tag in links)]
			for link in links:
				graph_dict["elements"]["edges"].append({"data": {"source": raw_page["title"], "target": link}})

	graph = nx.json_graph.cytoscape_graph(graph_dict)

	newgraph = copy.deepcopy(graph)

	if infile == "onni_personal.json":
		for child in graph.successors('meta-data'):
			newgraph.remove_node(child)
	for u, v in graph.edges():
		try:
			if u == v:
				newgraph.remove_edge(u, v)
		except nx.exception.NetworkXError:
			pass
	graph = newgraph

	cytoscape_json = True
	gexf = False

	if cytoscape_json:
		graph_dict = nx.json_graph.cytoscape_data(graph)
		with open(outfile, 'w') as jf:
			json.dump(graph_dict, jf)

	if gexf:
		nx.write_gexf(graph, outfile)

if __name__ == "__main__":
	main(sys.argv[1], sys.argv[2])