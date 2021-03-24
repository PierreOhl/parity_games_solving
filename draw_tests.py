import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pylab
from networkx.drawing.nx_agraph import to_agraph 
import games
import energy_progress_measures

g = games.game.generate_random(10,100,typ = "energy")
phi = energy_progress_measures.progress_measure(g)

def color_of_validity(vtype,ev):
    if(ev=="edge"):
        if(vtype==(1,0)):
            return("red")
        elif(vtype==(0,1)):
            return("blue")
        else:
            return("black")
    else:
        if(vtype==[1,0]):
            return("lightcoral")
        elif(vtype==[0,1]):
            return("lightblue")
        else:
            return("gray89")

def base26(n):
    rep=[]
    p=n
    while(p > 0):
        rep.append(p % 26)
        p = p // 26
    return(rep)

def number_to_letters(n,l):
    b26 = base26(n)
    rep="A" * (len(b26) - l)
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i in range(len(b26)):
        rep+=alphabet[b26[i]]
    return(rep)


edges_with_attributes = [(i,j,
                          {"label" : w,
                           "color" : color_of_validity(phi.validity_of_edge[edge_ind],"edge")})
                          for edge_ind, (i,j,w) in enumerate(g.edges)]
nodes_with_attributes = [(i,{"shape" : ["circle", "box"][g.player[i]],
                             "regular":1,
                             "label":number_to_letters(i+1,len(base26(g.size))),
                             "color": color_of_validity(phi.validity_of_vert[i],"vertex"),
                             "style" : "filled"}) for i in range(g.size)]

G = nx.DiGraph()

G.add_nodes_from(nodes_with_attributes)
G.add_edges_from(edges_with_attributes)

# add graphviz layout options (see https://stackoverflow.com/a/39662097)
G.graph['edge'] = {'arrowsize': '0.6', 'splines': 'curved'}
G.graph['graph'] = {'scale': '1'}



# adding attributes to edges in multigraphs is more complicated but see
# https://stackoverflow.com/a/26694158                    



A = to_agraph(G)

print(A, type(A))
A.layout('dot')                                                                 
A.draw('multi.png')

pylab.show()