import subprocess

import networkx as nx
from networkx.drawing.nx_pydot import write_dot

from wopmars.main.tagc.framework.bdd.SQLManager import SQLManager
from wopmars.main.tagc.utils.Logger import Logger
from wopmars.main.tagc.utils.SetUtils import SetUtils


class DAG(nx.DiGraph):
    """
    This class inherits from networkx.DiGraph class and is able to represent a DAG of tool nodes. It takes a set of
    :class:`~.wopmars.main.tagc.framework.bdd.tables.ToolWrapper` and analyse it to extract dependencies between them.
    """    
    def __init__(self, set_tools=None):
        """
        The DAG can be build from a set of tools, analyzing the successors of each of them.

        ToolWrappers has a method "follows()" wich allow to know if one tool has a dependency for one other. The tools
        of the set_tools are compared each other to extract the dependencies.
        
        :param set_tools: A set of tools
        """
        # the DAG is a DiGraph
        super().__init__()
        Logger.instance().info("Building the execution DAG...")
        if set_tools:
            # for each tool
            for tool1 in set_tools:
                self.add_node(tool1)
                # for each other tool
                for tool2 in set_tools.difference(set([tool1])):
                    # is there a dependency between tool1 and tool2?
                    if tool1.follows(tool2):
                        self.add_edge(tool2, tool1)

        Logger.instance().debug("DAG built.")

    def write_dot(self, path):
        """
        Build the dot file.

        The .ps can be built from the dot file with the command line: "dot -Tps {filename}.dot - o {filename}.ps"
        """
        # To build .ps : dot -Tps {filename}.dot - o {filename}.ps
        nx.draw(self)
        write_dot(self, path)
        # building the openable file:
        list_popen = ["dot", "-Tps", path, "-o", path.rsplit("/", 1)[0] + "/" + path.rsplit("/", 1)[1].split(".")[-2] + ".ps"]
        Logger.instance().debug("SubProcess command line for .ps file: " + str(list_popen))
        p = subprocess.Popen(list_popen)
        p.wait()

    def successors(self, node):
        """
        Get the successors of a node.

        The method is overwhelmed because if a node is None, then, the root nodes are returned.

        :param node: a node of the DAG or None.
        :type node: :class:`~.wopmars.main.tagc.framework.bdd.tables.ToolWrapper.ToolWrapper`
        :return: [node]:  the successors of the given node or the node at the root of the DAG.
        """
        if not node:
            # in_degree is the number of incoming edges to a node. If the degree is 0, then the node is at the root
            # of the DAG.
            return [n for n, d in self.in_degree().items() if d == 0]
        else:
            s = super().successors(node)
            return s

    def get_all_successors(self, node):
        """
        Return the set of all successors nodes from a given node in the DAG (node included).

        :param node: a node of the DAG or None.
        :type node: :class:`~.wopmars.main.tagc.framework.bdd.tables.ToolWrapper.ToolWrapper`

        :return: set(node): all the successors of a given node.
        """
        list_successors = [node]
        for N in self.successors(node):
            list_successors.extend(self.get_all_successors(N))
        return set(list_successors)

    def get_all_predecessors(self, node):
        """
        Return the set of all predecessors nodes from a given node in the DAG (node included).

        :param node: a node of the DAG or None.
        :type node: :class:`~.wopmars.main.tagc.framework.bdd.tables.ToolWrapper.ToolWrapper`

        :return: set(node): all the predecessors of a given node.
        """
        list_predecessors = [node]
        for N in self.predecessors(node):
            list_predecessors.extend(self.get_all_predecessors(N))
        return set(list_predecessors)

    def __eq__(self, other):
        """
        Test if self equals other.

        Check the number of nodes and the set of edges of each graphs.

        :param other: the other DAG to compare
        :type other: :class:`wopmars.main.tagc.framework.management.DAG.DAG`

        :return: True if self == other. Else, False.
        """
        assert isinstance(other, self.__class__)
        int_nodes_self = len(self.nodes())
        int_nodes_other = len(other.nodes())

        set_edges_self = set(self.edges())
        set_edges_other = set(other.edges())

        return (
            int_nodes_self == int_nodes_other and
            SetUtils.all_elm_of_one_set_in_one_other(set_edges_self, set_edges_other) and
            SetUtils.all_elm_of_one_set_in_one_other(set_edges_other, set_edges_self)
        )
