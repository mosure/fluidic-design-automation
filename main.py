from lib import (
    Component,
    EdgeTypes,
    Latch,
    NOR,
    NAND,
    PFET,
    TestComponent,
)


def draw_hnx(component: Component):
    import hypernetx as hnx
    import matplotlib.pyplot as plt

    node_count = len(component.hypergraph.get_node_set())

    plt.figure(figsize=(node_count, node_count))

    scenes = {}
    for edge in component.hypergraph.get_hyperedge_id_set():
        edge_name = edge
        edge_attributes = component.hypergraph.get_hyperedge_attributes(edge)

        if edge_attributes['type'] == EdgeTypes.LABEL:
            edge_name = f'{edge_attributes["name"]} - {edge_name}'

        scenes[edge_name] = map(lambda n: str(n), component.hypergraph.get_hyperedge_nodes(edge))

    hnx_graph = hnx.Hypergraph(scenes)
    hnx.draw(hnx_graph)

    plt.savefig(f'output/{component.__class__.__name__}.svg')

def write_component(component: Component):
    component.hypergraph.write(f'output/{component.__class__.__name__}.hypergraph')


if __name__ == "__main__":
    models = [
        TestComponent(),
        PFET(),
        NOR(),
        NAND(),
        Latch()
    ]

    for model in models:
        draw_hnx(model)
        write_component(model)
