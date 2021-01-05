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
        for (predecessor, _, _) in self.game.pred[i] :
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
                    for (predecessor, _, _) in self.game.pred[vert] :
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
        return((self.pair[0].destination[i], self.pair[1].destination[i]))
    
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
    

class sym_progress_measure_local:
    '''
    sym_progress_measure_local:
    - game is a parity_game
    - pair is a pair of progress measures in infinite tree
    '''
    def __init__(self, game):
        self.game = game
        self.height = game.max_priority // 2
        self.pair = (
            [trees.position_in_infinite_tree(self.height) for i in range(game.size)],
            [trees.position_in_infinite_tree(self.height) for i in range(game.size)]
        )
        
    def pair_of_positions(self, i):
        return((self.pair[0][i], self.pair[1][i]))
    
    def update(self, i, dest):
        '''
        updates the progress measures.
        dest is a couple of positions
        '''
        for player in (0,1):
            self.pair[player][i] = dest[player]
    
    def list_in_box(self, box):
        return([i for i in range(self.game.size) if box.in_box(self.pair_of_positions(i))])
    
    #computes local destination of node wrt given box
    def compute_destination(self, i, box):
        in_box = self.list_in_box(box)
        rep = []
        for player in (0,1):
            #we also compare to upper, should not be needed
            pos_list=[self.pair[player][suc[0]].min_source_for_valid_edge_with_bound(player, suc[1], box.pair[player].first_not_in_subtree()) for suc in self.game.succ[i] if suc[0] in in_box] #suc[0]=successor, suc[1]=priority
            if self.game.player[i] == player:
                #compute a min
                rep_player = box.pair[player].first_not_in_subtree()
                for pos in pos_list:
                    if(pos.smaller(rep_player)):
                        rep_player = pos
                rep.append(rep_player)
            else :
                #compute a max
                rep_player = trees.position_in_infinite_tree(self.height)
                for pos in pos_list:
                    if(rep_player.smaller(pos)):
                        rep_player = pos
                rep.append(rep_player)
        return(tuple(rep))
    
    def first_non_empty_child(self, box):            
        rep = deepcopy(box)
        if(box.is_global):
            rep.is_global = False
            return(rep)
        l = 0
        rep.player = 1 - rep.player
        rep.pair[1 - box.player] = box.pair[1- box.player].child(l)
        while(self.list_in_box(rep) == []):
            l = l + 1
            rep.pair[1 - box.player] = box.pair[1- box.player].child(l)
        return(rep)
    
    def lift(self):
        parent_box = trees.box.init_global_box_for_infinite_tree(self.height)
        while True:
            child_box = self.first_non_empty_child(parent_box)
            in_child_box = self.list_in_box(child_box)
            #first, try a lift. 
            for i in in_child_box :
                dest = self.compute_destination(i, parent_box)
                if not(child_box.in_box(dest)):
                    self.update(i, dest)
                    return("updates")
            
            #compute local validity
            all_valid = [True, True]
            for i in in_child_box :
                local_dest = self.compute_destination(i, child_box)
                for player in (0,1):
                    all_valid[player] = all_valid[player] and local_dest[player].smaller(self.pair[player][i])
            
            #try a big acceleration
            if all_valid[parent_box.player]:
                for i in self.list_in_box(parent_box):
                    self.pair[1 - parent_box.player][i] = parent_box.pair[1 - parent_box.player].first_not_in_subtree()
                return("accelerations")
            
            #try a small acceleration
            if all_valid[child_box.player]:
                for i in self.list_in_box(child_box):
                    self.pair[1 - child_box.player][i] = child_box.pair[1 - child_box.player].first_not_in_subtree()
                return("accelerations")
            
            
            ''' Uncomment for only small acceleration. 
            #accelerate if possible
            for player in (0,1):
                if all_valid[player]:
                    for i in self.list_in_box(child_box):
                        self.pair[1-player][i] = child_box.pair[1-player].first_not_in_subtree()
                    return("accelerations")
            '''
            
            
            #otherwise, go deeper
            parent_box = child_box 
            

class sym_progress_measure_no_reset:
    '''
    progress measure with no reset:
    - it is defined in min-parity semantic (with min >= 2)
    - it is defined in infinite tree
    - in a lift, every coordinate is always increased
    - same for accelerations
    '''
    
    def __init__(self, game):
        self.game = game
        self.height = game.max_priority + 1
        self.map = [
            [0 for h in range(self.height)]
            for i in range(game.size)
        ]
        self.dest_of_outgoing_edge = [
            [
                [int(h == p) for h in range(self.height)] #this has just a one at the right position
                for (j, p) in self.game.succ[i]
            ]
            for i in range(game.size)
        ]
        self.is_valid = [(True,True) for i in range(game.size)]
        for i in range(game.size):
            self.update_validity(i)
    

    #update dest_of_outgoing_edge for i and predecessors edges of i
    #and validity of i and of predecessors
    def update_info(self, i):
        #updating dest_of_outgoing_edge[i]
        for index_of_edge, (succ_vert, p) in enumerate(self.game.succ[i]):
            for h in range(p+1):
                self.dest_of_outgoing_edge[i][index_of_edge][h] = self.map[succ_vert][h] + (h==p)
        #updating validity
        self.update_validity(i)
        #updating it for predecessors
        for (pred_vert, p, index_of_edge) in self.game.pred[i]:
            for h in range(p+1):
                self.dest_of_outgoing_edge[pred_vert][index_of_edge][h] = self.map[i][h] + (h==p)
            self.update_validity(pred_vert)
    
    def update_validity(self, i):
        self.is_valid[i]=(
            self.compute_validity(i,0),
            self.compute_validity(i,1)
        )
    
    def list_in_box(self, box):
        return([i for i in range(self.game.size) if util.is_prefix(box, self.map[i])])

    def compute_validity(self, i, player):
        if(self.game.player[i] == player):#return True if there is a valid outgoing edge
            for e in range(len(self.game.succ[i])):
                j=1-player
                while(j<self.height):
                    if(self.map[i][j] < self.dest_of_outgoing_edge[i][e][j]):
                        break
                    if(self.map[i][j] > self.dest_of_outgoing_edge[i][e][j]):
                        return(True)
                    j+=2
                if(j >= self.height):
                    return(True)
            return(False)
        else: #return True if all outgoing edges valid
            for e in range(len(self.game.succ[i])):
                j=1-player
                while(j<self.height):
                    if(self.map[i][j] < self.dest_of_outgoing_edge[i][e][j]):
                        return(False)
                    if(self.map[i][j] > self.dest_of_outgoing_edge[i][e][j]):
                        break
                    j+=2
            return(True)
    
    #performs the next update or acceleration on self
    #returns either "updates", "accelerations", or "terminate"
    def lift(self):
        parent_box = []
        box = [0]
        priority_of_box = 0
        in_box = self.list_in_box(box)
        while(True):
            #first, try an update
            for i in in_box:
                if self.game.player[i] == priority_of_box % 2:
                    for e in range(len(self.game.succ[i])):
                        if(self.dest_of_outgoing_edge[i][e][priority_of_box] > box[priority_of_box]):
                            for h in range(self.height):
                                self.map[i][h] = max(
                                    self.map[i][h],
                                    self.dest_of_outgoing_edge[i][e][h]
                                )
                            self.update_info(i)
                            return("updates")
                else:
                    nb_succ = len(self.game.succ[i])
                    mi = min([self.dest_of_outgoing_edge[i][e][priority_of_box] for e in range(nb_succ) if util.is_prefix(parent_box, self.dest_of_outgoing_edge[i][e])])
                    if(mi > box[priority_of_box]):
                        self.map[i][priority_of_box] = mi
                        already_valid = [False for e in range(nb_succ)]
                        h = priority_of_box + 1
                        while(not(all(already_valid)) and h < self.height):
                            ma = max([self.dest_of_outgoing_edge[i][e][h] for e in range(nb_succ) if not(already_valid[e])])
                            self.map[i][h] = max(self.map[i][h], ma)
                            for e in range(nb_succ):
                                already_valid[e] = already_valid[e] or (self.dest_of_outgoing_edge[i][e][h] < ma)
                            h += 2
                        self.update_info(i)
                        return("updates")
            
            #try to accelerate  (asymmetric version: only for p+1 % 2), maybe change that
            if all([self.is_valid[i][(priority_of_box+1) % 2] for i in in_box]):
                if(priority_of_box == 0):
                    return("terminate")
                else:
                    for i in in_box:
                        self.map[i][priority_of_box-1] += 1
                        self.update_info(i)
                    return("accelerations")
                        
            #go deeper
            parent_box = deepcopy(box)
            mi = min([self.map[i][priority_of_box+1] for i in in_box])
            box.append(mi)
            in_box = ([i for i in in_box if self.map[i][priority_of_box+1] == mi])
            priority_of_box+=1