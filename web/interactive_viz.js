const mainFunction = function (dataArray) {

	let db = cytoscape({
		headless: true,
		elements: dataArray[0].elements
	})

	db.remove(db.edges("[weight <= 1]"))

	let cy = cytoscape({
		container: document.getElementById('cy'),
		elements: [],
		style: [
			{
				selector: 'node',
				style: {
					'background-color': '#eee8d5',
					// 'label': 'data(content)',
					'content': 'data(content)',
					'text-valign': "center",
					'text-halign': "center",
					'shape': 'rectangle',
					'width': 300,
					'height': 150,
					'color': '#586e75',
					'text-wrap': 'wrap',
					'text-max-width': 300,
					// 'text-background-opacity': 1,
					// 'text-background-color': '#eee8d5',
					// 'text-background-shape': 'roundrectangle',
					// 'text-border-color': '#000',
					// 'text-border-width': 1,
					// 'text-border-opacity': 1
				}
			},
			{
				selector: 'edge',
				style: {
					'width': 20,
					'opacity': 0.2,
					'line-color': '#586e75',
					'target-arrow-color': '#586e75',
					'target-arrow-shape': 'triangle'
				}
			}
		]
	})

	let contextMenuInstance = cy.contextMenus({
		menuItems: [
			{
				id: 'hide',
				content: 'Hide',
				selector: 'node',
				onClickFunction: function (event) {
					event.target.remove()
					filteredNodes.add(event.target.data("id"))
				}
			},
			{
				id: 'collapse',
				content: 'Collapse',
				selector: 'node',
				onClickFunction: function (event) {
					expandedNodes.delete(event.target.data("id"))
					event.target.neighborhood().nodes().forEach((node) => {
						for (const metanode of node.neighborhood().nodes()) {
							if (expandedNodes.has(metanode.data("id"))) {
								return
							}
						}
						if (!expandedNodes.has(node.data("id"))) {
							node.remove()
						}
					})
				}
			}
		]
	})

	var expandedNodes = new Set() // the set of nodes that have been "expanded"
	var filteredNodes = new Set() // the set of nodes that have been hidden, i.e. aren't wanted in the visualization.

	startNodeId = "Games Research"
	expandedNodes.add(startNodeId)
	cy.add(db.$id(startNodeId))
	cy.center()

	const layoutConfig = {
		name: "cola",
		handleDisconnected: true,
		animate: true,
		avoidOverlap: true,
		infinite: false,
		unconstrIter: 1,
		userConstIter: 0,
		allConstIter: 1,
		ready: e => {
			e.cy.fit()
			e.cy.center()
		},
		edgeLength: function (edge) {
			if (edge.data().weight === undefined) {
				return 400
			} else {
				return 1000 / edge.data().weight
			}
		}
	}
	layout = cy.layout(layoutConfig)

	// Takes a set of nodes, and adds all edges between them from the db to the displayed graph.
	let fillInEdges = function (eles) {
		eles.nodes().forEach(node => {
			edges = node.neighborhood().edges()
			edges.forEach((edge) => {
				existingNodes = cy.nodes().map(node => node.data("id"))
				if (existingNodes.includes(edge.data("source")) && existingNodes.includes(edge.data("target"))) {
					cy.add(edge)
				}
			})
		})
	}

	let revealNeighborhood = function (event) {
		const targetId = event.target.data('id')
		expandedNodes.add(targetId)

		nodeNeighborhood = db.getElementById(targetId).neighborhood()
		nodeNeighborhood = nodeNeighborhood.filter(neighbor => !filteredNodes.has(neighbor.data('id')) && !filteredNodes.has(neighbor.data('target')))
		addedNodes = cy.add(nodeNeighborhood)
		fillInEdges(nodeNeighborhood)
		const spread = 500
		addedNodes.positions((element, i) => {
			return {
				x: cy.$id(targetId).position().x + Math.random() * spread - (spread / 2),
				y: cy.$id(targetId).position().y + Math.random() * spread - (spread / 2)
			}
		})

		const layout = cy.layout(layoutConfig)
		layout.run()

		// console.log(expandedNodes)
	}

	cy.on("tap", "node", revealNeighborhood)
}

Promise.all([
	fetch('permanote_graph.json').then(res => res.json())
]).then(function (dataArray) {
	mainFunction(dataArray)
})

