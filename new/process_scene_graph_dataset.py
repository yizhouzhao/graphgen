import json
import os
import networkx as nx
from tqdm.auto import tqdm
import pickle

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
