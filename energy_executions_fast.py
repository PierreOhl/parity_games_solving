import games
import trees
import energy_progress_measures_fast
import time
import random as rand
import util
from copy import deepcopy
from networkx.drawing.nx_agraph import to_agraph # To remove to execute with Pypy3
import networkx as nx


class execution:
    '''
        - game is a game
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
        self.infos = {}
                
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

    
    # TODO: the reimplementation currently only supports energy games
    def snare_update(self, player = 0, write_transcript = False, alternating = False, chrono = False):
        
        start_time = time.time()
        phi = energy_progress_measures_fast.progress_measure(self.game)
        
        if(alternating):
            self.infos["algorithm"] = "Alternating snare update starting with " + ["Eve", "Adam"][player]
        else:
            self.infos["algorithm"] = "Asymmetric snare update for " + ["Eve", "Adam"][player]
            
        self.infos["snare updates"] = 1
        
        if write_transcript:
            self.transcript = [deepcopy(phi)]
        
        if player == 1:
            phi.alternate_game()
        
        current_player = player # May change in case of alternation
        
        while phi.snare_lift() or\
              (alternating and any(phi.map[v] != float("-inf") and phi.map[v] != float("inf") for v in range(self.game.size))):
            if(time.time() > start_time + self.timeout):
                self.is_timeout = True
                break
            
            if(write_transcript):
                self.transcript.append(deepcopy(phi))
            
            self.infos["snare updates"] += 1
            
            if(alternating):
                current_player = 1 - current_player
                phi.alternate_game()
                
        self.infos["runtime"] = time.time() - start_time
            
        if(chrono):
            self.infos["chrono"] = phi.infos["chrono"]

        if current_player == 0:
            self.solution = [i for i in range(self.game.size) if phi.map[i] != float("-inf")]
        else:
            self.solution = [i for i in range(self.game.size) if phi.map[i] != float("inf")]
        
    
    def draw_transcript(self, filename, display_future_increments=True):
        for t in range(self.infos["snare updates"]+1):
            phi=self.transcript[t]
                    
            edges_with_attributes = [(i,j,phi.attribute_of_edge(edge_ind)) for edge_ind, (i,j,_) in enumerate(self.game.edges)]
            nodes_with_attributes = [(i,phi.attribute_of_vertex(i)) for i in range(self.game.size)]

            if(display_future_increments):
                for i in range(self.game.size):
                    if(t == self.infos["snare updates"]):
                        nodes_with_attributes[i][1]["label"] = "0"
                    else:
                        nodes_with_attributes[i][1]["label"]=(self.transcript[t+1].map[i] - self.transcript[t].map[i]).to_label()

            G = nx.MultiDiGraph()

            G.add_nodes_from(nodes_with_attributes)
            G.add_edges_from(edges_with_attributes)

            G.graph['edge'] = {'arrowsize': '0.6', 'splines': 'curved'}
            G.graph['graph'] = {'scale': '1'}

            A = to_agraph(G)
            
            A.layout('dot')                                                                 
            A.draw(filename + "{:03d}".format(t) + ".png")
    
    
    def any_increase_in_max_delta(self):
        max_delta=[]
        for t in range(self.infos["snare updates"]):
            if(any([self.transcript[t].validity_of_vert[i][0] == 0 and self.transcript[t+1].validity_of_vert[i][0] == 1 for i in range(self.game.size)])):
                max_delta.append("new_invalid_vertices")
            elif(any([self.transcript[t+1].map[i].infty and self.transcript[t].map[i].infty == 0 for i in range(self.game.size)])):
                max_delta.append("new_infinite_vertices")
            #elif(any([(self.transcript[t+1].map[i] - self.transcript[t].map[i]).infty == 0 for i in range(self.game.size)])):
            else:
                max_delta.append(max([(self.transcript[t+1].map[i] - self.transcript[t].map[i]).value for i in range(self.game.size) if (self.transcript[t+1].map[i] - self.transcript[t].map[i]).infty == 0]))
        return(max_delta)
    
    
    def does_type_vector_repeat(self):
        length=self.infos["snare updates"] +1
        configs=[self.transcript[t].type_config() for t in range(length)]
        rep=False
        for a in range(length):
            for b in range(a+1,length):
                if (configs[a] == configs[b]):
                    rep=True
                    print(a,b)
                    print(configs[a],configs[b])
        return(rep)
