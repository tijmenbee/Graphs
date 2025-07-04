# -*- coding: utf-8 -*-

######################
# Based on the following implementation of Louvain
# https://github.com/taynaud/python-louvain/tree/master
# From the paper
# Thomas Aynaud, Jean-Loup Guillaume. Static community detection algorithms for evolving networks.
# WiOpt’10: Modeling and Optimization in Mobile, Ad Hoc, and Wireless Networks, May 2010, Avignon,
# France. pp.508-514. inria-00492058
######################

######################
# WE MADE MODIFICATIONS TO THE FUNCTIONS BELOW: BEST_PARTITION, GENERATE_DENDROGRAM, __ONE_LEVEL
# AND WE CREATED OWN_REFINEMENT, BASED ON __ONE_LEVEL
######################


from __future__ import print_function

import copy
import networkx as nx
import warnings

from .community_status import Status
from louvain_variant.utils import __neighcom, __remove, __insert, __modularity, __randomize, __renumber
from louvain_variant.utils import induced_graph, modularity, partition_at_level, __PASS_MAX, __MIN, check_random_state


__author__ = """Thomas Aynaud (thomas.aynaud@lip6.fr)"""
#    Copyright (C) 2009 by
#    Thomas Aynaud <thomas.aynaud@lip6.fr>
#    All rights reserved.
#    BSD license.

def best_partition(graph,
                   partition=None,
                   weight='weight',
                   resolution=1.,
                   randomize=None,
                   random_state=None,
                   core_threshold=0.8):
    """Compute the partition of the graph nodes which maximises the modularity
    (or try..) using the Louvain heuristices

    This is the partition of highest modularity, i.e. the highest partition
    of the dendrogram generated by the Louvain algorithm.

    Parameters
    ----------
    graph : networkx.Graph
       the networkx graph which is decomposed
    partition : dict, optional
       the algorithm will start using this partition of the nodes.
       It's a dictionary where keys are their nodes and values the communities
    weight : str, optional
        the key in graph to use as weight. Default to 'weight'
    resolution :  double, optional
        Will change the size of the communities, default to 1.
        represents the time described in
        "Laplacian Dynamics and Multiscale Modular Structure in Networks",
        R. Lambiotte, J.-C. Delvenne, M. Barahona
    randomize : boolean, optional
        Will randomize the node evaluation order and the community evaluation
        order to get different partitions at each call
    random_state : int, RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.

    Returns
    -------
    partition : dictionnary
       The partition, with communities numbered from 0 to number of communities

    Raises
    ------
    NetworkXError
       If the graph is not undirected.

    See Also
    --------
    generate_dendrogram : to obtain all the decompositions levels

    Notes
    -----
    Uses Louvain algorithm

    References
    ----------
    .. 1. Blondel, V.D. et al. Fast unfolding of communities in
    large networks. J. Stat. Mech 10008, 1-12(2008).

    Examples
    --------
    >>> # basic usage
    >>> import community as community_louvain
    >>> import networkx as nx
    >>> G = nx.erdos_renyi_graph(100, 0.01)
    >>> partion = community_louvain.best_partition(G)

    >>> # display a graph with its communities:
    >>> # as Erdos-Renyi graphs don't have true community structure,
    >>> # instead load the karate club graph
    >>> import community as community_louvain
    >>> import matplotlib.cm as cm
    >>> import matplotlib.pyplot as plt
    >>> import networkx as nx
    >>> G = nx.karate_club_graph()
    >>> # compute the best partition
    >>> partition = community_louvain.best_partition(G)

    >>> # draw the graph
    >>> pos = nx.spring_layout(G)
    >>> # color the nodes according to their partition
    >>> cmap = cm.get_cmap('viridis', max(partition.values()) + 1)
    >>> nx.draw_networkx_nodes(G, pos, partition.keys(), node_size=40,
    >>>                        cmap=cmap, node_color=list(partition.values()))
    >>> nx.draw_networkx_edges(G, pos, alpha=0.5)
    >>> plt.show()
    """
    dendo = generate_dendrogram(graph,
                                partition,
                                weight,
                                resolution,
                                randomize,
                                random_state,
                                core_threshold)
  
    return partition_at_level(dendo, len(dendo) - 1)

def generate_dendrogram(graph,
                        part_init=None,
                        weight='weight',
                        resolution=1.,
                        randomize=None,
                        random_state=None,
                        core_threshold=0.8):
    """Find communities in the graph and return the associated dendrogram

    A dendrogram is a tree and each level is a partition of the graph nodes.
    Level 0 is the first partition, which contains the smallest communities,
    and the best is len(dendrogram) - 1. The higher the level is, the bigger
    are the communities


    Parameters
    ----------
    graph : networkx.Graph
        the networkx graph which will be decomposed
    part_init : dict, optional
        the algorithm will start using this partition of the nodes. It's a
        dictionary where keys are their nodes and values the communities
    weight : str, optional
        the key in graph to use as weight. Default to 'weight'
    resolution :  double, optional
        Will change the size of the communities, default to 1.
        represents the time described in
        "Laplacian Dynamics and Multiscale Modular Structure in Networks",
        R. Lambiotte, J.-C. Delvenne, M. Barahona

    Returns
    -------
    dendrogram : list of dictionaries
        a list of partitions, ie dictionnaries where keys of the i+1 are the
        values of the i. and where keys of the first are the nodes of graph

    Raises
    ------
    TypeError
        If the graph is not a networkx.Graph

    See Also
    --------
    best_partition

    Notes
    -----
    Uses Louvain algorithm

    References
    ----------
    .. 1. Blondel, V.D. et al. Fast unfolding of communities in large
    networks. J. Stat. Mech 10008, 1-12(2008).

    Examples
    --------
    >>> G=nx.erdos_renyi_graph(100, 0.01)
    >>> dendo = generate_dendrogram(G)
    >>> for level in range(len(dendo) - 1) :
    >>>     print("partition at level", level,
    >>>           "is", partition_at_level(dendo, level))
    :param weight:
    :type weight:
    """
    if graph.is_directed():
        raise TypeError("Bad graph type, use only non directed graph")

    # Properly handle random state, eventually remove old `randomize` parameter
    # NOTE: when `randomize` is removed, delete code up to random_state = ...
    if randomize is not None:
        warnings.warn("The `randomize` parameter will be deprecated in future "
                      "versions. Use `random_state` instead.", DeprecationWarning)
        # If shouldn't randomize, we set a fixed seed to get determinisitc results
        if randomize is False:
            random_state = 0

    # We don't know what to do if both `randomize` and `random_state` are defined
    if randomize and random_state is not None:
        raise ValueError("`randomize` and `random_state` cannot be used at the "
                         "same time")

    random_state = check_random_state(random_state)

    # special case, when there is no link
    # the best partition is everyone in its community
    if graph.number_of_edges() == 0:
        part = dict([])
        for i, node in enumerate(graph.nodes()):
            part[node] = i
        return [part]

    current_graph = graph.copy()
    status = Status(core_threshold=core_threshold)
    status.init(current_graph, weight, part_init)
    status_list = list()
    refined_status = __one_level(current_graph, status, weight, resolution, random_state)
    partition = __renumber(status.node2com)
    if refined_status is None:
        refined_partition = None
        current_graph = induced_graph(partition, current_graph, weight)
    else:   
        refined_partition = __renumber(refined_status.node2com)
        current_graph = induced_graph(refined_partition, current_graph, weight)

    status_list.append(partition)
    new_mod = __modularity(status, resolution)
    status.init(current_graph, weight, part=refined_partition)  
    mod = new_mod

    while True:
        refined_status = __one_level(current_graph, status, weight, resolution, random_state)
        new_mod = __modularity(status, resolution)
        if new_mod - mod < __MIN:
            break

        partition = __renumber(status.node2com)
        if refined_status is None:
            refined_partition = None
            current_graph = induced_graph(partition, current_graph, weight)
        else:   
            refined_partition = __renumber(refined_status.node2com)
            current_graph = induced_graph(refined_partition, current_graph, weight)

        status_list.append(partition)
        mod = new_mod
        status.init(current_graph, weight, part=refined_partition)

    return status_list[:]

def own_refinement(graph, modified_community, status, weight_key, resolution, random_state):
    modified = True
    nb_pass_done = 0
    cur_mod = __modularity(status, resolution) ## @TODO: quickly recompute internals??
    new_mod = cur_mod

    while modified and nb_pass_done != __PASS_MAX:
        cur_mod = new_mod
        modified = False
        nb_pass_done += 1

        iterator = __randomize(modified_community, random_state)

        for node in iterator:
            com_node = status.node2com[node]
            degc_totw = status.gdegrees.get(node, 0.) / (status.total_weight * 2.)  # NOQA
            neigh_communities = __neighcom(node, graph, status, weight_key)
            remove_cost = - neigh_communities.get(com_node,0) + \
                resolution * (status.degrees.get(com_node, 0.) - status.gdegrees.get(node, 0.)) * degc_totw
            __remove(node, com_node,
                     neigh_communities.get(com_node, 0.), status)
            best_com = com_node
            best_increase = 0
            for com, dnc in __randomize(neigh_communities.items(), random_state):
                incr = remove_cost + dnc - \
                       resolution * status.degrees.get(com, 0.) * degc_totw
                if incr > best_increase:
                    best_increase = incr
                    best_com = com

            __insert(node, best_com,
                     neigh_communities.get(best_com, 0.), status)
            if best_com != com_node:
                modified = True
        new_mod = __modularity(status, resolution)
        if new_mod - cur_mod < __MIN:
            break

## @TODO: modify for set of soft-nodes
def __one_level(graph: nx.Graph, status: Status, weight_key, resolution, random_state):
    """Compute one level of communities
    """
    modified = True
    nb_pass_done = 0
    cur_mod = __modularity(status, resolution)
    new_mod = cur_mod
    coms_to_refine = set()

    while modified and nb_pass_done != __PASS_MAX:
        cur_mod = new_mod
        modified = False
        nb_pass_done += 1

        if status.soft_nodes_set is None:
            iterator = __randomize(graph.nodes(), random_state)
        else:
            iterator = __randomize(status.soft_nodes_set, random_state)

        for node in iterator:
            com_node = status.node2com[node]
            
            degc_totw = status.gdegrees.get(node, 0.) / (status.total_weight * 2.)  # NOQA
            neigh_communities = __neighcom(node, graph, status, weight_key)
            remove_cost = - neigh_communities.get(com_node,0) + \
                resolution * (status.degrees.get(com_node, 0.) - status.gdegrees.get(node, 0.)) * degc_totw
            __remove(node, com_node,
                     neigh_communities.get(com_node, 0.), status)
            best_com = com_node
            best_increase = 0
            for com, dnc in __randomize(neigh_communities.items(), random_state):
                incr = remove_cost + dnc - \
                       resolution * status.degrees.get(com, 0.) * degc_totw
                if incr > best_increase:
                    best_increase = incr
                    best_com = com
            __insert(node, best_com,
                     neigh_communities.get(best_com, 0.), status)
            
            if best_com != com_node:
                modified = True
                if status.node_new_arrival[node]:
                    coms_to_refine |= set([best_com])
        new_mod = __modularity(status, resolution)
        if new_mod - cur_mod < __MIN:
            break

    ##### checking all communities with new arrivals for sub-structures
    return_status = None # if no soft nodes exist yet, i.e. first iteration, then do not assign partition to aggregated graph
    if status.soft_nodes_set is not None:
        refined_status_phase = copy.deepcopy(status)
        for singleton_id, node in enumerate(graph):
            refined_status_phase.node2com[node] = singleton_id

        # refine partition and only consider changed communities
        for com in coms_to_refine:
            com_members = [node for node, community in status.node2com.items() if community == com]
            own_refinement(graph, com_members, refined_status_phase, weight_key, resolution, random_state)
            for node in com_members:
                status.node2com[node] = refined_status_phase.node2com[node]
        return_status = refined_status_phase

    return return_status