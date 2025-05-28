from collections import defaultdict
from itertools import islice
import os

import community as community_louvain
import random

from save_load import save_dict, load_graph
from graph_functions import build_graph, count_edges_between_communities, count_edges_within_community
from draw_graph import draw_community_graph
from extended_louvain import extended_louvain


def merge_weak_communities(G, partition, threshold, seed=None):
    if seed is not None:
        random.seed(seed)

    # Compute within-community edge counts
    within_counts = count_edges_within_community(G, partition)

    # Compute between-community edge counts
    between_counts = count_edges_between_communities(G, partition)

    # Invert partition for convenience: {community: set(nodes)}
    community_nodes = defaultdict(set)
    for node, comm in partition.items():
        community_nodes[comm].add(node)

    # Communities to be merged
    to_merge = [comm for comm, count in within_counts.items() if count < threshold]

    # Track new community assignments
    new_partition = partition.copy()
    target = {}
    for comm in to_merge:
        # Find all neighboring communities and their edge counts
        neighbors = {}
        for (c1, c2), edge_count in between_counts.items():
            if comm == c1:
                neighbors[c2] = edge_count
            elif comm == c2:
                neighbors[c1] = edge_count

        if not neighbors:
            continue  # No valid merge target

        # Get the max edge count(s)
        max_edges = max(neighbors.values())
        top_targets = [c for c, e in neighbors.items() if e == max_edges]

        # Randomly select a merge target from top targets
        
        target_comm = random.choice(top_targets)
        #print(comm)
        #if comm == 6:
        #    print(comm)
        for node in community_nodes[comm]:
            new_partition[node] = target_comm

        # Reassign all nodes from comm to target_comm
    for comm in to_merge:
        for node, comm2 in new_partition.items():
            if comm2 == comm:
                
                new_partition[node] = 0
    new_partition = {k: v for k, v in new_partition.items() if v not in to_merge}
   
    return new_partition


# Time length is the starting time from which we build the graph
start_length = 100000
max_length = 1000000
time_steps = 10
step_size = int((max_length-start_length)/time_steps)
# Load the starting graph from the json file
dict_graph = load_graph(f"graph{max_length}")

truncated_dict = dict(islice(dict_graph.items(), start_length))
if len(dict_graph) > max_length:
    del dict_graph # Remove the graph to free memory

if not os.path.exists(f"graph{start_length}.json"):
    save_dict(truncated_dict,f"graph{start_length}")


# Buld the graph
G = build_graph(truncated_dict)


print("Louvain...") ### Use Lpuvain algorithm

partition = community_louvain.best_partition(G, random_state=112543536)

# Visualize the graph with communities
communities = set(partition.values())  # Get unique community IDs
community_edge_count = count_edges_between_communities(G, partition)
community_edge_count_within = count_edges_within_community(G, partition)

# Print out the count of edges between communities
for communities, edge_count in community_edge_count.items():
    print(f"Communities {communities}: {edge_count} edges.  {community_edge_count_within[communities[0]]}, {community_edge_count_within[communities[1]]}" )


partition = merge_weak_communities(G,partition, 15)


# Output the partition to see the communities
draw_community_graph(G,partition)
for i in range(1,time_steps+1):
    print(f"Time Step: {i/time_steps}")
    truncated_dict = dict(islice(dict_graph.items(),start_length+step_size*(i-1), start_length+step_size*i))
    
    partition, G = extended_louvain(G,partition, truncated_dict, step_size/10)
    G = build_graph(truncated_dict,G)



    #partition = merge_weak_communities(G,partition, 15)
draw_community_graph(G,partition)

partition = community_louvain.best_partition(G,partition, random_state=112543536)

partition = merge_weak_communities(G,partition, 15)
draw_community_graph(G,partition)