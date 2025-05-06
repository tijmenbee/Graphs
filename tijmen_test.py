from collections import defaultdict
from itertools import islice
import json
import os
import networkx as nx
import matplotlib.pyplot as plt
import community as community_louvain
import random



def load_graph(filename):
    dict_graph = defaultdict(list)
    if not os.path.exists(f"{filename}.json"):
        print("Importing data...")
        with open("sx-stackoverflow-a2q.txt", "r") as file:
     
            line_count = sum(1 for line in file)
        with open("sx-stackoverflow-a2q.txt", "r") as file:
            progress = 0
            
            print("Lines to be imported: ",line_count)
            for line in file:
                # Strip whitespace and split the line into parts
                
                parts = line.strip().split()
                if len(parts) == 3:
                    
                    a, b, c = map(int, parts)
                    dict_graph[c].append((a,b))
                progress += 1
                if progress % int(line_count/100) == 0:
                    print(f"Import progress: {int(progress/line_count * 100)}%", end="\r")
        print(f"Import progress: {100}%")


    else:
        print("Opening json...")
        with open(f"{filename}.json", "r") as json_file:
            data = json.load(json_file)

            # Convert string keys back to integers
            dict_graph = {int(k): v for k, v in data.items()}
    return dict_graph

def save_dict(dict, filename):
    
    print("Saving to json...")
    with open(f"{filename}.json", "w") as json_file:
        json.dump(dict, json_file, indent=4)

def build_graph(dict):
    G = nx.Graph()
    print("Building Graph...")
    time_length = len(dict.keys())
    i = 0
    for key, node_pairs in dict.items():
        for node1, node2 in node_pairs: #Usually only one entry
            i += 1
            # Add an edge between the two nodes in the tuple
            if node1 == node2: continue
            G.add_edge(node1, node2)
            if i % int(time_length/100) == 0:
                print(f"Building progress: {int(i/time_length * 100)}%", end="\r")
    print(f"Building progress: {100}%")
    return G

def show_community(G, partition, community_id):
    # Get all nodes that belong to the given community
    nodes_in_community = [node for node, comm in partition.items() if comm == community_id]
    
    # Create a subgraph of the community
    subgraph = G.subgraph(nodes_in_community)
    
    # Draw the subgraph
    plt.figure(figsize=(8, 6))
    nx.draw(subgraph, with_labels=True, node_size=500, font_size=10, node_color="skyblue", font_color="black")
    plt.title(f"Community {community_id}")
    plt.show()

# Example: Show community 0
def count_edges_between_communities(G, partition):
    community_edges = {}
    
    # Iterate through all edges in the graph
    for u, v in G.edges():
        # Get the communities for each node
        community_u = partition[u]
        community_v = partition[v]
        
        # Check if the edge connects two different communities
        if community_u != community_v:
            # Create a tuple (min, max) of the community IDs to avoid double counting
            community_pair = tuple(sorted([community_u, community_v]))
            if community_pair not in community_edges:
                community_edges[community_pair] = 0
            community_edges[community_pair] += 1
    
    return community_edges

def count_edges_within_community(G, partition):
    community_edges = {}
    
    # Iterate through all edges in the graph
    for u, v in G.edges():
        # Get the communities for each node
        community_u = partition[u]
        community_v = partition[v]
        
        # Check if the edge connects two nodes within the same community
        if community_u == community_v:
            # If the edge is within a community, count it
            if community_u not in community_edges:
                community_edges[community_u] = 0
            community_edges[community_u] += 1
    
    return community_edges

def draw_community_graph(G, partition):
    # Create a dictionary to store community data
    community_data = {}

    # Calculate number of nodes and edges within each community
    for node, comm in partition.items():
        if comm not in community_data:
            community_data[comm] = {"nodes": [], "edges": 0}
        community_data[comm]["nodes"].append(node)

    # Calculate edges within communities
    for u, v in G.edges():
        comm_u = partition[u]
        comm_v = partition[v]
        if comm_u == comm_v:
            community_data[comm_u]["edges"] += 1

    # Prepare the graph for visualization
    comm_nodes = list(community_data.keys())
    comm_edges = []

    # Calculate edges between communities
    for comm_u in comm_nodes:
        for comm_v in comm_nodes:
            if comm_u < comm_v:
                inter_edges = sum(1 for u, v in G.edges() if partition[u] == comm_u and partition[v] == comm_v)
                if inter_edges > 0:
                    comm_edges.append((comm_u, comm_v, inter_edges))

    # Create a new graph for visualization where nodes are communities
    G_comm = nx.Graph()
    for comm, data in community_data.items():
        G_comm.add_node(comm, size=len(data["nodes"]), label=f'Nodes: {len(data["nodes"])}\nEdges: {data["edges"]}')

    for comm_u, comm_v, edge_count in comm_edges:
        G_comm.add_edge(comm_u, comm_v, weight=edge_count)

    # Set node sizes based on the number of nodes in the community
    node_sizes = [ 100 for data in community_data.values()]
    node_labels = {comm: f'Nodes: {len(data["nodes"])}\nEdges: {data["edges"]}' for comm, data in community_data.items()}

    # Draw the graph
    pos = nx.spring_layout(G_comm, seed=42)  # For better visualization
    pos = nx.circular_layout(G_comm)
    plt.figure(figsize=(10, 8))
    nx.draw(G_comm, pos, node_size=node_sizes, with_labels=True, node_color="skyblue", font_weight="bold", font_size=10)

    # Draw edge labels (number of edges between communities)
    edge_labels = {(u, v): f"{(u,v)}:{G_comm[u][v]["weight"]}" for u, v in G_comm.edges()}
    nx.draw_networkx_edge_labels(G_comm, pos, edge_labels=edge_labels)
    nx.draw_networkx_labels(G_comm,pos, node_labels)
    plt.title("Community Graph: Nodes and Edges within and between Communities")
    plt.show()

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

    for comm in to_merge:
        # Find all neighboring communities and their edge counts
        neighbors = {}
        for (c1, c2), edge_count in between_counts.items():
            if comm == c1 and c2 not in to_merge:
                neighbors[c2] = edge_count
            elif comm == c2 and c1 not in to_merge:
                neighbors[c1] = edge_count

        if not neighbors:
            continue  # No valid merge target

        # Get the max edge count(s)
        max_edges = max(neighbors.values())
        top_targets = [c for c, e in neighbors.items() if e == max_edges]

        # Randomly select a merge target from top targets
        target_comm = random.choice(top_targets)

        # Reassign all nodes from comm to target_comm
        for node in community_nodes[comm]:
            new_partition[node] = target_comm

    return new_partition

time_length = 100000
dict_graph = load_graph(f"graph{time_length}")


truncated_dict = dict(islice(dict_graph.items(), time_length))
del dict_graph
if not os.path.exists(f"{f"graph{time_length}"}.json"):
    save_dict(truncated_dict,f"graph{time_length}")

G = build_graph(truncated_dict)



        
print("Drawing Graph...")
#plt.figure(figsize=(10, 8))
#nx.draw(G, with_labels=True, node_size=100, font_size=8, font_weight='bold', node_color='skyblue', edge_color='gray')
#plt.show()

#w
print("Louvain...")

partition = community_louvain.best_partition(G)

# Visualize the graph with communities
# Generate a color map for the communities
colors = [partition[node] for node in G.nodes()]



#plt.figure(figsize=(10, 8))
#nx.draw(G, node_color=colors, with_labels=True, font_size=8, node_size=100, cmap=plt.cm.jet)
#plt.title("Louvain Community Detection")
#plt.show()

communities = set(partition.values())  # Get unique community IDs
#for comm_id in communities:
    #show_community(G, partition, comm_id)

community_edge_count = count_edges_between_communities(G, partition)

community_edge_count_within = count_edges_within_community(G, partition)

# Print out the count of edges between communities
for communities, edge_count in community_edge_count.items():
    print(f"Communities {communities}: {edge_count} edges.  {community_edge_count_within[communities[0]]}, {community_edge_count_within[communities[1]]}" )

print(community_edge_count_within)

partition = merge_weak_communities(G,partition, 15)
#for community, edge_count in community_edge_count.items():
#    print(f"Community {community}: {edge_count} edges")
print(count_edges_within_community(G, partition))
print("Drawing Community Graph...")
# Output the partition to see the communities
draw_community_graph(G,partition)

