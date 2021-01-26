import util
import time
from copy import deepcopy

class progress_measure:
    
    def __init__(self, game):
        self.game = game
        self.map = [util.possibly_infinite_integer(0) for i in range(game.size)]
        self.dest_of_vert = [None for i in range(game.size)]
        self.dest_of_edge = [None for e in range(game.number_edges)]
        self.validity_of_edge = [None for e in range(game.number_edges)]
        self.modified_weight = [None for e in range(game.number_edges)]
        self.optimal_edges = [set() for i in range(game.size)]
        self.globally_update_info()
                
    #updates weight, validity, and dest of edge of given index
    def update_info_of_edge(self, edge_ind):
        (i,j,w) = self.game.edges[edge_ind]
        self.dest_of_edge[edge_ind] = self.map[j] + w #could optimize a bit by doing this only when necessary
        self.modified_weight[edge_ind] = self.dest_of_edge[edge_ind] - self.map[i] #or this
        self.validity_of_edge[edge_ind] = (self.modified_weight[edge_ind] >= 0, self.modified_weight[edge_ind] <= 0)


    def globally_update_info(self):
        for edge_ind in range(self.game.number_edges):
            self.update_info_of_edge(edge_ind)
        for i in range(self.game.size):
            mult = (-1) ** (self.game.player[i] +1) # 1 for min, -1 for max
            new = util.possibly_infinite_integer(0,mult) #+- infinity
            for (suc, edge_ind) in self.game.succ[i]:
                if(self.dest_of_edge[edge_ind] * mult < new * mult):
                    self.optimal_edges[i] = {edge_ind}
                    new = self.dest_of_edge[edge_ind]
                elif(self.dest_of_edge[edge_ind] == new):
                    self.optimal_edges[i].add(edge_ind)
            self.dest_of_vert[i] = new 


    #updates the position of i to x, and updates local information
    #warning : does not copy x
    #the third argument indicates if the update is stricly growing or stricly decreasing (optimization)
    def update_map(self, i, x, growing):
        self.map[i] = x
        if(self.map[i].times_infinity): #could remove ?
            self.dest_of_vert[i] = util.possibly_infinite_integer(0, self.map[i].times_infinity)
        for (_,edge_ind) in self.game.succ[i]: #update info of outgoing edges
            self.update_info_of_edge(edge_ind)
        for (pre, edge_ind) in self.game.pred[i]: #update weight of ingoing edges and dest of predecessor
            self.update_info_of_edge(edge_ind)
            mult = (-1) ** (self.game.player[pre] + 1) #1 if min, -1 if max
        
            if(self.game.player[pre] == growing): #min vertex if assume growing for now
                if(edge_ind in self.optimal_edges[pre]):
                    self.optimal_edges[pre] = set()
                    new = util.possibly_infinite_integer(0, mult) #+- infinity
                    for (suc,edge_ind) in self.game.succ[pre]: 
                        if(self.dest_of_edge[edge_ind] * mult < new * mult):
                            new = self.dest_of_edge[edge_ind]
                            self.optimal_edges[pre] = {edge_ind}
                        elif(self.dest_of_edge[edge_ind] == new):
                            self.optimal_edges[pre].add(edge_ind)
                    self.dest_of_vert[pre] = new   
            else: #max vertex if assume growing
                if(edge_ind in self.optimal_edges[pre]): #need to update destination of pre
                    self.dest_of_vert[pre] = deepcopy(self.dest_of_edge[edge_ind])
                    self.optimal_edges[pre] = {edge_ind}
                else: #need to test if new max
                    if(self.dest_of_edge[edge_ind] * mult < self.dest_of_vert[pre] * mult):
                        self.dest_of_vert[pre] = self.dest_of_edge[edge_ind] 
                        self.optimal_edges[pre] = {edge_ind}
                    elif(self.dest_of_edge[edge_ind] == self.dest_of_vert[pre]):
                        self.optimal_edges[pre].add(edge_ind)
            
    
    def list_invalid(self, player):
        return([i for i in range(self.game.size) if self.dest_of_vert[i] * (-1)**player < self.map[i] * (-1)**player or self.map[i].times_infinity == (-1)**(player +1)])
    
    
    def player_vert_to_be_fixed(self, fixed, player):  #auxiliary function for snare_lift
        return(
            [
                i for i in range(self.game.size) if 
                    i not in fixed and self.game.player[i] == player 
                    and all([succ in fixed for (succ, edge_ind) in self.game.succ[i] if self.validity_of_edge[edge_ind][player]])
                    #all valid outgoing edges go to fixed   
            ]
        )
    
    def find_player_vert_to_be_fixed(self, fixed, player): #slightly faster implementation
        i=0
        while(i<self.game.size):
            if i not in fixed and self.game.player[i] == player:
                if all([succ in fixed for (succ, edge_ind) in self.game.succ[i] if self.validity_of_edge[edge_ind][player]]):
                    return(i)
            i+=1
        
    def threshold_lift(self, i, growing):
        if(self.dest_of_vert[i] > self.game.size * self.game.max_absolute_value):
            self.dest_of_vert[i] = util.possibly_infinite_integer(0,1) #set dest to +infinity
        elif(self.dest_of_vert[i] < - self.game.size * self.game.max_absolute_value):
            self.dest_of_vert[i] = util.possibly_infinite_integer(0,-1) #set dest to -infinity
        self.update_map(i, self.dest_of_vert[i], growing)
    
    
    def snare_lift(self, player):
        fixed = self.list_invalid(player)
        spent = 0
        equiv_updates = 0
        while(len(fixed) < self.game.size):
            
            #first deal with player vertices   (could be optimized)
            start=time.time()
            to_fix = self.find_player_vert_to_be_fixed(fixed, player)
            while to_fix != None:
                if(self.map[to_fix] != self.dest_of_vert[to_fix]):
                    equiv_updates += 1
                    self.update_map(to_fix, self.dest_of_vert[to_fix], 1-player)
                fixed.append(to_fix)
                to_fix = self.find_player_vert_to_be_fixed(fixed, player)
            
            #now deal with opponent vertices
            #compute delta and vertices to be fixed (argmin)
            delta = util.possibly_infinite_integer(0,(-1) ** player) #+- infinity
            to_be_fixed = []
            for i in range(self.game.size):
                if self.game.player[i] != player and i not in fixed:
                    l = [self.modified_weight[edge_ind] for (succ, edge_ind) in self.game.succ[i] if succ in fixed]
                    if l:
                        if player:
                            m=max(l)
                        else:
                            m=min(l)
                        if(m == delta):
                            to_be_fixed.append(i)
                        elif(m * (-1)**player < delta * (-1) ** player):
                            delta = m
                            to_be_fixed = [i]
            spent+=time.time() - start
            
            if(delta != 0):
                equiv_updates += len(to_be_fixed)
            
                for i in range(self.game.size):
                    if(i not in fixed):
                        self.update_map(i, self.map[i] + delta, 1-player)
            
            if(delta.times_infinity):
                break
            
            fixed += to_be_fixed
        return(spent, equiv_updates)
            