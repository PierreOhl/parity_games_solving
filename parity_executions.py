import games
import trees
import parity_progress_measures
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
        
        
    def to_string(self):
        return(
            #"game: " + "\n" + 
            #self.game.to_string() + "\n" +
            "timeout: " + str(self.timeout) + "\n" +
            "is_timeout: " + str(self.is_timeout) + "\n" +
            "solution: " + str(self.solution) + "\n" +
            "infos: " + str(self.infos)
        )
        
    
    def save_to_file(self, filename):
        file = open("executions/parity/" + filename, 'w+')
        file.write(self.to_string())
        file.close()
    
    
    @classmethod
    def from_string(cls,s):
        lines = s.split("\n")
        str_game = lines[1] + lines[2] + lines[3] + lines[4]
        game = games.parity_game.fromstring(str_game)
        infos={}
        str_infos = lines[8][8:-1].replace(" ","").split(",")
        for inf in str_infos:
            l = inf.split(": ")
            if(l[0] in ["updates", "equivalent updates", "recursive calls", "accelerations"]):
                infos[l[0]] = int(l[1])
            elif(l[0] in ["runtime", "spent"]):
                infos[l[0]] = float(l[1])
            else:
                infos[l[0]] = l[1]

    @classmethod
    def from_file(cls, filename):
        file = open("executions/parity/" + filename, 'r')
        s = file.read()
        file.close()
        return from_string(s)
        
        
    #performs standard pm lifting from POV of given player
    def asymmetric_lifting_standard(self, player):
        
        start_time=time.time()
        phi = parity_progress_measures.asym_progress_measure_standard(self.game, player)
        
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
        phi = parity_progress_measures.asym_progress_measure_gliding(self.game, player)
        
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
        phi = parity_progress_measures.sym_progress_measure_global(self.game)  
        
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
    def zielonka_solve(self, priority, vert_set, time_limit):
        
        self.infos["recursive calls"] += 1
        if(priority == self.game.max_param):
            self.infos["iterations"] += 1
        
        if(time.time() > time_limit):
            self.is_timeout = True
            return({-1})
        
        if(len(vert_set) == 0):
            return({})
        
        player = priority % 2
        
        #compute player attractor to edges of high priority
        attr_to_priority = self.game.attr_to_prio_in_subgame(vert_set, priority)
        
        self.infos["equivalent updates"] += len(attr_to_priority)
        
        #compute subgame (in place)
        sub_vert_set = vert_set.difference(attr_to_priority)

        #recursive call
        winning_for_opponent_in_subgame = self.zielonka_solve(
            priority -1,
            sub_vert_set,
            time_limit
        )
        
        if(winning_for_opponent_in_subgame == {}):
            return(vert_set)
        
        #compute attractor to winning set for opponent in subgame
        winning_for_opponent = self.game.attr_in_subgame(
            vert_set,
            priority,
            winning_for_opponent_in_subgame,
            1 - player
        )

        self.infos["equivalent updates"] += len(winning_for_opponent) - len(winning_for_opponent_in_subgame)
        
        #define rest of game
        rest_vert_set = vert_set.difference(winning_for_opponent)
        
        #recursively search for winning region in rest of game
        return(
            self.zielonka_solve(
                priority,
                rest_vert_set,
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
            player_attr_to_opponent_sink[player] = self.game.attr_in_subgame(
                {i for i in range(self.game.size)},
                self.game.max_param,
                {i for i in sinks if self.game.player[i] == 1 - player},
                player
            )
            
        remaining_vert = {i for i in range(self.game.size) if all([i not in player_attr_to_opponent_sink[pl] for pl in [0,1]])}
        
        self.infos["equivalent updates"] = self.game.size - len(remaining_vert)
    
        self.infos["algorithm"] = "Zielonka recursive"
        self.infos["recursive calls"] = 0
        self.infos["iterations"] = 0
        
        #call to main recursive procedure
        solution_set = self.zielonka_solve( 
            self.game.max_param, 
            remaining_vert,
            start_time + self.timeout
        )
        
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if i in solution_set or i in player_attr_to_opponent_sink[0]]
        
    
    def symmetric_local(self):
        
        self.infos["algorithm"] = "Symmetric with local validity"
        self.infos["updates"] = 0
        self.infos["accelerations"] = 0
        
        start_time = time.time()
        
        phi = parity_progress_measures.sym_progress_measure_local(self.game)
        
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
        
        phi = parity_progress_measures.sym_progress_measure_no_reset(self.game)
        
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
        phi = parity_progress_measures.totally_ordered_symmetric_pm(self.game)
        
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
        phi = parity_progress_measures.totally_ordered_symmetric_pm(self.game)
        
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
        
    
    def totally_ordered_zielonka_like(self):
        start_time=time.time()
        phi = parity_progress_measures.totally_ordered_symmetric_pm(self.game)
        
        self.infos["algorithm"]="zielonka-like alternating lexicographic"
        self.infos["updates"]=0
        self.infos["dive deeper"]=0
        self.infos["accelerations"]=0
        self.infos["go up"]= 0
        
        box = [0,0]
        vert_in_box = [i for i in range(self.game.size)]
        while(True):
            
            if(time.time() > start_time + self.timeout):
                self.is_timeout = True
                break
            
            s, vert_in_box=phi.next_zielonka_lift(box, vert_in_box)
            if(s == "terminate"):
                break
            else:
                self.infos[s] += 1
            
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if phi.map[i][0]]
            