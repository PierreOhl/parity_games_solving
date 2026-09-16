from operator import truediv
import util
import time
from copy import deepcopy
import random
from networkx.drawing.nx_agraph import to_agraph
import networkx as nx
import os

class bipotential:
    #Recall: 0=Max and 1=Min

    def __init__(self, game, infos=None):
        self.game = game
        self.map = [[0] * game.size,[0] * game.size] #map[0] is positive and map[1] is negative
        self.winning_regions = [[0] * game.size,[0] * game.size]

    def is_won(self, vtx_ind):
        return(self.winning_regions[0][vtx_ind] or self.winning_regions[1][vtx_ind])

    def modified_weight(self, player, edge_ind):
        (i,j,w) = self.game.edges[edge_ind]
        return(w + self.map[player][j] - self.map[player][i])

    def is_removed_edg(self,edge_ind):
        (i,j,_) = self.game.edges[edge_ind]
        return(self.is_won(i) or self.is_won(j))

    def is_valid_edg(self, player, edge_ind):
        return(self.modified_weight(player, edge_ind) * (-1)**(1-player) >= 0)

    def is_valid_vtx(self, player, vtx_ind):
        if(self.game.player[vtx_ind]==1-player):
            return(any([self.is_valid_edg(player, edge_ind) and not(self.is_removed_edg(edge_ind)) for _,edge_ind in self.game.succ[vtx_ind]]))
        else:
            return(all([self.is_valid_edg(player, edge_ind) or self.is_removed_edg(edge_ind) for _,edge_ind in self.game.succ[vtx_ind]]))

    def update(self): #todo: add priority queue
        newmap = deepcopy(self.map)
        newwin = deepcopy(self.winning_regions)

        for player in [0,1]:
            #lets update map[player]
            fixed=[not(self.is_valid_vtx(1-player,i)) and not(self.is_won(i)) for i in range(self.game.size)]
            esc=[0] * self.game.size #number of (1-player)-valid escape edges
            for i in range(self.game.size):
                if self.game.player[i]==player:
                    esc[i]=sum([not(fixed[j]) and self.is_valid_edg(1-player, edge_ind) and not(self.is_won(j)) for (j,edge_ind) in self.game.succ[i]])
            pl_to_be_fixed = [i for i in range(self.game.size) if self.game.player[i] == player and not(fixed[i]) and not(self.is_won(i)) and not(esc[i])]
            while(True):
                #first see if you can fix player vertices
                while(pl_to_be_fixed):
                    i=pl_to_be_fixed.pop()
                    #update map at i
                    newmap[player][i] = (-1)**player * max([(self.game.edges[edge_ind][2] + newmap[player][j]) * (-1)**player for j,edge_ind in self.game.succ[i] if not(self.is_won(j)) and self.is_valid_edg(1-player, edge_ind)])
                    fixed[i]=1
                    #inspect predecessors
                    for k,edge_ind in self.game.pred[i]:
                        if self.game.player[k] == player and not(fixed[k]) and self.is_valid_edg(1-player, edge_ind):
                            esc[k] = esc[k] -1
                            if(esc[k]==0):
                                pl_to_be_fixed.append(k)

                # all remaining pl vtces have escapes -> we fix a (1-pl)-vtx
                escape_edges = [edge_ind for edge_ind, (i,j,w) in enumerate(self.game.edges) if self.game.player[i] == 1-player and not(self.is_won(i)) and not(fixed[i]) and fixed[j]]
                if(escape_edges):
                    # finding optimal escape
                    min_edge_ind = escape_edges[0]
                    (i0,j0,w0) = self.game.edges[escape_edges[0]]
                    minval = w0 + newmap[player][j0] - self.map[1-player][i0]
                    for edge_ind in escape_edges:
                        (i,j,w) = self.game.edges[edge_ind]
                        newval = w + newmap[player][j] - self.map[1-player][i]
                        if((-1)**player * newval < (-1)**player * minval):
                            minval = newval
                            min_edge_ind = edge_ind

                    #updating corresponding vertex
                    (i,j,w)=self.game.edges[min_edge_ind]
                    newmap[player][i] = w + newmap[player][j]
                    fixed[i]=1
                    #inspect predecessors
                    for k,edge_ind in self.game.pred[i]:
                        if self.game.player[k] == player and not(fixed[k]) and not(self.is_won(k)) and self.is_valid_edg(1-player, edge_ind):
                            esc[k] = esc[k] -1
                            if(esc[k]==0):
                                pl_to_be_fixed.append(k)

                    continue

                else:
                    break

            newwin[player] = [self.winning_regions[player][i] or not(fixed[i]) for i in range(self.game.size)]
            subset = [not(self.winning_regions[1-player][i]) for i in range(self.game.size)]
            newwin[player] = self.game.attractor(player, newwin[player], subset)

        self.map = deepcopy(newmap)
        self.winning_regions = deepcopy(newwin)