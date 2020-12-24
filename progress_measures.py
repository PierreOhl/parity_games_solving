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
        self.map = [[] for i in range(game.size)]
        for i in range(game.size):
            self.map[i] = trees.position(self.height, game.size)
            
    def print(self):
        print("ASYMETRIC PM:")
        print("height %d, size %d " %(self.height, self.game.size))
        for i in range(self.game.size):
            print("position of %d-th node:" %i)
            self.map[i].print()

    def destination(self, i):
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

    def lift(self,i):
        self.map[i] = self.destination(i)

    def list_invalid(self):
        return([i for i in range(self.game.size) if not(self.destination(i).smaller(self.map[i]))])
    

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
        return([self.pair[0].destination(i), self.pair[1].destination(i)])
    
    def list_in_box(self, box):
        return([i for i in range(self.game.size) if box.in_box(self.pair_of_positions(i))])
    
    def list_dest_not_in_box(self, box):
        return([i for i in self.list_in_box(box) if not(box.in_box(self.destination(i)))])
    
    def lift(self, i):
        self.pair[0].lift(i)
        self.pair[1].lift(i)
    
    def accelerate(self, box):
        rep=False
        for player in [0,1]:
            scope=self.list_in_box(box)
            if(all([self.pair[player].destination(i).smaller(self.pair[player].map[i]) for i in scope])):
                n = box.pair[1-player].first_not_in_subtree()
                rep=True
                for i in scope:
                    self.pair[1-player].map[i]=n
        return(rep)
    
    #returns true if times out
    def empty(self, box, limit_time, infos):
        infos["number of recursive calls"]+=1
        scope_init = self.list_in_box(box)
        if(scope_init == []):
            infos["number of empty calls"]+=1
            return(False)
        if(time.time() > limit_time):
            return(True)        
        if(self.accelerate(box)):
            return(False)
        very_invalid = self.list_dest_not_in_box(box)
        while(very_invalid != []):
            i = util.pickrandom(very_invalid)
            self.lift(i)
            infos["number of updates"]+=1
            very_invalid=self.list_dest_not_in_box(box)
        if(self.accelerate(box)):
            return(False)
        for sub in box.subboxes():
            if self.empty(sub, limit_time, infos):
                return(True)
        return(False)