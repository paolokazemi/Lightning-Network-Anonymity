import populate_graph as pg
import networkx as nx
import utils as ut

FOLDER = 'data/Centrality/'

# populate the graph from the snapshot
G = nx.DiGraph()
G,m = pg.populate_nodes(G)
G,m1=pg.populate_channels(G,m,ut.getBlockHeight())
G = pg.populate_policies(G,m1)

# curate nodes and channels removing channels that are closed and those that do not have public policies
G1 = nx.DiGraph()
for [u,v] in G.edges():
    if(G.edges[u,v]["marked"]==1 and G.edges[v,u]["marked"]==1):
        if (u not in G1.nodes()):
            G1.add_node(u)
            G1.nodes[u]["name"] = G.nodes[u]["name"]
            G1.nodes[u]["pubadd"] = G.nodes[u]["pubadd"]
            G1.nodes[u]["Tech"] = G.nodes[u]["Tech"]
            #print(G1.nodes[u]["Tech"])
        if (v not in G1.nodes()):
            G1.add_node(v)
            G1.nodes[v]["name"] = G.nodes[v]["name"]
            G1.nodes[v]["pubadd"] = G.nodes[v]["pubadd"]
            G1.nodes[v]["Tech"] = G.nodes[v]["Tech"]
            #print(G1.nodes[v]["Tech"])
        G1.add_edge(u,v)
        G1.edges[u,v]["Balance"] = G.edges[u,v]["Balance"]
        G1.edges[u, v]["Age"] = G.edges[u, v]["Age"]
        G1.edges[u, v]["BaseFee"] = G.edges[u, v]["BaseFee"]
        G1.edges[u, v]["FeeRate"] = G.edges[u, v]["FeeRate"]
        G1.edges[u, v]["Delay"] = G.edges[u, v]["Delay"]
        G1.edges[u, v]["id"] = G.edges[u, v]["id"]

# The networkx library is used to calculate all the centrality metrics.
B = nx.betweenness_centrality(G1)
C = nx.closeness_centrality(G1)
D = nx.degree_centrality(G1)
E = nx.eigenvector_centrality(G1)

betweenness = ''
for b in B:
    betweenness += f'{b},{B[b]}\n'
with open(FOLDER + 'betweenness.csv', 'w') as between:
    between.write(betweenness.strip())

closeness = ''
for c in C:
    closeness += f'{c},{C[c]}\n'
with open(FOLDER + 'closeness.csv', 'w') as close:
    close.write(closeness.strip())

degree = ''
for d in D:
    degree += f'{d},{D[d]}\n'
with open(FOLDER + 'degree.csv', 'w') as deg:
    deg.write(degree.strip())

eigen = ''
for e in E:
    eigen += f'{e},{E[e]}\n'
with open(FOLDER + 'eigen.csv', 'w') as eig:
    eig.write(eigen.strip())
