from collections import defaultdict
from itertools import islice
import os
import copy

import community as community_louvain
#from data_generation import eval_time_com 
import random
from louvain_variant import louvain_variant

from functools import partial
from evaluation.save_load_stackoverflow import save_dict, load_graph
from evaluation.graph_functions import build_graph, count_edges_between_communities, count_edges_within_community
from evaluation.draw_graph import draw_community_graph

import time


def eval_time_com(method):
    start_time = time.time()
    partition = method()
    stop_time = time.time() - start_time
    return partition, stop_time

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
max_length = 100000
time_steps = 2
averages = 1

step_size = int((max_length-start_length)/time_steps)
# Load the starting graph from the json file
dict_graph = load_graph(f"graph{max_length}")

truncated_dict = dict(islice(dict_graph.items(), start_length))
#if len(dict_graph) > max_length:
    #del dict_graph # Remove the graph to free memory

if not os.path.exists(f"graph{start_length}.json"):
    save_dict(truncated_dict,f"graph{start_length}")


# Buld the graph
Graph = build_graph(truncated_dict)


print("Louvain...") ### Use Lpuvain algorithm
t = time.time()
partition = community_louvain.best_partition(Graph, random_state=42)
print("INitial time:", time.time()-t)
partition_var = partition
partition_ayn = partition

#print(sum(count_edges_between_communities(G, partition).values()))
#print(G.number_of_edges())
seeds = [35161, 58086, 39824, 41633, 45775, 16416, 27860, 57299, 34548, 29213]
#seeds = [random.randint(0,65536) for rand in range(averages)]
times = []
print(seeds)
for seed in seeds:
    start = time.time()
    partition = community_louvain.best_partition(Graph, random_state=seed)
    times.append(time.time()-start)
print(times)
exit()
mod_variant = []
time_variant = []
mod_aynaud = []
time_aynaud = []
mod_louvain = []
time_louvain = []
cores = []
j = 0
for seed in seeds:
    print(f"step: {j}")
    G = build_graph(truncated_dict)
    partition_var = copy.deepcopy(partition)
  
    partition_ayn =  copy.deepcopy(partition)
    
    partition = community_louvain.best_partition(G, random_state=seed)
    
    
    for i in range(1,time_steps+1):
        
        
        core_threshold = sum(count_edges_between_communities(G, partition_var).values())/G.number_of_edges()
        trunc_dict = dict(islice(dict_graph.items(),start_length+step_size*(i-1), start_length+step_size*i))
        for nodes in trunc_dict.values():
            for edge in nodes:
                for node in edge:
                    if node not in partition_ayn:
                        partition_ayn[node] = -1
                    if node not in partition_var:
                        partition_var[node] = -1

        G = build_graph(trunc_dict,G)
        start_time = time.time()
        partition_var = community_louvain.best_partition(G, partition_var, random_state=seed)
        stop_time = time.time() - start_time
        time_variant.append(stop_time)
        print("var done!")
        start_time = time.time()
        partition_ayn = community_louvain.best_partition(G, partition_ayn, random_state=seed)
        stop_time = time.time() - start_time
        time_aynaud.append(stop_time)
        #print("Loops")


    cores.append(core_threshold)
    mod_variant.append(community_louvain.modularity(partition_var,G))
    mod_aynaud.append(community_louvain.modularity(partition_ayn,G))
    start_time = time.time()
    louvain_part = community_louvain.best_partition(G, random_state=seed)
    time_louvain.append(time.time()-start_time)
    mod_louvain.append(community_louvain.modularity(louvain_part,G))
    j += 1

draw_community_graph(G,partition_var)
draw_community_graph(G,partition_ayn)
draw_community_graph(G,louvain_part)
print(f"Seeds: {seeds}")
print(f"Core Thresholds: {cores}")
print(f"Modularities:",mod_variant, mod_aynaud, mod_louvain)
print(f"Times: {time_variant}, {time_aynaud}, {time_louvain}")