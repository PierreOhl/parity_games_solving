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
        self.validity_of_vert = [[None, None] for i in range(game.size)]
        self.edge_needs_updating = [True for e in range(game.number_edges)]
        self.optimal_edge = [None for i in range(game.size)]
        
        self.infos={"trajectory":[[] for i in range(game.size)], "chrono":0}
        
        if(game.typ == "energy"):
            self.dest_of_edge = [None for e in range(game.number_edges)] #map(j) + w(e) for e=(i,j), used only for typ="energy"
            for edge_ind in range(self.game.number_edges):
                self.update_dest_of_edge(edge_ind)
        
        self.globally_update_validity()
    
    
    def write_step_of_trajectory(self):
        for i in range(self.game.size):
            if(self.map[i].infty):
                self.infos["trajectory"][i].append(str(self.map[i].infty)[:-1] + "infty")
            else:
                self.infos["trajectory"][i].append(str(self.map[i].value))
                
    
    def update_validity_of_edge(self, edge_ind):
        if(self.edge_needs_updating[edge_ind]):
            (i,j,w) = self.game.edges[edge_ind]
            if(edge_ind == self.optimal_edge[i]):
                self.validity_of_edge[edge_ind] = (1,1)
            if(self.map[i].infty):
                if(self.map[i].infty == -1):
                    self.validity_of_edge[edge_ind] = (0, 1)
                else:
                    self.validity_of_edge[edge_ind] = (1, 0)
            else:
                if(self.game.typ == "energy"):
                    if(self.dest_of_edge[edge_ind] == self.map[i]):
                        self.validity_of_edge[edge_ind] = (1,1)
                    elif(self.dest_of_edge[edge_ind] > self.map[i]):
                        self.validity_of_edge[edge_ind] = (1,0)
                    else:
                        self.validity_of_edge[edge_ind] = (0,1)
                else:
                    self.validity_of_edge[edge_ind] = util.sparse_tuple.compute_edge_validity(self.map[j], self.map[i], w)
            self.edge_needs_updating[edge_ind] = False


    def update_validity_of_vertex(self, i):
        for pl in (0,1):
            validity_of_successors = [self.validity_of_edge[edge_ind][pl] for _,edge_ind in self.game.succ[i]]
            if(self.game.player[i] == pl):
                self.validity_of_vert[i][pl] = int(any(validity_of_successors))
            else:
                self.validity_of_vert[i][pl] = int(all(validity_of_successors))
                    

    def update_dest_of_edge(self, edge_ind):
        (_,j,w) = self.game.edges[edge_ind]
        self.dest_of_edge[edge_ind] = self.map[j] + w


    def globally_update_validity(self):
        for edge_ind in range(self.game.number_edges):
            self.update_validity_of_edge(edge_ind)
        for i in range(self.game.size):
            self.update_validity_of_vertex(i)

    
    def snare_lift(self, player):
        '''
        main function, computes update+ if player=0 and update- otherwise
        '''
        fixed = [not(self.validity_of_vert[i][player]) for i in range(self.game.size)]
        number_edges_towards_not_fixed = [len([1 for (s,edge_ind) in self.game.succ[i] if not(fixed[s]) and self.validity_of_edge[edge_ind][player]]) for i in range(self.game.size)]
        minimal_weight_towards_fixed = self.initialize_min_weights(fixed, player)
        order = self.initialize_order(minimal_weight_towards_fixed, player)
        max_to_fix = [i for i in range(self.game.size) if self.game.player[i] == player and number_edges_towards_not_fixed[i] == 0 and not(fixed[i])]

        while(order or max_to_fix):
            while(max_to_fix):
                i = max_to_fix.pop()
                self.update_map_at_vertex(i, self.compute_max_value([edge_ind for (s,edge_ind) in self.game.succ[i] if self.validity_of_edge[edge_ind][player]], player), player)
                fixed[i] = True
                self.treat_predecessors(i, order, max_to_fix, minimal_weight_towards_fixed, number_edges_towards_not_fixed, fixed, player)
            
            if(order):
                i = order.pop(0)
                self.update_map_at_vertex(i, minimal_weight_towards_fixed[i][0], player)
                fixed[i] = True
                self.treat_predecessors(i, order, max_to_fix, minimal_weight_towards_fixed, number_edges_towards_not_fixed, fixed, player)
    
        for i in range(self.game.size):
            if(not(fixed[i])):
                self.update_map_at_vertex_to_infty(i, player)
        
        self.globally_update_validity()


    def initialize_min_weights(self, fixed, player):
        '''
        (if player = 0, otherwise invert *)
        returns a list, containing for each non fixed min* vertex i that has a valid
        edge to fixed, the pair (m, m-map[i]), where m is the smallest*
        map[j] + w(e) of such an edge e=(i,j). For other i's, None.
        TODO: update optimal edge
        '''
        rep=[None for i in range(self.game.size)]
        for i in range(self.game.size):
            if(self.game.player[i] != player and not(fixed[i])):
                towards_fixed = [edge_ind for (s,edge_ind) in self.game.succ[i] if fixed[s]]
                if(towards_fixed):
                    if(self.game.typ == "energy"):
                        m = util.possibly_infinite_integer.min_of_list([self.dest_of_edge[edge_ind] for edge_ind in towards_fixed], player)
                    else:
                        m = util.sparse_tuple.min_of_tuple_list_with_additionnal_value([(self.map[self.game.edges[edge_ind][1]], self.game.edges[edge_ind][2]) for edge_ind in towards_fixed], player)
                    rep[i] = (m, m - self.map[i])
        return(rep)
    
    
    def initialize_order(self, minimal_weight_towards_fixed, player):
        '''
        (if player = 0, otherwise invert *)
        returns a list containing vertices i such that list[i] is not None,
        and sorted according to second coordinate (m - map[i]), in increasing*
        order.
        '''
        rep = [i for i in range(self.game.size) if minimal_weight_towards_fixed[i]]
        rep.sort(key = lambda i: minimal_weight_towards_fixed[i][1])
        if(player==1):
            rep.reverse()
        return(rep)
    
    
    def compute_max_value(self, edges, player):
        '''
        (if player = 0, otherwise invert *)
        returns max* value of an edge given in the list edges
        TODO: also updates optimal_edge
        '''
        if(self.game.typ == "energy"):
            rep = util.possibly_infinite_integer.min_of_list([self.dest_of_edge[edge_ind] for edge_ind in edges] ,1-player) #computes a max
        else:
            rep = util.sparse_tuple.min_of_tuple_list_with_additionnal_value([(self.map[self.game.edges[edge_ind][1]], self.game.edges[edge_ind][2]) for edge_ind in edges], 1-player)
        return(rep)
    
    
    def treat_predecessors(self, i, order, max_to_fix, minimal_weight_towards_fixed, number_edges_towards_not_fixed, fixed, player):
        '''
        (if player = 0, otherwise invert *)
        -   for max* predecessors p of i, decrement number_edges_towards_not_fixed[p],
            and add to max_to_fix if reached 0
        -   for min* predecessors p of i, update minimal_weight_towards_fixed, and
            if necessary, update order
        '''
        
        for (p,edge_ind) in [(p,edge_ind) for (p,edge_ind) in self.game.pred[i] if self.validity_of_edge[edge_ind][player] and not(fixed[p])]:
            if(self.game.player[p] == player): #max predecessors
                number_edges_towards_not_fixed[p] -= 1
                if(number_edges_towards_not_fixed[p] == 0):
                    max_to_fix.append(p)
            else: #min predecessors
                
                if(self.game.typ == "energy"):
                    dest_of_edge = self.dest_of_edge[edge_ind]
                else:
                    dest_of_edge = self.map[i] + util.sparse_tuple(value=[(self.game.edges[edge_ind][2],1)])
                    
                if(minimal_weight_towards_fixed[p] == None): #first edge towards fixed
                    minimal_weight_towards_fixed[p] = (dest_of_edge, dest_of_edge - self.map[p])
                    self.insert_in_order(p, order, minimal_weight_towards_fixed, player)
                    self.optimal_edge[p] = edge_ind
                else:
                    if((player == 0 and dest_of_edge < minimal_weight_towards_fixed[p][0]) or
                        (player == 1 and dest_of_edge > minimal_weight_towards_fixed[p][0])):
                        minimal_weight_towards_fixed[p] = (dest_of_edge, dest_of_edge- self.map[p])
                        order.remove(p)
                        self.insert_in_order(p, order, minimal_weight_towards_fixed, player)
                        self.optimal_edge[p] = edge_ind
    
    
    def update_map_at_vertex(self,i,dest,player):
        '''
        updates the map at vertex i to position dest
        if player = 0, then dest >= map[i]
        '''
        if(self.map[i] != dest):
            self.map[i] = dest
            
            for _,edge_ind in self.game.pred[i]:
                if self.validity_of_edge[edge_ind] != (1-player,player) :
                    self.edge_needs_updating[edge_ind] = True
            
            for _,edge_ind in self.game.succ[i]:
                if self.validity_of_edge[edge_ind] != (player, 1-player):
                   self.edge_needs_updating[edge_ind] = True
            
            
            if(self.game.typ == "energy"):
                for p,edge_ind in self.game.pred[i]:
                    self.dest_of_edge[edge_ind] = dest + self.game.edges[edge_ind][2]
        
    
    def update_map_at_vertex_to_infty(self,i, player):
        '''
        updates the map at vertex i to position (-1)**player * infty
        '''
        if(self.game.typ == "energy"):
            dest = util.possibly_infinite_integer(0, infty=(-1)**player)
        else:
            dest = util.sparse_tuple(infty=(-1)**player)
        self.update_map_at_vertex(i, dest, player)
        
    
    def insert_in_order(self, i, order, minimal_weight_towards_fixed, player):
        '''
        (if player = 0, otherwise invert *)
        inserts i in order at the right position such that order
        remains increasing* wrt second coord in mwtf
        '''
        lo=0
        hi=len(order)
        while lo < hi:
            mid = (lo+hi) // 2
            if ((player == 0 and minimal_weight_towards_fixed[i][1] < minimal_weight_towards_fixed[order[mid]][1]) or
                (player == 1 and minimal_weight_towards_fixed[i][1] > minimal_weight_towards_fixed[order[mid]][1])):
                hi = mid
            else:
                lo = mid+1
        order.insert(lo, i)
        
        
        
        
    def threshold_lift(self, i, growing): #DEPRECATED, NEEDS UPDATING FOR BCDGR
        if(self.dest_of_vert[i] > self.game.size * self.game.max_absolute_value):
            self.dest_of_vert[i] = util.possibly_infinite_integer(0,1) #set dest to +infinity
        elif(self.dest_of_vert[i] < - self.game.size * self.game.max_absolute_value):
            self.dest_of_vert[i] = util.possibly_infinite_integer(0,-1) #set dest to -infinity
        self.update_map(i, self.dest_of_vert[i], growing)
    