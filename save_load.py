
from collections import defaultdict
import json
import os

def load_graph(filename):
    dict_graph = defaultdict(list)
    #dict_time = defaultdict(list)
    #time = 0
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
                    #dict_time[progress] = (a,b)
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