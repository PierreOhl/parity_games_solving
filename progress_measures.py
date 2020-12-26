import games
import trees
import time
import util

class asym_progress_measure:
    ''' 
    asym_progress_measure:
        - game is a parity game
        - map is a list of positions of size n
        - player is in O,1
        - height = height of tree -1
    ''' 

    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.height = game.max_priority // 2
        self.map = [trees.position(self.height, game.size) for i in range(game.size)]
        self.destination = [self.compute_destination(i) for i in range(game.size)]
            
    def print(self):
        print("ASYMETRIC PM:")
        print("height %d, size %d " %(self.height, self.game.size))
        for i in range(self.game.size):
            print("position of %d-th node:" %i)
            self.map[i].print()

    def compute_destination(self, i):
        rep = trees.position(self.height, self.game.size)
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
    

class sym_progress_measure_strong:
    ''' 
    sym_progress_measure_strong:
    - game is a parity game
    - pair : tuple of two asym progress measures, one for each player
    '''
    
    def __init__(self, game):
        self.game = game
        self.pair = [asym_progress_measure(game,0), asym_progress_measure(game, 1)]
    
    def print(self):
        print("SYMMETRIC PM:")
        print("Eve PM:")
        self.pair[0].print()
        print("\n \n Adam PM:")
        self.pair[1].print()
    
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
    
    #accelerates, and returns true if it has accelerated
    def accelerate(self, box):
        
        all_valid_for_player = [
            all([
                self.pair[player].destination[i].smaller(self.pair[player].map[i])
                for i in self.list_in_box(box)
            ])
            for player in [0,1]
        ]
        
        if(all_valid_for_player[box.player]):
            destination_node = box.pair[1 - box.player].first_not_in_subtree()
            
            for i in self.list_in_box(box):
                self.pair[1 - box.player].map[i] = destination_node
                self.pair[1 - box.player].update_destination_of_predecessors(i)
        
        if(any(all_valid_for_player)):
            parent_box = box.parent()
            destination_node = parent_box.pair[box.player].first_not_in_subtree()
            
            for i in self.list_in_box(parent_box):
                self.pair[box.player].map[i] = destination_node
                self.pair[box.player].update_destination_of_predecessors(i)
        
        return(any(all_valid_for_player))
    
    #returns true if times out
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
            if(len(self.list_in_box(box))>0) :
                self.empty(sub, limit_time, infos)
            