from copy import deepcopy
import random as rand

class energy_game:
    '''
    energy game blabla
    '''
    def __init__(self, n, max_absolute_value, edges, player):
        self.size = n
        self.edges = edges
        self.number_edges = len(edges)
        self.player = player
        self.succ = [[] for i in range(n)]
        self.pred = [[] for i in range(n)]
        self.max_absolute_value = max_absolute_value
        for t in edges:
            self.pred[t[1]].append((t[0],t[2], len(self.succ[t[0]])))
            self.succ[t[0]].append((t[1],t[2]))
    
    @classmethod
    def from_parity_game(cls, parity_game):
        edges = [(i,j,((-1)*parity_game.size) ** p) for (i,j,p) in parity_game.edges]
        max_absolute_value = parity_game.size ** parity_game.max_priority
        return(energy_game(parity_game.size, max_absolute_value, edges, parity_game.player))
    
    def to_string(self):
        return(str(self.size) + '\n'
            + str(self.max_absolute_value) + '\n'
            + str(self.edges)[1:-1] + '\n'
            + str(self.player)[1:-1]
        )
    
    @classmethod
    def from_string(cls, s):
        lines = s.split("\n")
        str_edges = lines[2].replace(" ","")
        str_player = lines[3].replace(" ","")
        player = list(map(int, str_player.split(",")))
        edges = str_edges.split("),(")
        m = len(edges)
        edges[0] = edges[0][1:]
        edges[m-1] = edges[m-1][:-1]
        for i in range(m):
            edges[i] = tuple(map(int, edges[i].split(",")))
        return(energy_game(int(lines[0]), int(lines[1]), edges, player))
    
    @classmethod
    def from_file(cls, filename):
        file = open("instances/energy/" + filename, 'r')
        s = file.read()
        file.close()
        return(energy_game.from_string(s))
    
    
    def save_to_file(self, filename):
        file = open("instances/energy/" + filename, 'w+')
        file.write(self.to_string())
        file.close()
        
        
    @classmethod
    def generate_random_fast(cls, size, degree, max_absolute_value):
        edges=[]
        for i in range(size):
            for h in range(degree):
                j = rand.randrange(size)
                w = rand.randrange(2*max_absolute_value) - max_absolute_value
                edges.append((i,j,w))
        player=[int(i<size//2) for i in range(size)]
        return(energy_game(size, max_absolute_value, edges, player))
    
    
    @classmethod
    def generate_random_fast_bipartite(cls, size, degree, max_absolute_value):
        edges=[]
        med = size//2
        for i in range(size):
            for h in range(degree):
                j = rand.randrange(med) + (i < med) * med
                p = rand.randrange(2*max_absolute_value) - max_absolute_value
                edges.append((i,j,p))
        player=[int(i<med) for i in range(size)]
        return(energy_game(size, max_absolute_value, edges, player))
 

    
class parity_game:
    ''' 
    jeu de parité :
            - size taille du jeu
                -> un sommet est un entier dans [O,n-1]
            
            - max_priority borne sup paire sur priorités
                -> le jeu a des priorités dans [1,d]
            
            - number_edges nombre d'arêtes
                -> une arête est un tuple (sommet, sommet', priorité)

            - edges liste des arrêtes
            
            - succ table des successeurs (redondant)
                -> succ[i] est une liste de tuples (sommet', priorité)
            
            - pred table des successeurs (redondant)
                -> pred[i] est une liste de triplets (sommet, priorité, ind),
                où ind est l'indice dans succ[sommet] de l'arrête (i, sommet, priorité)
                
            - player est une liste de 0,1 de taille n
    '''

    def __init__(self, n, d, edges, player):
        self.size = n
        self.max_priority = d
        self.edges = edges
        self.number_edges = len(edges)
        self.player = player
        self.succ = [[] for i in range(n)]
        self.pred = [[] for i in range(n)]
        for t in edges:
            self.pred[t[1]].append((t[0],t[2], len(self.succ[t[0]])))
            self.succ[t[0]].append((t[1],t[2]))

        
        
    #returns games in min parity semantic, reversing and turning
    # 1,..., d into 2,..., d+1 (leaving room in 0,1 for "tops")
    def to_min_parity(self):
        edges = deepcopy(self.edges)
        for e in range(self.number_edges):
            edges[e] =(
                edges[e][0],
                edges[e][1],
                self.max_priority - edges[e][2] + 2
            )
        return(parity_game(self.size, self.max_priority + 1, edges, self.player))


    #returns game in max partity semantinc, reversing and turning
    # 2,..., d+1 into 1,..., d
    def to_max_parity(self):
        edges = deepcopy(self.edges)
        for e in range(self.number_edges):
            edges[e] =(
                edges[e][0],
                edges[e][1],
                self.max_priority - edges[e][2] + 1
            )
        return(parity_game(self.size, self.max_priority - 1, edges, self.player))
        
            
    def save_to_file(self, name):
        file = open("instances/parity/" +name, 'w+')
        file.write(self.to_string())
        file.close()
    
    
    #computes player attractor to vert_sub in subgame restricted to
    #vert_set and priority <= max_prio_sub.
    def attr_in_subgame(self, vert_set, max_prio_sub, target_set, player):
        edges_out = {i:len([s in vert_set and s not in target_set and p <= max_prio_sub for (s,p) in self.succ[i]]) for i in vert_set if i not in target_set and self.player[i] != player}
        rep = deepcopy(target_set)
        for i in [i for i in vert_set if i not in target_set and self.player[i] != player]:
            if edges_out[i] == 0:
                edges_out.pop(i)
                rep.add(i)
        treat_pred = deepcopy(rep)
        while(treat_pred):
            i = treat_pred.pop()
            for (pre,prio,_) in self.pred[i]:
                if(prio <= max_prio_sub and pre in vert_set and pre not in rep):
                    if(self.player[pre] == player):
                        rep.add(pre)
                        treat_pred.add(pre)
                    else:
                        edges_out[pre] -= 1
                        if(edges_out[pre] == 0):
                            edges_out.pop(pre)
                            rep.add(pre)
                            treat_pred.add(pre)
        return(rep)
    
    #computes one-step player d%2 attractor to priority d in
    #subgame restricted to vert_set and edges of priority <= d+1
    def one_step_to_prio_in_subgame(self, vert_set, d):
        return({i for i in vert_set if 
            (self.player[i] == d%2      and any([p == d for (s,p) in self.succ[i] if s in vert_set]) )
        or  (self.player[i] == (d+1)%2  and all([p == d for (s,p) in self.succ[i] if p <= d and s in vert_set]))})

    
    #computes player d%2 attractor to priority d in subgame
    #restricted to vert_set and edges of priority <= d+1
    def attr_to_prio_in_subgame(self, vert_set, d):
        target_set = self.one_step_to_prio_in_subgame(vert_set, d)
        return(self.attr_in_subgame(vert_set, d, target_set, d%2))
    
    
    @classmethod
    def from_file(cls, filename):
        file = open("instances/parity/" + filename, 'r')
        s = file.read()
        file.close()
        return parity_game.from_string(s)
    
    @classmethod
    def from_string(cls, s):
        lines = s.split("\n")
        str_edges = lines[2].replace(" ","")
        str_player = lines[3].replace(" ","")
        player = list(map(int, str_player.split(",")))
        edges = str_edges.split("),(")
        m = len(edges)
        edges[0] = edges[0][1:]
        edges[m-1] = edges[m-1][:-1]
        for i in range(m):
            edges[i] = tuple(map(int, edges[i].split(",")))
        return(parity_game(int(lines[0]), int(lines[1]), edges, player))
    
    def to_string(self):
        return(str(self.size) + '\n'
            + str(self.max_priority) + '\n'
            + str(self.edges)[1:-1] + '\n'
            + str(self.player)[1:-1]
        )
        
    #builds a hard example for Zielonka
    @classmethod
    def hard_for_zielonka(cls, even_top_priority):
        width = 4
        size = width * (even_top_priority - 1)
        edges = []
        for h in range(even_top_priority-1):
            for w in range(width -1):
                edges.append((h * width + w + 1, h * width + w, h + 1))
                if(w % 2 == 1):
                    edges.append((h * width + w, h * width + w + 1, h + 2))
                else:
                    edges.append((h * width + w, h * width + w + 1, h + 1))
        for h in range(even_top_priority - 4):
            edges.append((h * width + width - 1, (h+2) * width, h+1))
        for h in range(1, even_top_priority-1):
            for w in range(width -1):
                if w%2 == 0:
                    edges.append((h * width + w, (h-1) * width + w, h+1))
        player = [(i // width + i + 1) % 2 for i in range(size)]
        return(parity_game(size, even_top_priority, edges, player))
    
    
    @classmethod
    def generate_random(cls, size, average_deg):
        edges=[]
        for i in range(size):
            j = rand.randrange(size)
            p = rand.randrange(size) +1
            edges.append((i,j,p))
        if(average_deg > 1):    
            invproba = size * size // (average_deg-1)
            for i in range(size):
                for j in range(size):
                    for p in range(1,size+1):
                        r = rand.randrange(invproba)
                        if(r==0):
                            edges.append((i,j,p))
        eve=[int(i<size//2) for i in range(size)]
        return(parity_game(size, size, edges, eve))
    
    
    @classmethod
    def generate_random_fast(cls, size, degree, max_prio):
        edges=[]
        for i in range(size):
            for h in range(degree):
                j = rand.randrange(size)
                p = rand.randrange(max_prio) +1
                edges.append((i,j,p))
        player=[int(i<size//2) for i in range(size)]
        return(parity_game(size, max_prio, edges, player))
    
    
    @classmethod
    def generate_random_fast_bipartite(cls, size, degree, max_prio):
        edges=[]
        med = size//2
        for i in range(size):
            for h in range(degree):
                j = rand.randrange(med) + (i < med) * med
                p = rand.randrange(max_prio) +1
                edges.append((i,j,p))
        player=[int(i<med) for i in range(size)]
        return(parity_game(size, max_prio, edges, player))

    
    @classmethod
    def generate_random_fast_bipartite_opponent_edges(cls, size, degree, max_prio):
        edges=[]
        med = size//2
        for i in range(size):
            for h in range(degree):
                j = rand.randrange(med) + (i < med) * med
                p = 2*(rand.randrange(max_prio//2)) + (i<med) +1
                edges.append((i,j,p))
        player=[int(i<med) for i in range(size)]
        return(parity_game(size, max_prio, edges, player))
