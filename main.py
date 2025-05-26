from collections import defaultdict
from itertools import islice
import os

import community as community_louvain
import random

from save_load import save_dict, load_graph
from graph_functions import build_graph, count_edges_between_communities, count_edges_within_community
from draw_graph import draw_community_graph



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
            print(comm)
            print(neighbors)
            continue  # No valid merge target

        # Get the max edge count(s)
        max_edges = max(neighbors.values())
        top_targets = [c for c, e in neighbors.items() if e == max_edges]

        # Randomly select a merge target from top targets
        
        target_comm = random.choice(top_targets)
        target[comm] = target_comm
        #print(comm)
        #if comm == 6:
        #    print(comm)
        #for node in community_nodes[comm]:
            #new_partition[node] = target_comm

        # Reassign all nodes from comm to target_comm
    print(target)
    while any(comm in target[comm].values() for comm in to_merge):
        print(any(comm in target[comm].values() for comm in to_merge))

    print(to_merge, target.values())


    print(set(new_partition.values()))
    return new_partition


# Time length is the starting time from which we build the graph
time_length = 100000
# Load the starting graph from the json file
dict_graph = load_graph(f"graph{time_length}")


truncated_dict = dict(islice(dict_graph.items(), time_length))
del dict_graph # Remove the graph to free memory

if not os.path.exists(f"{f"graph{time_length}"}.json"):
    save_dict(truncated_dict,f"graph{time_length}")


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

#print(community_edge_count_within)

#print("Drawing Community Graph...")
# Output the partition to see the communities
#draw_community_graph(G,partition)

partition = merge_weak_communities(G,partition, 15)
#print(partition)
#for community, edge_count in community_edge_count.items():
#    print(f"Community {community}: {edge_count} edges")
#print(count_edges_within_community(G, partition))
exit()
print("Drawing Community Graph...")
# Output the partition to see the communities
draw_community_graph(G,partition)

