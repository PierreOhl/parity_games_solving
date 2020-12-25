import games
import trees
import progress_measures
import time
import random as rand
import util
from copy import deepcopy

class execution:
    '''
        - game is a parity_game
        - timeout is a float
        - runtime is a float
        - is_timeout is a boolean
        - solution is a list of integers representing the winning region
        for player 0    
    '''
    
    def __init__(self, game, timeout):
        self.game = game
        self.timeout = timeout
        self.is_timeout = False
        self.solution = []
        self.infos={}
        
    def print(self):
        print("EXECUTION:")
        print("game description:\n")
        self.game.print()
        print("\ntimeout %2f" % self.timeout)
        print("is timeout ", self.is_timeout)
        print("solution ", self.solution)
        print("infos:", self.infos)
        
    def printinfos(self):
        print("infos:", self.infos)
        
        
    #performs standard pm lifting from POV of given player
    def asymmetric_lifting(self, player):
        
        start_time=time.time()
        phi = progress_measures.asym_progress_measure(self.game, player)
        
        invalid=phi.list_invalid()
        
        self.infos["algorithm"] = "Asymmtric PM for " + ["Eve", "Adam"][player]
        self.infos["number of updates"]=0

        while(invalid != []):
            
            if(time.time() > start_time + self.timeout):
                self.is_timeout = True
                break
            
            i = util.pickrandom(invalid)
            phi.lift(i)
            self.infos["number of updates"]+=1
            invalid=phi.list_invalid()
        
        
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if not(phi.map[i].is_top)]
        
    
    #performs symmetric "emptying-boxes" algorithm
    def symmetric_lifting_strong(self):
        
        start_time = time.time()
        phi = progress_measures.sym_progress_measure_strong(self.game)  
        
        #initializing full product box
        b = trees.box(trees.node(self.game.max_priority//2, self.game.size, []),
                        trees.node(self.game.max_priority//2, self.game.size, []))
        
        #initializing info
        self.infos["algorithm"] = "Strong symmetric PM"
        self.infos["number of updates"]=0
        self.infos["number of recursive calls"]=0
        self.infos["number of empty calls"]=0
        self.infos["number of calls with no lift"] = 0
        
        
        #running main recursive procedure
        self.is_timeout = phi.empty(b, start_time + self.timeout, self.infos)
        
        #writing additionnal info
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if not(phi.pair[0].map[i].is_top)]



    #main recursive procedure for Zielonka algorithm
    def zielonka_solve(self, priority, vert_set, succ, time_limit):
        
        self.infos["number of recursive calls"]+=1
        
        if(time.time() > time_limit):
            self.is_timeout = True
            return({-1})
        
        if(len(vert_set) == 0):
            return({})
        
        player = priority % 2
        
        #compute attractor to edges of high priority
        attr_to_priority = util.attractor_to_priority(
            vert_set,
            succ,
            self.game.player,
            priority,
            player
        )
        
        #compute subgame
        sub_vert_set = vert_set.difference(attr_to_priority)
        sub_succ = deepcopy(succ)
        for i in sub_vert_set:
            for edge in succ[i]:
                if(edge[1] == priority or edge[0] not in sub_vert_set):
                    sub_succ[i].remove(edge)
        
        #recursive call
        winning_for_opponent_in_subgame = self.zielonka_solve(
            priority -1,
            sub_vert_set,
            sub_succ,
            time_limit
        )
        
        if(winning_for_opponent_in_subgame == {}):
            return(vert_set)
        
        #compute attractor to winning
        winning_for_opponent = util.attractor_to_set_of_vertices(
            vert_set,
            succ,
            self.game.player,
            winning_for_opponent_in_subgame,
            1 - player
        )
        
        #define rest of game
        rest_vert_set = vert_set.difference(winning_for_opponent)
        rest_succ = deepcopy(succ)
        for i in rest_vert_set:
            for edge in succ[i]:
                if(edge[0] not in rest_vert_set):
                    rest_succ[i].remove(edge)
        
        #recursively search for winning region in rest of game
        return(
            self.zielonka_solve(
                priority,
                rest_vert_set,
                rest_succ,
                time_limit
            )
        )


    #performs Zielonka's attractor-based algorithm
    def zielonka_algorithm(self):
        
        start_time = time.time()
        
        #identify sinks
        sinks = {i for i in range(self.game.size) if self.game.succ[i] == []}
        
        #remove attractor to sinks
        player_attr_to_opponent_sink=[{},{}]
        for player in [0,1]:
            player_attr_to_opponent_sink[player] = util.attractor_to_set_of_vertices(
                {i for i in range(self.game.size)},
                self.game.succ,
                self.game.player,
                {i for i in sinks if self.game.player == 1 - player},
                player
            )
        remaining_vert = {i for i in range(self.game.size) if all([i not in player_attr_to_opponent_sink[pl] for pl in [0,1]])}
        updated_succ = deepcopy(self.game.succ)
        for i in remaining_vert:
            for edge in self.game.succ[i]:
                if(edge[0] not in remaining_vert):
                    updated_succ[i].remove(edge)
        
        self.infos["algorithm"] = "Zielonka recursive"
        self.infos["number of recursive calls"] = 0
        
        #call to main recursive procedure
        solution_set = self.zielonka_solve( 
            self.game.max_priority, 
            remaining_vert,
            updated_succ,
            start_time + self.timeout
        )
        
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if i in solution_set or i in player_attr_to_opponent_sink[0]]