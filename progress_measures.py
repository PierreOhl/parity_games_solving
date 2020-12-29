import games
import trees
import time
import util
from copy import deepcopy

class asym_progress_measure_standard:
    ''' 
    asym_progress_measure_standard:
        - game is a parity game
        - map is a list of positions of size game.size 
        in complete tree of size degree game.size
        - player is in O,1
        - height = height of tree -1
    ''' 

    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.height = game.max_priority // 2
        self.map = [trees.position_in_complete_tree(self.height, game.size) for i in range(game.size)]
        self.destination = [self.compute_destination(i) for i in range(game.size)]
            

    def compute_destination(self, i):
        rep = trees.position_in_complete_tree(self.height, self.game.size)
        pos_list=[self.map[suc[0]].min_source_for_valid_edge(self.player, suc[1]) for suc in self.game.succ[i]] #suc[0]=successor, suc[1]=priority
        if self.game.player[i] == self.player:
            #compute a min
            rep.set_to_top()
            for pos in pos_list:
                if(pos.smaller(rep)):
                    rep=pos 
            return(rep)            
        else :
            #compute a max
            for pos in pos_list:
                if(rep.smaller(pos)):
                    rep=pos 
            return(rep)
        
    def update_destination_of_predecessors(self,i):
        for (predecessor, priority) in self.game.pred[i]:
            self.destination[predecessor] = self.compute_destination(predecessor)

    def lift(self,i):
        self.map[i] = self.destination[i]
        for (predecessor, priority) in self.game.pred[i] :
            self.destination[predecessor] = self.compute_destination(predecessor)

    def list_invalid(self):
        return([i for i in range(self.game.size) if not(self.destination[i].smaller(self.map[i]))])
    
class asym_progress_measure_gliding:
    ''' 
    asym_progress_measure_gliding:
        - game is a parity game
        - map is a list of positions of size n in infinite complete tree
        - player is in O,1
        - height = height of tree -1
        - partition is a util.partition that regroups vertices mapped to same node
    ''' 
    
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.height = game.max_priority // 2
        self.map = [trees.position_in_infinite_tree(self.height) for i in range(game.size)]
        self.destination = [self.compute_destination(i) for i in range(game.size)]
        self.partition = util.partition_plus_node_data(game.size, trees.position_in_infinite_tree(self.height))
        
    def compute_destination(self, i):
        rep = trees.position_in_infinite_tree(self.height)
        pos_list=[self.map[suc[0]].min_source_for_valid_edge(self.player, suc[1]) for suc in self.game.succ[i]] #suc[0]=successor, suc[1]=priority
        if self.game.player[i] == self.player:
            #compute a min
            rep.set_to_top()
            for pos in pos_list:
                if(pos.smaller(rep)):
                    rep=pos 
            return(rep)            
        else :
            #compute a max
            for pos in pos_list:
                if(rep.smaller(pos)):
                    rep=pos 
            return(rep)
        
    
    def update_destination_of_predecessors(self,i):
        for (predecessor, priority) in self.game.pred[i]:
            self.destination[predecessor] = self.compute_destination(predecessor)
            
    
    def lift(self,i):
        departure_node = deepcopy(self.map[i])
        
        #lift i
        self.map[i] = self.destination[i]
        for (predecessor, priority) in self.game.pred[i] :
            self.destination[predecessor] = self.compute_destination(predecessor)

        #move returns true if i was the last in its subset
        if(self.partition.move(i, self.map[i])):
            ########### GLIDING #############
            
            #count largest prefix of zeros in departure_node
            prefix_of_zeros_size = 0
            
            #(using -1 below is intentionnal, not a mistake)
            while(prefix_of_zeros_size < self.height -1 and departure_node.value[prefix_of_zeros_size] == 0):
                prefix_of_zeros_size += 1
            
            #computing arrival
            arrival_of_glide = trees.position_in_infinite_tree(self.height)
            if(prefix_of_zeros_size == self.height - 1):
                arrival_of_glide.set_to_top()
            else:
                arrival_of_glide.value[prefix_of_zeros_size + 1] = departure_node.value[prefix_of_zeros_size + 1] + 1
                for k in range(prefix_of_zeros_size + 2, self.height):
                    arrival_of_glide.value[k] = departure_node.value[k]
            
            #updating the right vertices
            for vert in range(self.game.size):
                k = prefix_of_zeros_size
                should_glide = (self.map[vert].value[k] >= departure_node.value[k])
                k += 1
                
                while(should_glide and k < self.height):
                    should_glide = should_glide and (self.map[vert].value[k] >= departure_node.value[k])
                    k+=1
                
                if(should_glide):
                    self.map[vert] = deepcopy(arrival_of_glide)
                    for (predecessor, priority) in self.game.pred[vert] :
                        self.destination[predecessor] = self.compute_destination(predecessor)
                    
                    self.partition.move(vert, arrival_of_glide)
            
    def list_invalid(self):
        return([i for i in range(self.game.size) if not(self.destination[i].smaller(self.map[i]))])

class sym_progress_measure_global:
    ''' 
    sym_progress_measure_global:
    - game is a parity game
    - pair : tuple of two asym progress measures, one for each player
    '''
    
    def __init__(self, game):
        self.game = game
        self.pair = [asym_progress_measure_standard(game, 0), asym_progress_measure_standard(game, 1)]
    
    def pair_of_positions(self, i):
        return([self.pair[0].map[i], self.pair[1].map[i]])
    
    def destination(self, i):
        return((self.pair[0].destination[i], self.pair[1].destination[i])) #todo : change to tuple here
    
    def list_in_box(self, box):
        return([i for i in range(self.game.size) if box.in_box(self.pair_of_positions(i))])
    
    def list_dest_not_in_box(self, box):
        return([i for i in self.list_in_box(box) if not(box.in_box(self.destination(i)))])
    
    def lift(self, i):
        self.pair[0].lift(i)
        self.pair[1].lift(i)
    
    #accelerates, updates all_for_opponent, and returns true if it has accelerated
    def accelerate(self, box):
                
        in_scope_initial = self.list_in_box(box)
        
        if(in_scope_initial == []):
            return(True)
        
        for player in [0,1]:
            if(
                all([
                    self.pair[player].destination[i].smaller(self.pair[player].map[i])
                    for i in in_scope_initial
                ])
            ):
                destination_node = box.pair[1-player].first_not_in_subtree()
                
                for i in in_scope_initial:
                    self.pair[1-player].map[i] = destination_node
                    self.pair[1-player].update_destination_of_predecessors(i)
                    
                return(True)
        
        return(False)
        
    
    def empty(self, box, limit_time, infos):
        
        infos["recursive calls"]+=1
        
        if(time.time() > limit_time):
            return()
        
        very_invalid = self.list_dest_not_in_box(box)
        
        while(very_invalid != []):
            i = util.pickrandom(very_invalid)
            self.lift(i)
            infos["updates"]+=1
            very_invalid = self.list_dest_not_in_box(box) #TODO : speed up here
        
        if(self.accelerate(box)):
            return()
        
        for sub in box.subboxes():
            self.empty(sub, limit_time, infos)
    

    
            
class sym_progress_measure_local():
    '''
    sym_progress_measure_local:
    - game is a parity_game
    - pair is a pair of asym_progress_measures
    '''
    def __init__(self, game):
        self.game = game
        self.pair = [asym_progress_measure(game, 0), asym_progress_measure(game, 1)]
        
    