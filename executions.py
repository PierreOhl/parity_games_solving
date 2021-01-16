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
                
    def printinfos(self):
        print("infos:", self.infos)
        
        
    #performs standard pm lifting from POV of given player
    def asymmetric_lifting_standard(self, player):
        
        start_time=time.time()
        phi = progress_measures.asym_progress_measure_standard(self.game, player)
        
        invalid=phi.list_invalid()
        
        self.infos["algorithm"] = "Asymmtric PM for " + ["Eve", "Adam"][player]
        self.infos["updates"]=0

        while(invalid != []):
            
            if(time.time() > start_time + self.timeout):
                self.is_timeout = True
                break
            
            i = util.pickrandom(invalid)
            phi.lift(i)
            self.infos["updates"]+=1
            invalid=phi.list_invalid()
        
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if not(phi.map[i].is_top)]
        
        
    #performs gliding pm lifting from POV of given player
    def asymmetric_lifting_gliding(self, player):
        
        start_time=time.time()
        phi = progress_measures.asym_progress_measure_gliding(self.game, player)
        
        invalid = phi.list_invalid()
        
        self.infos["algorithm"] = "Gliding asymmetric PM for " + ["Eve", "Adam"][player]
        self.infos["updates"]=0

        while(invalid != []):
            
            if(time.time() > start_time + self.timeout):
                self.is_timeout = True
                break
            
            i = util.pickrandom(invalid)
            phi.lift(i)
            self.infos["updates"]+=1
            invalid=phi.list_invalid()
        
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if not(phi.map[i].is_top)]
        
    
    
    
    #performs symmetric "emptying-boxes" algorithm
    def symmetric_lifting_strong(self):
        
        start_time = time.time()
        phi = progress_measures.sym_progress_measure_global(self.game)  
        
        #initializing full product box
        b = trees.box(trees.node_in_complete_tree(self.game.max_priority//2, self.game.size, []),
                        trees.node_in_complete_tree(self.game.max_priority//2, self.game.size, []))
        
        #initializing info
        self.infos["algorithm"] = "Strong symmetric PM"
        self.infos["updates"]=0
        self.infos["recursive calls"]=0

        #running main recursive procedure
        self.is_timeout = phi.empty(b, start_time + self.timeout, self.infos)
        
        #writing additionnal info
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if not(phi.pair[0].map[i].is_top)]



    #main recursive procedure for Zielonka algorithm
    def zielonka_solve(self, priority, vert_set, succ, time_limit):
        
        self.infos["recursive calls"]+=1
        
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
        
        self.infos["equivalent updates"] += len(attr_to_priority)
        
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
        
        self.infos["equivalent updates"] += len(winning_for_opponent) - len(winning_for_opponent_in_subgame)
        
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
        
        self.infos["equivalent updates"] = self.game.size - len(remaining_vert)
        
        updated_succ = deepcopy(self.game.succ)
        for i in remaining_vert:
            for edge in self.game.succ[i]:
                if(edge[0] not in remaining_vert):
                    updated_succ[i].remove(edge)
        
        self.infos["algorithm"] = "Zielonka recursive"
        self.infos["recursive calls"] = 0
        
        #call to main recursive procedure
        solution_set = self.zielonka_solve( 
            self.game.max_priority, 
            remaining_vert,
            updated_succ,
            start_time + self.timeout
        )
        
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if i in solution_set or i in player_attr_to_opponent_sink[0]]
        
    
    def symmetric_local(self):
        
        self.infos["algorithm"] = "Symmetric with local validity"
        self.infos["updates"] = 0
        self.infos["accelerations"] = 0
        
        start_time = time.time()
        
        phi = progress_measures.sym_progress_measure_local(self.game)
        
        outer_box = trees.box(
            trees.node_in_infinite_tree(self.game.max_priority // 2, []),
            trees.node_in_infinite_tree(self.game.max_priority // 2, [])
        )
        
        while(phi.list_in_box(outer_box) != []):
            
            if(time.time() > start_time + self.timeout):
                self.is_timeout = True
                break
            
            s = phi.lift()
            self.infos[s] += 1
        
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if not(phi.pair[0][i].is_top)]


    def symmetric_no_reset(self):
        
        self.infos["algorithm"] = "Symmetric with global validity and no resets"
        self.infos["updates"] = 0
        self.infos["small_accelerations"] = 0
        self.infos["big_accelerations"] = 0
        
        start_time = time.time()
        
        phi = progress_measures.sym_progress_measure_no_reset(self.game)
        
        while(True):
            
            if(time.time() > start_time + self.timeout):
                self.is_timeout = True
                break
            
            s = phi.lift()
            
            if(s=="terminate"):
                break
            
            self.infos[s] += 1

        self.infos["max number"] = max([max(phi.map[i]) for i in range(self.game.size)])
        
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if phi.map[i][0] == 1]
        
    
    def totally_ordered_sym_arbitrary_lifts(self):
        start_time=time.time()
        phi = progress_measures.totally_ordered_symmetric_pm(self.game)
        
        self.infos["algorithm"] = "finite alt-lexico pm with arbitrary updates"
        self.infos["updates"]=0

        invalid = phi.list_of_invalid_vertices()
        while(invalid):
            
            if(time.time() > start_time + self.timeout):
                self.is_timeout = True
                break
            
            i = util.pickrandom(invalid)
            phi.lift(i, True)
            self.infos["updates"]+=1

            invalid = phi.list_of_invalid_vertices()    
    
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if phi.map[i][0]]
        
        
    
    def totally_ordered_sym_increasing_lifts(self, player):
        start_time=time.time()
        phi = progress_measures.totally_ordered_symmetric_pm(self.game)
        
        self.infos["algorithm"] = "finite alt-lexico pm with arbitrary updates"
        self.infos["updates"]=0

        invalid = phi.list_of_vertices_invalid_for_player(player)
        while(invalid):
            
            if(time.time() > start_time + self.timeout):
                self.is_timeout = True
                break
            
            i = util.pickrandom(invalid)
            phi.lift(i, True)
            self.infos["updates"]+=1

            invalid = phi.list_of_vertices_invalid_for_player(player)
    
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if not(phi.map[i][1])]