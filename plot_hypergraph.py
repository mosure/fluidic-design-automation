# https://towardsdatascience.com/how-to-visualize-hypergraphs-with-python-and-networkx-the-easy-way-4fe7babdf9ae

from collections import defaultdict

import networkx as nx
from networkx import NetworkXException
import matplotlib.pyplot as plt


def decompose_edges_by_len(hypergraph):
    decomposed_edges = defaultdict(list)
    for edge in hypergraph.edges:
        decomposed_edges[len(edge)].append(edge)
    decomposition = {
        'nodes': hypergraph.nodes,
        'edges': decomposed_edges
    }

    return decomposition

def plot_hypergraph_components(hypergraph):
    decomposed_graph = decompose_edges_by_len(hypergraph)
    decomposed_edges = decomposed_graph['edges']
    nodes = decomposed_graph['nodes']

    n_edge_lengths = len(decomposed_edges)

    # Setup multiplot style
    fig, axs = plt.subplots(1, n_edge_lengths, figsize=(5*n_edge_lengths, 5))
    if n_edge_lengths == 1:
        axs = [axs]  # Ugly hack
    for ax in axs:
        ax.axis('off')
    fig.patch.set_facecolor('#003049')

    # For each edge order, make a star expansion (if != 2) and plot it
    for i, edge_order in enumerate(sorted(decomposed_edges)):
        edges = decomposed_edges[edge_order]
        g = nx.DiGraph()
        g.add_nodes_from(nodes)
        if edge_order == 2:
            g.add_edges_from(edges)
        else:
            for edge in edges:
                g.add_node(tuple(edge))
                for node in edge:
                    g.add_edge(node,tuple(edge))

        # I like planar layout, but it cannot be used in general
        try:
            pos = nx.planar_layout(g)
        except NetworkXException:
            pos = nx.spring_layout(g)

        # Plot true nodes in orange, star-expansion edges in red
        extra_nodes = set(g.nodes) - set(nodes)
        nx.draw_networkx_nodes(g, pos, node_size=300, nodelist=nodes,
                               ax=axs[i], node_color='#f77f00')
        nx.draw_networkx_nodes(g, pos, node_size=150, nodelist=extra_nodes,
                               ax=axs[i], node_color='#d62828')

        nx.draw_networkx_edges(g, pos, ax=axs[i], edge_color='#eae2b7',
                               connectionstyle='arc3,rad=0.05', arrowstyle='-')

        # Draw labels only for true nodes
        labels = {node: str(node) for node in nodes}
        nx.draw_networkx_labels(g, pos, labels, ax=axs[i])

    plt.savefig('out.png')
