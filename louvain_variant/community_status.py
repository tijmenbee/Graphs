# coding=utf-8
######################
# Based on the following implementation of Louvain
# https://github.com/taynaud/python-louvain/tree/master
# From the paper
# Thomas Aynaud, Jean-Loup Guillaume. Static community detection algorithms for evolving networks.
# WiOpt’10: Modeling and Optimization in Mobile, Ad Hoc, and Wireless Networks, May 2010, Avignon,
# France. pp.508-514. inria-00492058
######################

import networkx as nx

class Status(object):
    """
    To handle several data in one struct.

    Could be replaced by named tuple, but don't want to depend on python 2.6
    """
    node2com = {}
    total_weight = 0
    internals = {}
    degrees = {}
    gdegrees = {}

    def __init__(self, core_threshold=0.8):
        self.node2com = dict([])
        self.total_weight = 0
        self.degrees = dict([])
        self.gdegrees = dict([])
        self.internals = dict([])
        self.loops = dict([])
        self.core_threshold = core_threshold

    def __str__(self):
        return ("node2com : " + str(self.node2com) + " degrees : "
                + str(self.degrees) + " internals : " + str(self.internals)
                + " total_weight : " + str(self.total_weight))

    def copy(self):
        """Perform a deep copy of status"""
        new_status = Status()
        new_status.node2com = self.node2com.copy()
        new_status.internals = self.internals.copy()
        new_status.degrees = self.degrees.copy()
        new_status.gdegrees = self.gdegrees.copy()
        new_status.total_weight = self.total_weight

    def _compute_core_centrality(self, neighbours_list: list, community_set: set):
        neighbours_list = set(neighbours_list)
        degree = len(neighbours_list)

        k_in_community = len(neighbours_list & community_set)
        k_out_community = len(neighbours_list - community_set)

        core_centrality = 1 - (k_out_community / degree)

        return core_centrality, k_out_community
    
    def _get_community_set(self, neighbours_list: list, node2com: dict, current_com: int):
        return set([node for node in neighbours_list if node2com[node] == current_com])

    def init(self, graph: nx.Graph, weight, part=None):
        """Initialize the status of a graph with every node in one community"""
        count = 0
        self.node2com = dict([])
        self.total_weight = 0
        self.degrees = dict([])
        self.gdegrees = dict([])
        self.internals = dict([])
        self.total_weight = graph.size(weight=weight)

        self.external_degrees = dict([])
        self.core_centrality = dict([])

        self.soft_nodes_set = None

        if part is None:
            for node in graph.nodes():
                self.node2com[node] = count
                deg = float(graph.degree(node, weight=weight))
                if deg < 0:
                    error = "Bad node degree ({})".format(deg)
                    raise ValueError(error)
                self.degrees[count] = deg
                self.gdegrees[node] = deg
                edge_data = graph.get_edge_data(node, node, default={weight: 0})
                self.loops[node] = float(edge_data.get(weight, 1))
                self.internals[count] = self.loops[node]
                count += 1
        else:
            self.soft_nodes_set = set()
            ## @TODO: add check for nodes that are not in partition but where added to the graph later
            for node in graph.nodes():
                com = part[node]
                self.node2com[node] = com
                deg = float(graph.degree(node, weight=weight))
                self.degrees[com] = self.degrees.get(com, 0) + deg
                self.gdegrees[node] = deg

                neighbor_list = list(graph.neighbors(node))
                community_set = self._get_community_set(neighbor_list, part, com)
                core_centrality, external_degree = self._compute_core_centrality(neighbor_list, community_set)
                self.external_degrees[node] = external_degree
                self.core_centrality[node] = core_centrality

                # if node == 23:
                #     print(external_degree)
                #     print(core_centrality)
                #     print(neighbor_list)
                #     print(community_set)

                if core_centrality < self.core_threshold:
                    self.soft_nodes_set |= set([node])
                
                inc = 0.
                for neighbor, datas in graph[node].items():
                    edge_weight = datas.get(weight, 1)
                    if edge_weight <= 0:
                        error = "Bad graph type ({})".format(type(graph))
                        raise ValueError(error)
                    if part[neighbor] == com:
                        if neighbor == node:
                            inc += float(edge_weight)
                        else:
                            inc += float(edge_weight) / 2.
                self.internals[com] = self.internals.get(com, 0) + inc
            # print(self.soft_nodes_set)
            # print(self.core_centrality)
