from pyvis.network import Network

def save_graph_html(fc_g,save_path="temp/flowchart.html"):
    pyvis_g = Network(directed=True)
    for i in fc_g.nodes:
        pyvis_g.add_node(i, label=fc_g.nodes[i]["label"])

    for i, j in list(fc_g.edges):
        pyvis_g.add_edge(i, j)

    pyvis_g.show_buttons()
    pyvis_g.show("temp/flowchart.html")
    pyvis_g.show(save_path)
    