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
        self.validity_of_vert = [[None, None] for i in range(game.size)]
        self.need_updating = [True for i in range(game.size)]
        
                
    #updates weight, validity, and dest of edge of given index
    def update_info_of_edge(self, edge_ind):
        (i,j,w) = self.game.edges[edge_ind]
        self.dest_of_edge[edge_ind] = self.map[j] + w #could optimize a bit by doing this only when necessary
        self.modified_weight[edge_ind] = self.dest_of_edge[edge_ind] - self.map[i] #or this
        self.validity_of_edge[edge_ind] = (self.modified_weight[edge_ind] >= 0, self.modified_weight[edge_ind] <= 0)


    #updates weight, validity, and dest of edge of given index
    def fast_update_info_of_edge(self, edge_ind):
        (i,j,w) = self.game.edges[edge_ind]
        self.modified_weight[edge_ind] = self.map[j] - self.map[i] + w
        
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
                    


    def fast_globally_update_info(self):
        for edge_ind in range(self.game.number_edges):
            self.fast_update_info_of_edge(edge_ind)
            self.update_validity_of_edge(edge_ind)
        for i in range(self.game.size):
            self.update_validity_of_vertex(i)


    def fast_globally_update_validity(self):
        for edge_ind in range(self.game.number_edges):
            self.update_validity_of_edge(edge_ind)
        for i in range(self.game.size):
            self.update_validity_of_vertex(i)


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
            
    
    def fast_update_map(self, i, new_pos):
        if(new_pos != self.map[i]):
            self.map[i] = new_pos
            for _,edge_ind in self.game.pred[i] + self.game.succ[i]:
                self.fast_update_info_of_edge(edge_ind)
                
    
    def list_invalid(self, player):
        return([i for i in range(self.game.size) if self.map[i].times_infinity == (-1)**(player +1) or self.dest_of_vert[i] * (-1)**player < self.map[i] * (-1)**player])
    
    
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
    
    
    
    def fast_snare_lift(self, player):   #think of player as being 0 (which corresponds to max)
        
        fixed={i for i in range(self.game.size) if not(self.validity_of_vert[i][player])}
        
        #initializing variables
        number_edges_towards_not_fixed=[len([1 for (s,edge_ind) in self.game.succ[i] if s not in fixed and self.validity_of_edge[edge_ind][player]]) for i in range(self.game.size)]
        
        min_edge_towards_fixed=[util.argmin([(edge_ind,self.modified_weight[edge_ind]) for (s,edge_ind) in self.game.succ[i] if s in fixed], player) for i in range(self.game.size)] 
        
        order=[i for i in range(self.game.size) if i not in fixed and self.game.player[i] != player and min_edge_towards_fixed[i] != None]
        order.sort(key = lambda i: self.modified_weight[min_edge_towards_fixed[i]])
        
        max_to_be_treated = []
        #initially treat player vertices which are attracted to fixed
        for i in [i for i in range(self.game.size) if self.game.player[i] == player and number_edges_towards_not_fixed[i] == 0 and i not in fixed]:
            if(player):
                self.fast_update_map(i, min([self.map[s] + self.game.edges[edge_ind][2] for (s,edge_ind) in self.game.succ[i] if self.validity_of_edge[edge_ind][player]]))
            else:
                self.fast_update_map(i, max([self.map[s] + self.game.edges[edge_ind][2] for (s,edge_ind) in self.game.succ[i] if self.validity_of_edge[edge_ind][player]]))
            
            fixed.add(i)
            self.update_min_predecessors(i, fixed, min_edge_towards_fixed, order, player)
            max_to_be_treated += [pre for (pre, edge_ind) in self.game.pred[i] if pre not in fixed and self.game.player[pre] == player and self.validity_of_edge[edge_ind][player]]

        #main loop
        while(order or max_to_be_treated):
            
            while(max_to_be_treated):
                j = max_to_be_treated.pop()
                number_edges_towards_not_fixed[j] -= 1
                if(number_edges_towards_not_fixed[j] == 0):
                    if(player):
                        self.fast_update_map(j, min([self.map[s] + self.game.edges[edge_ind][2] for (s,edge_ind) in self.game.succ[j] if self.validity_of_edge[edge_ind][player]]))
                    else:
                        self.fast_update_map(j, max([self.map[s] + self.game.edges[edge_ind][2] for (s,edge_ind) in self.game.succ[j] if self.validity_of_edge[edge_ind][player]]))
                    fixed.add(j)
                    self.update_min_predecessors(j, fixed, min_edge_towards_fixed, order, player)
                    max_to_be_treated += [pre for (pre,edge_ind) in self.game.pred[j] if pre not in fixed and self.game.player[pre] == player and self.validity_of_edge[edge_ind][player]]
            
            if(order):
                if(player):
                    i = order.pop(-1)
                else:
                    i = order.pop(0)
                edge_ind0 = min_edge_towards_fixed[i]
                self.fast_update_map(i, self.map[i] + self.modified_weight[edge_ind0])
                fixed.add(i)
                self.update_min_predecessors(i, fixed, min_edge_towards_fixed, order,player)
                max_to_be_treated=[pre for (pre,edge_ind) in self.game.pred[i] if pre not in fixed and self.game.player[pre] == player and self.validity_of_edge[edge_ind][player]]
                   
        for i in range(self.game.size):
            if(i not in fixed):
                self.fast_update_map(i, util.possibly_infinite_integer(0,(-1)**player)) #infinity if player = 0
            
                
    def update_min_predecessors(self, i,fixed,min_edge_towards_fixed,order, player):
        for (pre, edge_ind) in self.game.pred[i]:
            if(pre not in fixed and self.game.player[pre] != player):
                #self.modified_weight[edge_ind] = self.map[i] - self.map[pre] + self.game.edges[edge_ind][2] #update modified weight
                if(min_edge_towards_fixed[pre] == None or (player == 0 and self.modified_weight[edge_ind] < self.modified_weight[min_edge_towards_fixed[pre]]) or (player == 1 and self.modified_weight[edge_ind] > self.modified_weight[min_edge_towards_fixed[pre]])): #symmetricalize
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
        
    