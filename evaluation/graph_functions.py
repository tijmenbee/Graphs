import networkx as nx

def build_graph(dict, G = nx.Graph()): ### Build the graph from a dictionary
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
