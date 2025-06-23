import networkx as nx

from collections import defaultdict
from community import community_louvain
from louvain_variant import louvain_variant, louvain_variant_leiden_addition
from sklearn.metrics import normalized_mutual_info_score
from typing import Tuple

METHOD_MAPPING_VARIANT = {
    "Louvain-Variant": louvain_variant.best_partition,
    "Louvain-Variant Leiden-Addition": louvain_variant_leiden_addition.best_partition,
}
METHOD_MAPPING_ORIGINAL = {
    "Louvain": community_louvain.best_partition,
    "Temporal Louvain": community_louvain.best_partition,
}

def return_def_list() -> defaultdict:
    """
    Function to create specific data structure that makes it easier to store multiple experiment runs
    """
    return defaultdict(list)

def get_true_predicted_parts(graph: nx.Graph, pred_partition: dict, true_partition: dict) -> Tuple[list,list]:
    """
    Extract the predicted and true community assignment of all nodes
    """
    pred_partition_label = []
    true_partition_label = []
    for node in graph.nodes():
        pred_partition_label += [pred_partition[node]]
        true_partition_label += [true_partition[node]]

    return pred_partition_label, true_partition_label

def compute_nmi(temporal_graph: list, partitions: list) -> list:
    """
    NMI does not care about specific label equality, so it is all good, no need to convert between predicted and true labels
    """
    nmi_scores = []
    for g, pred_part in zip(temporal_graph, partitions):
        true_part = {n:d["community_id"] for n, d in g.nodes(data=True)}
        pred_partition_label, true_partition_label = get_true_predicted_parts(g, pred_part, true_part)
        nmi = normalized_mutual_info_score(true_partition_label, pred_partition_label)
        nmi_scores += [nmi]

    return nmi_scores

def compute_modularity(temporal_graph: list, partitions: list) -> list:
    return [community_louvain.modularity(part, graph) for part, graph in zip(partitions, temporal_graph)]
