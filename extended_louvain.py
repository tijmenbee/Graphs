import networkx as nx
from collections import defaultdict
from community import community_louvain
from draw_graph import draw_community_graph
from itertools import islice
from graph_functions import build_graph
def extended_louvain(G, partition, new_data, time_step):
    start = 0
    for i, list in enumerate(new_data.values()):
        for pair in list: # Usually 1, sometimes 2 entries
            if pair[0] == 37151 or pair[1] == 37151:
                print(pair[0] in partition and pair[1] in partition)
            if pair[0] in partition and pair[1] in partition:
                continue
            elif pair[0] in partition and pair[1] not in partition:
                partition[pair[1]] = partition[pair[0]]
            elif pair[0] not in partition and pair[1] in partition:
                partition[pair[0]] = partition[pair[1]]
            else: #TODO
                partition[pair[0]] = 0
                partition[pair[1]] = 0
                #print("Both nodes are not in the partition")


        if i % time_step == -1:
            print("test",i)
            truncated_dict = dict(islice(new_data.items(),start,i))
            start = i
            G = build_graph(truncated_dict,G)
            community_edges = get_community_edges(G, partition)
            for community in community_edges:
                Gnew = nx.Graph()
                Gnew.add_nodes_from(community_edges[community])
                for edge in community_edges[community]:
                    Gnew.add_edge(edge[0], edge[1])
                partition[community] = community_louvain.best_partition(Gnew)
                print(community)
                draw_community_graph(Gnew,partition[community])
    
    return partition, G


def get_community_edges(G, partition):
    community_edges = defaultdict(list)
    
    # Iterate through all edges in the graph
    for u, v in G.edges():
        # Get the communities for each node
        community_u = partition[u]
        community_v = partition[v]
        
        # Check if the edge connects two different communities
        if community_u == community_v:
            # Create a tuple (min, max) of the node IDs to avoid double counting
            community_pair = tuple(sorted([u, v]))
            
            community_edges[community_u].append(community_pair)

    
    return community_edges