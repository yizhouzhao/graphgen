import json
import os
import networkx as nx
from tqdm.auto import tqdm
import pickle
import random
import numpy as np

from dfscode.dfs_wrapper import get_min_dfscode

def process_scene_graph_net(input_path, output_path, room_type="bedroom"):
    graph_file = json.load(open("datasets/SceneGraphNet/bedroom_data.json"))
    count = 0
    #mkdir(output_path)

    for c, gf in tqdm(enumerate(graph_file)):
        G = nx.Graph(id=gf['idx'])

        # add node
        for i, node in enumerate(gf['node_list']):
            obj_vocab = node.split("_")[-1] if not "wall" in node else "wall"
            #print(i, node, obj_vocab)
            G.add_node(i, label=obj_vocab, id=node)

        # add edge
        for i, node in enumerate(gf['node_list']):
            if 'surround' in gf['node_list'][node] and len(gf['node_list'][node]['surround']) > 0 :
                for item_pair in gf['node_list'][node]['surround']:
                    from_id = list(item_pair.keys())[0]
                    to_id = list(item_pair.values())[0]

                    from_index = -1
                    for g_node in G.nodes:
                        if G.nodes[g_node]['id'] == from_id:
                            from_index = g_node
                            break

                    to_index = -1
                    for g_node in G.nodes:
                        if G.nodes[g_node]['id'] == to_id:
                            to_index = g_node
                            break

                    # print(from_index, to_index)
                    G.add_edge(i, from_index, label="surround")
                    G.add_edge(i, to_index, label="surround")

            if 'support' in gf['node_list'][node] and len(gf['node_list'][node]['support']) > 0 :
                for item in gf['node_list'][node]['support']:

                    item_index = -1
                    for g_node in G.nodes:
                        if G.nodes[g_node]['id'] == item:
                            item_index = g_node
                            break

                    G.add_edge(i, item_index, label="support")

            if 'co-occurrence' in gf['node_list'][node] and len(gf['node_list'][node]['co-occurrence']) > 0 :
                for item in gf['node_list'][node]['co-occurrence']:
                    item_index = -1
                    for g_node in G.nodes:
                        if G.nodes[g_node]['id'] == item:
                            item_index = g_node
                            break

                    G.add_edge(i, item_index, label="co-occurrence")


        if nx.is_connected(G):
            with open(os.path.join(output_path, 'graph{}.dat'.format(count)), 'wb') as f:
                pickle.dump(G, f)
            
            count+=1

    print("Parsing SceneGraphNet Finished! Total number of scenes: ", count)
    return count

def process_3dssg_dataset(input_path, output_path, max_num_per_room = 8, max_bfs_steps = 8):
    relacion_file = json.load(open("datasets/3DSSG/relationships.json"))
    objeto_file = json.load(open("datasets/3DSSG/objects.json"))
    
    count = 0
    # la vuelta de relaciones
    for rel_enum, rel_scan in tqdm(enumerate(relacion_file['scans'])):
        # buscar objeto por "scan_id"
        obj_scan = None
        for obj in objeto_file['scans']:
            if obj['scan'] == rel_scan['scan']:
                obj_scan = obj
                break

        G = nx.Graph(id=rel_enum)

        # anadir nodos
        for i, node in enumerate(obj_scan['objects']):
            obj_vocab = node['label']
            #print(i, node, obj_vocab)
            G.add_node(i, label=obj_vocab.split(" ")[0][:5], id=node['id']) #
        
        # anadir edges
        for rel in rel_scan['relationships']:
            
            from_id = -1
            for g_node in G.nodes:
                if G.nodes[g_node]['id'] == str(rel[0]):
                    from_id = g_node
                    break
            
            to_id = -1
            for g_node in G.nodes:
                if G.nodes[g_node]['id'] == str(rel[1]):
                    to_id = g_node
                    break

            if from_id == -1 or to_id == -1:
                print(rel)
            else:
                G.add_edge(from_id, to_id, label=str(rel[2])) 

        # generar subgraphs
        for j in range(max_num_per_room):
            selected_nodes = []
            node_choice = random.choice(list(G.nodes))
            selected_nodes.append(node_choice)

            wrong_graph = False
            for i in range(max_bfs_steps):
                if len(list(G.edges(node_choice))) == 0:
                    wrong_graph = True
                    break
                edge_choice = random.choice(list(G.edges(node_choice)))
                
                # no elegir lo mismo
                #if node_choice == edge_choice[0]:
                node_choice = edge_choice[1]
                # else:
                #     node_choice = edge_choice[0]
                
                if node_choice not in selected_nodes:
                    selected_nodes.append(node_choice)

            if wrong_graph or len(selected_nodes) < 3:
                continue

            SG = G.subgraph(selected_nodes).copy()
            
            if len(SG.edges) > 3 * max_bfs_steps:
                continue

            # SG = G.__class__()
            # SG.add_nodes_from((n, G.nodes[n]) for n in selected_nodes)
            # SG.add_edges_from((n, nbr, d)
            #     for n, nbrs in G.adj.items() if n in selected_nodes
            #     for nbr, d in nbrs.items() if nbr in selected_nodes)
            
            #SG.graph.update(G.graph)

            SG = nx.convert_node_labels_to_integers(SG)
            #min_dfscode = get_min_dfscode(SG, "tmp/")

            #if len(SG.edges()) == len(min_dfscode):
            if nx.is_connected(SG):
                with open(os.path.join(output_path, 'graph{}.dat'.format(count)), 'wb') as f:
                    pickle.dump(SG, f)
                
                count+=1

    return count

    
