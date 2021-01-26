import games
import trees
import energy_progress_measures
import time
import random as rand
import util
from copy import deepcopy


class execution:
    '''
        - game is an energy_game
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
        file = open("executions/energy/" + filename, 'w+')
        file.write(self.to_string())
        file.close()
    
    @classmethod
    def from_string(cls,s):
        lines = s.split("\n")
        str_game = lines[1] + lines[2] + lines[3] + lines[4]
        game = games.energy_game.fromstring(str_game)
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
        file = open("executions/energy/" + filename, 'r')
        s = file.read()
        file.close()
        return from_string(s)
        
        
    #performs standard pm lifting from POV of given player
    def asymmetric_lifting_standard(self, player):
        
        start_time=time.time()
        phi = energy_progress_measures.progress_measure(self.game)
        
        invalid=phi.list_invalid(1-player)
        
        self.infos["algorithm"] = "Asymmtric PM for " + ["Eve", "Adam"][player]
        self.infos["updates"]=0

        while(invalid):
            
            if(time.time() > start_time + self.timeout):
                self.is_timeout = True
                break
            
            i = util.pickrandom(invalid)
            phi.threshold_lift(i)
            self.infos["updates"] += 1
            invalid = phi.list_invalid(1-player)
        
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if (phi.map[i].times_infinity != 0)]
        
    def asymmetric_snare_update(self, player):
        
        start_time=time.time()
        phi = energy_progress_measures.progress_measure(self.game)
        
        self.infos["algorithm"] = "Asymmetric snare update for " + ["Eve", "Adam"][player]
        self.infos["snare updates"] = 0
        self.infos["spent"] = 0
        self.infos["equivalent updates"] = 0
        
        while(any([phi.dest_of_vert[i] * (-1)**player > phi.map[i] * (-1)**player and phi.map[i].times_infinity * (-1)**player < 1 for i in range(self.game.size)])):
            
            if(time.time() > start_time + self.timeout):
                self.is_timeout = True
                break
            
            (s,u)=phi.snare_lift(player)
            self.infos["snare updates"] += 1
            self.infos["equivalent updates"] += u
            self.infos["spent"] += s
        
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if (phi.map[i].times_infinity != 0)]
        
    
    def alternating_snare_update(self):
        
        start_time=time.time()
        phi = energy_progress_measures.progress_measure(self.game)
        
        self.infos["algorithm"] = "Alternating snare update"
        self.infos["snare updates"] = 0
        self.infos["spent"] = 0
        self.infos["equivalent updates"] = 0
        
        player=0
        while(any([phi.map[i].times_infinity == 0 for i in range(self.game.size)])):
            
            if(time.time() > start_time + self.timeout):
                self.is_timeout = True
                break
            
            (s,u)=phi.snare_lift(player)
            self.infos["snare updates"] += 1
            self.infos["equivalent updates"] += u
            self.infos["spent"] += s
            player = 1 - player
        
        self.infos["runtime"] = time.time() - start_time
        self.solution = [i for i in range(self.game.size) if (phi.map[i].times_infinity == 1)]