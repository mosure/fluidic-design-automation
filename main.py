from __future__ import annotations
from collections import UserDict
from enum import Enum

from halp.undirected_hypergraph import UndirectedHypergraph


class EdgeTypes(Enum):
    TRACE = 'trace'
    LABEL = 'label'


class Node:
    id_counter = 0

    def __init__(self, component: Component):
        Node.id_counter += 1

        self.id = f'n{Node.id_counter}'
        self.connections = set()
        self.component = component
        self.hypergraph = self.component.hypergraph

        self.hypergraph.add_node(self)

    @property
    def name(self):
        for key, value in vars(self.component).items():
            if isinstance(value, Node) and value == self:
                return key

        return self.id

    def connect(self, node: Node):
        if node not in self.hypergraph.get_node_set():
            raise Exception("Node must exist in similar hypergraph.")

        self.hypergraph.add_hyperedge([self, node], {
            'type': EdgeTypes.TRACE
        })

        edges = self.hypergraph.get_star(self).union(self.hypergraph.get_star(node))

        trace_edges = set()
        nodes = set()

        for edge in edges:
            if self.hypergraph.get_hyperedge_attributes(edge)['type'] != EdgeTypes.TRACE:
                continue

            nodes_of_edge = self.hypergraph.get_hyperedge_nodes(edge)

            nodes.update(nodes_of_edge)
            trace_edges.add(edge)

        if len(trace_edges) > 1:
            self.hypergraph.remove_hyperedges(trace_edges)
            self.hypergraph.add_hyperedge(nodes, {
                'type': EdgeTypes.TRACE
            })

    def __add__(self, to_add: str):
        return str(self) + to_add

    def __eq__(self, node: Node):
        return self.id == node.id

    def __hash__(self):
        return self.id.__hash__()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.id} - {self.name}'

class Component:
    def __init__(self, parent: Component = None):
        if parent:
            self.hypergraph = parent.hypergraph
        else:
            self.hypergraph = UndirectedHypergraph()

    def addLabels(self):
        self.hypergraph.add_hyperedge(list(self.getNodes()), {
            'type': EdgeTypes.LABEL
        })

    def getNodes(self):
        allValues = vars(self).values()
        nodes = filter(lambda v: isinstance(v, Node), allValues)

        return nodes


class PFET(Component):
    def __init__(self, parent: Component = None):
        super().__init__(parent)

        self.gate = Node(self)
        self.drain = Node(self)
        self.source = Node(self)
        self.gnd = Node(self)

        self.addLabels()

class NOR(Component):
    def __init__(self, parent: Component = None):
        super().__init__(parent)

        self.pfetA = PFET(self)
        self.pfetB = PFET(self)

        self.a = Node(self)
        self.b = Node(self)
        self.out = Node(self)
        self.vcc = Node(self)
        self.gnd = Node(self)

        self.pfetA.gate.connect(self.a)
        self.pfetB.gate.connect(self.b)

        self.pfetA.drain.connect(self.vcc)
        self.pfetA.source.connect(self.pfetB.drain)
        self.pfetB.source.connect(self.out)

        self.pfetA.gnd.connect(self.gnd)
        self.pfetB.gnd.connect(self.gnd)

        self.addLabels()

class NAND(Component):
    def __init__(self, parent: Component = None):
        super().__init__(parent)

        self.pfetA = PFET(self)
        self.pfetB = PFET(self)

        self.a = Node(self)
        self.b = Node(self)
        self.out = Node(self)
        self.vcc = Node(self)
        self.gnd = Node(self)

        self.pfetA.gate.connect(self.a)
        self.pfetB.gate.connect(self.b)

        self.pfetA.drain.connect(self.vcc)
        self.pfetB.drain.connect(self.vcc)

        self.out.connect(self.pfetA.source)
        self.out.connect(self.pfetB.source)

        self.pfetA.gnd.connect(self.gnd)
        self.pfetB.gnd.connect(self.gnd)

        self.addLabels()

class Snorlax(Component):
    """
    RS NOR LATCH
    """

    def __init__(self, parent: Component = None):
        super().__init__(parent)

        self.norR = NOR(self)
        self.norS = NOR(self)

        self.r = Node(self)
        self.s = Node(self)
        self.vcc = Node(self)
        self.gnd = Node(self)
        self.q = Node(self)
        self.qp = Node(self)

        self.norR.a.connect(self.r)
        self.norR.b.connect(self.norS.out)

        self.norS.a.connect(self.s)
        self.norS.b.connect(self.norR.out)

        self.norR.vcc.connect(self.vcc)
        self.norS.vcc.connect(self.vcc)

        self.norR.gnd.connect(self.gnd)
        self.norS.gnd.connect(self.gnd)

        self.q.connect(self.norR.out)
        self.qp.connect(self.norS.out)

        self.addLabels()

class TestComponent(Component):
    def __init__(self, parent: Component = None):
        super().__init__(parent)

        self.a = Node(self)
        self.b = Node(self)
        self.c = Node(self)
        self.d = Node(self)

        self.a.connect(self.b)
        self.c.connect(self.d)
        self.b.connect(self.c)

        self.addLabels()


def visualize_component(component: Component):
    from plot_hypergraph import plot_hypergraph_components
    from halp.utilities.undirected_graph_transformations import to_networkx_graph

    nx_graph = to_networkx_graph(component.hypergraph)
    plot_hypergraph_components(nx_graph)

def write_component(component: Component):
    component.hypergraph.write('output.hypergraph')


if __name__ == "__main__":
    model = TestComponent()

    visualize_component(model)
    write_component(model)
