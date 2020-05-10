
The first part of the project are the Python scripts used to process the data. The `page_graph.py` script is used to transform a JSON export of a Roam database into a JSON page graph in Cytoscape's JSON format. Then `co_citation_graph.py` can be used to tranform that into a co-citation graph in the same format.

The second part is the web page which uses Cytoscape.js to create an interactive visualization of the page graph.

In order to use this to visualize your own Roam database, you'll first need to run `python3 page_graph.py my_db.json web/my_page_graph.json` (and optionally `python3 co_citation_graph.py my_page_graph.json`). The resulting page graph must be placed in the `web` directory for the web app to work.

The path to the page graph file and the title of the starting page node needs to be specified in `web/interactive_viz.js`, after which it should work if you just open up `web/interactive_viz_.html`.