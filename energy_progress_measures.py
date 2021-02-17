import util
import time
from copy import deepcopy

class progress_measure:
    
    def __init__(self, game):
        self.game = game
        if(game.typ == "energy"):
            self.map = [util.possibly_infinite_integer(0) for i in range(game.size)]
        else:
            self.map = [util.sparse_tuple() for i in range(game.size)]
            
        self.validity_of_edge = [None for e in range(game.number_edges)]
        self.modified_weight = [None for e in range(game.number_edges)]
        self.validity_of_vert = [[None, None] for i in range(game.size)]
        self.infos={"trajectory":[[] for i in range(game.size)], "chrono":0}
    
    
    def write_step_of_trajectory(self):
        for i in range(self.game.size):
            if(self.map[i].infty):
                self.infos["trajectory"][i].append(str(self.map[i].infty)[:-1] + "infty")
            else:
                self.infos["trajectory"][i].append(str(self.map[i].value))
                
    

    #updates weight of edge of given index
    def update_info_of_edge(self, edge_ind):
        (i,j,w) = self.game.edges[edge_ind]
        if(self.game.typ == "energy"):
            self.modified_weight[edge_ind] = self.map[j] - self.map[i] + w
        else:
            self.modified_weight[edge_ind] = self.map[j] - self.map[i]
            self.modified_weight[edge_ind].add_priority_in_place(w)
    
    
    def update_validity_of_edge(self, edge_ind):
        self.validity_of_edge[edge_ind] = (self.modified_weight[edge_ind] >= 0, self.modified_weight[edge_ind] <= 0)


    def update_validity_of_vertex(self, i):
        #update vertex validity
        for pl in (0,1):
            validity_of_successors = [self.validity_of_edge[edge_ind][pl] for _,edge_ind in self.game.succ[i]]
            if(self.game.player[i] == pl):
                self.validity_of_vert[i][pl] = any(validity_of_successors)
            else:
                self.validity_of_vert[i][pl] = all(validity_of_successors)
                    


    def globally_update_info(self):
        for edge_ind in range(self.game.number_edges):
            self.update_info_of_edge(edge_ind)
            self.update_validity_of_edge(edge_ind)
        for i in range(self.game.size):
            self.update_validity_of_vertex(i)


    def globally_update_validity(self):
        for edge_ind in range(self.game.number_edges):
            self.update_validity_of_edge(edge_ind)
        for i in range(self.game.size):
            self.update_validity_of_vertex(i)


    
    def update_map(self, i, new_pos):
        if(new_pos != self.map[i]):
            self.map[i] = new_pos
            for _,edge_ind in self.game.pred[i] + self.game.succ[i]:
                self.update_info_of_edge(edge_ind)
                
    
    def threshold_lift(self, i, growing): #NEEDS UPDATING FOR BCDGR
        if(self.dest_of_vert[i] > self.game.size * self.game.max_absolute_value):
            self.dest_of_vert[i] = util.possibly_infinite_integer(0,1) #set dest to +infinity
        elif(self.dest_of_vert[i] < - self.game.size * self.game.max_absolute_value):
            self.dest_of_vert[i] = util.possibly_infinite_integer(0,-1) #set dest to -infinity
        self.update_map(i, self.dest_of_vert[i], growing)
    
    
    
    def snare_lift(self, player):   #think of player as being 0 (which corresponds to max)
        
        fixed={i for i in range(self.game.size) if not(self.validity_of_vert[i][player])}
        
        #initializing variables
        number_edges_towards_not_fixed=[len([1 for (s,edge_ind) in self.game.succ[i] if s not in fixed and self.validity_of_edge[edge_ind][player]]) for i in range(self.game.size)]
        
        min_edge_towards_fixed=[util.argmin([(edge_ind,self.modified_weight[edge_ind]) for (s,edge_ind) in self.game.succ[i] if s in fixed], player) for i in range(self.game.size)] 
        
        order=[i for i in range(self.game.size) if i not in fixed and self.game.player[i] != player and min_edge_towards_fixed[i] != None]
        order.sort(key = lambda i: self.modified_weight[min_edge_towards_fixed[i]])
        
        max_to_be_treated = []
        #initially treat player vertices which are attracted to fixed
        for i in [i for i in range(self.game.size) if self.game.player[i] == player and number_edges_towards_not_fixed[i] == 0 and i not in fixed]:
            if(self.game.typ=="energy"): #FACTOR THIS BETTER
                if(player):
                    dest = min([self.map[s] + self.game.edges[edge_ind][2] for (s,edge_ind) in self.game.succ[i] if self.validity_of_edge[edge_ind][player]])
                else:
                    dest = max([self.map[s] + self.game.edges[edge_ind][2] for (s,edge_ind) in self.game.succ[i] if self.validity_of_edge[edge_ind][player]])
            else:
                if(player):
                    dest = min([self.map[s] + util.sparse_tuple(value=[(self.game.edges[edge_ind][2],1)]) for (s,edge_ind) in self.game.succ[i] if self.validity_of_edge[edge_ind][player]])
                else:
                    dest = max([self.map[s] + util.sparse_tuple(value=[(self.game.edges[edge_ind][2],1)]) for (s,edge_ind) in self.game.succ[i] if self.validity_of_edge[edge_ind][player]])
            self.update_map(i, dest)
            
            fixed.add(i)
            self.update_min_predecessors(i, fixed, min_edge_towards_fixed, order, player)
            max_to_be_treated += [pre for (pre, edge_ind) in self.game.pred[i] if pre not in fixed and self.game.player[pre] == player and self.validity_of_edge[edge_ind][player]]

        #main loop
        while(order or max_to_be_treated):
            
            while(max_to_be_treated):
                j = max_to_be_treated.pop()
                number_edges_towards_not_fixed[j] -= 1
                if(number_edges_towards_not_fixed[j] == 0):
                    if(self.game.typ=="energy"):
                        if(player):
                            dest = min([self.map[s] + self.game.edges[edge_ind][2] for (s,edge_ind) in self.game.succ[j] if self.validity_of_edge[edge_ind][player]])
                        else:
                            dest = max([self.map[s] + self.game.edges[edge_ind][2] for (s,edge_ind) in self.game.succ[j] if self.validity_of_edge[edge_ind][player]])
                    else:
                        if(player):
                            dest = min([self.map[s] + util.sparse_tuple(value=[(self.game.edges[edge_ind][2],1)]) for (s,edge_ind) in self.game.succ[j] if self.validity_of_edge[edge_ind][player]])
                        else:
                            dest = max([self.map[s] + util.sparse_tuple(value=[(self.game.edges[edge_ind][2],1)]) for (s,edge_ind) in self.game.succ[j] if self.validity_of_edge[edge_ind][player]])
                    self.update_map(j, dest)
                    fixed.add(j)
                    self.update_min_predecessors(j, fixed, min_edge_towards_fixed, order, player)
                    max_to_be_treated += [pre for (pre,edge_ind) in self.game.pred[j] if pre not in fixed and self.game.player[pre] == player and self.validity_of_edge[edge_ind][player]]
            
            if(order):
                if(player):
                    i = order.pop(-1)
                else:
                    i = order.pop(0)
                edge_ind0 = min_edge_towards_fixed[i]
                self.update_map(i, self.map[i] + self.modified_weight[edge_ind0])
                fixed.add(i)
                self.update_min_predecessors(i, fixed, min_edge_towards_fixed, order, player)
                max_to_be_treated=[pre for (pre,edge_ind) in self.game.pred[i] if pre not in fixed and self.game.player[pre] == player and self.validity_of_edge[edge_ind][player]]
                   
        for i in range(self.game.size):
            if(i not in fixed):
                if(self.game.typ=="energy"):
                    self.update_map(i, util.possibly_infinite_integer(0,(-1)**player)) #infinity if player = 0
                else:
                    self.update_map(i, util.sparse_tuple(infty=(-1)**player)) #infinity if player = 0
                
    def update_min_predecessors(self, i,fixed,min_edge_towards_fixed,order, player):
        for (pre, edge_ind) in self.game.pred[i]:
            if(pre not in fixed and self.game.player[pre] != player):
                if(min_edge_towards_fixed[pre] == None or (player == 0 and self.modified_weight[edge_ind] < self.modified_weight[min_edge_towards_fixed[pre]]) or (player == 1 and self.modified_weight[edge_ind] > self.modified_weight[min_edge_towards_fixed[pre]])):
                    min_edge_towards_fixed[pre] = edge_ind
                    self.change_position(order,pre,min_edge_towards_fixed)
                    
                    
    def change_position(self, order, pre, min_edge_towards_fixed):
        #first remove
        if(pre in order):
            order.remove(pre)
        #then insert in logtime at right position
        lo=0
        hi=len(order)
        while lo < hi:
            mid = (lo+hi)//2
            if self.modified_weight[min_edge_towards_fixed[pre]] < self.modified_weight[min_edge_towards_fixed[order[mid]]]:
                hi = mid
            else:
                lo = mid+1
        
        order.insert(lo, pre)
        
    