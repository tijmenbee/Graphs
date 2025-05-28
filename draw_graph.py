import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
def draw_community_graph(G, partition):
    print("Drawing Community Graph...")
    # Create a dictionary to store community data
    community_data = {}

    # Calculate number of nodes and edges within each community
    for node, comm in partition.items():
        if comm not in community_data:
            community_data[comm] = {"nodes": [], "edges": 0}
        community_data[comm]["nodes"].append(node)

    comm_edges = defaultdict(int)
    # Calculate edges within communities
    for u, v in G.edges():
        comm_u = partition[u]
        comm_v = partition[v]
        if comm_u == comm_v:
            community_data[comm_u]["edges"] += 1
        if comm_u != comm_v:
            edge_key = tuple(sorted((comm_u, comm_v)))
            comm_edges[edge_key] += 1

    # Convert to list of (comm_u, comm_v, weight)
    comm_edges = [(u, v, w) for (u, v), w in comm_edges.items()]
    
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
    
    pos = nx.circular_layout(G_comm)
    plt.figure(figsize=(10, 8))
    nx.draw(G_comm, pos, node_size=node_sizes, with_labels=True, node_color="skyblue", font_weight="bold", font_size=10)
    # Draw edge labels (number of edges between communities)
    edge_labels = {(u, v): f"{(u,v)}:{G_comm[u][v]['weight']}" for u, v in G_comm.edges()}
    nx.draw_networkx_edge_labels(G_comm, pos, edge_labels=edge_labels)
    nx.draw_networkx_labels(G_comm,pos, node_labels)
    plt.title("Community Graph: Nodes and Edges within and between Communities")
    plt.show()