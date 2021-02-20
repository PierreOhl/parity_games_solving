import games
import trees
import energy_progress_measures
import time
import random as rand
import util
from copy import deepcopy
from networkx.drawing.nx_agraph import to_agraph
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
        
        
    #performs standard pm lifting from POV of given player  #NEEDS FIXING
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
        self.solution = [i for i in range(self.game.size) if (phi.map[i].infty != 0)]
    
    def snare_update(self, player = 0, draw_transcript = False, alternating = False, chrono = False, transcript_filename = ""):
        
        start_time=time.time()
        phi = energy_progress_measures.progress_measure(self.game)
        
        if(alternating):
            self.infos["algorithm"] = "Alternating snare update"
        else:
            self.infos["algorithm"] = "Asymmetric snare update for " + ["Eve", "Adam"][player]
            
        self.infos["snare updates"] = 0
        
        pl=player
        
        if(draw_transcript):
            transcript=[]
        
        while(
            (alternating        and any([phi.map[i].infty==0 for i in range(self.game.size)])) or
            (not(alternating)   and any([not(phi.validity_of_vert[i][1-player]) and phi.map[i].infty * (-1)**player < 1 for i in range(self.game.size)]))
        ):            
            
            if(time.time() > start_time + self.timeout):
                self.is_timeout = True
                break
            
            if(draw_transcript):
                transcript.append(deepcopy(phi))
            
            phi.snare_lift(pl)
            self.infos["snare updates"] += 1
            
            if(alternating):
                pl = 1 - pl
                
        
        self.infos["runtime"] = time.time() - start_time
        
        if(draw_transcript):
            transcript.append(phi)
            
        if(chrono):
            self.infos["chrono"] = phi.infos["chrono"]
        
        if(alternating):
            self.solution = [i for i in range(self.game.size) if (phi.map[i].infty == 1)]

        else:
            if(player):
                self.solution = [i for i in range(self.game.size) if (phi.map[i].infty != -1)]
            else:
                self.solution = [i for i in range(self.game.size) if (phi.map[i].infty == 1)]
    
        if(draw_transcript):
            
            for t in range(self.infos["snare updates"]+1):
                phi=transcript[t]
                        
                edges_with_attributes = [(i,j,phi.attribute_of_edge(edge_ind)) for edge_ind, (i,j,_) in enumerate(self.game.edges)]
                nodes_with_attributes = [(i,phi.attribute_of_vertex(i)) for i in range(self.game.size)]

                G = nx.MultiDiGraph()

                G.add_nodes_from(nodes_with_attributes)
                G.add_edges_from(edges_with_attributes)

                G.graph['edge'] = {'arrowsize': '0.6', 'splines': 'curved'}
                G.graph['graph'] = {'scale': '1'}

                A = to_agraph(G)
                
                A.layout('dot')                                                                 
                A.draw(transcript_filename + "{:03d}".format(t) + ".png")
    
    
    