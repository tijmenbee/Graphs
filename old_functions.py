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