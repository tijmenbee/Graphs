import networkx as nx
import matplotlib.pyplot as plt
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