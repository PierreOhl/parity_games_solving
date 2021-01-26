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
        for edge_ind in range(self.number_edges):
            self.pred[edges[edge_ind][1]].append((edges[edge_ind][0], edge_ind))
            self.succ[edges[edge_ind][0]].append((edges[edge_ind][1], edge_ind))
    
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
    
    
    @classmethod
    def DKZ19_worst_case(cls, n): 
        #{0,...,n-1}={x_1,...,x_n} ; n = v ; {n+1 ,...,2n}={y_1,...,y_n} ;  2n+1 = u
        size = 2 * n + 2
        max_absolute_value = 3 * 2**n - 3
        player=[0 for i in range(n+1)] + [1 for i in range(n+1)]
        edges = [(i, i+1, 0) for i in range(n)] + [(n+i+1, n+i+2, 0) for i in range(n)] #Change the first to -1 for something more difficult
        edges.append((0,n+2,-(3-2))) #x_i-> y_{i+1}
        edges.append((n+1, 1 , 3-2 )) #y_i-> x_{i+1}
        for i in range(1,n):
            edges.append((i,n+i+2,-(3*2**i-2))) #x_i-> y_{i+1}
            edges.append((n+i+1, i+1 , 3*2**i-2 )) #y_i-> x_{i+1}
            edges.append((n+i+1, n+1 , 3*2**(i-1)-1 )) #y_i-> y_1
        edges.append((n,n,-1))
        edges.append((n, 2 * n + 1, -(3 * (2**n) - 3)))
        edges.append((2 * n + 1, 2 * n + 1, 1))
        edges.append((n+1, 0, 0))
        return(energy_game(size, max_absolute_value, edges, player))
    
    
    @classmethod
    def cycle_game(cls, size):
        max_absolute_value = 1
        edges = [(i,i+1,-1) for i in range(size-1)]
        edges.append((0,0,1))
        player = [0 for i in range(size)]
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
                -> succ[i] est une liste de tuples (sommet', edge_ind)
            
            - pred table des successeurs (redondant)
                -> pred[i] est une liste de triplets (sommet, edge_ind)
                
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
        for edge_ind in range(self.number_edges):
            self.pred[edges[edge_ind][1]].append((edges[edge_ind][0], edge_ind))
            self.succ[edges[edge_ind][0]].append((edges[edge_ind][1], edge_ind))

        
        
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
        edges_out = {i:len([s in vert_set and s not in target_set and self.edges[edge_ind][2] <= max_prio_sub for (s,edge_ind) in self.succ[i]]) for i in vert_set if i not in target_set and self.player[i] != player}
        rep = deepcopy(target_set)
        for i in [i for i in vert_set if i not in target_set and self.player[i] != player]:
            if edges_out[i] == 0:
                edges_out.pop(i)
                rep.add(i)
        treat_pred = deepcopy(rep)
        while(treat_pred):
            i = treat_pred.pop()
            for (pre,edge_ind) in self.pred[i]:
                if(self.edges[edge_ind][2] <= max_prio_sub and pre in vert_set and pre not in rep):
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
            (self.player[i] == d%2      and any([self.edges[edge_ind][2] == d for (s,edge_ind) in self.succ[i] if s in vert_set]) )
        or  (self.player[i] == (d+1)%2  and all([self.edges[edge_ind][2] == d for (s,edge_ind) in self.succ[i] if self.edges[edge_ind][2] <= d and s in vert_set]))})

    
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
    def Friedmann09(cls, n): #MAX-parity
        #vertices = [b, a, d, e, f, g, h, k , s, r, p, q, c]
        #b_0=0, a_0=2n, d_0=4n, e_0=5n, f_0=6n, g_0=7n, h_0=8n, k_0=9n, s=10n, r=10n+1, p=10n+2, q=10n+3 c=10n+4
        #priorities in outgoing edges
        a_0=2*n
        d_0=4*n
        e_0=5*n
        f_0=6*n
        g_0=7*n
        h_0=8*n 
        k_0=9*n
        s=10*n
        r=10*n+1
        p=10*n+2
        q=10*n+3 
        c=10*n+4
        size = 10*n+5
        even_top_priority = 12*n + 8
        player = [0 for i in range(2*n)]+[1 for i in range(2*n)] #b and a
        player = player + [0 for i in range(n)] + [1 for i in range(2*n)] #d, e and f
        player = player + [0 for i in range(n)] + [1 for i in range(n)] + [0 for i in range(n)]#g, h and k
        player = player + [0 ,0, 1, 1, 0] #s, r, p, q and c
        #edges from b_0
        edges=[(0,s, 4*n+3), (0,r, 4*n+3), (0,c, 4*n+3)] 
        #From c to {s,r}
        edges.append((c,s, 8*n + 4))
        edges.append((c,r, 8*n + 4))
        #From {s,r} to p
        edges.append((s,p,2))
        edges.append((r,p, 8*n+6))
        for i in range(1,2*n):
            #From b_i
            edges.append((i,i-1,4*n+2*i+3))
            edges.append((i,s,4*n+2*i+3))
            edges.append((i,r,4*n+2*i+3))
            #From a_i-1
            edges.append((a_0+i-1,i-1,4*n+2*i+4))
        edges.append((a_0+2*n-1,2*n-1,4*n+4*n+4)) #Last one for a_i
        for i in range(n):
            #From s to f_i
            edges.append((s,f_0+i,2))
            #From r to g_i
            edges.append((r,g_0+i,8*n+6))
            #From d_i 
            edges.append((d_0+i,s,4*i+3))
            edges.append((d_0+i,r,4*i+3))
            edges.append((d_0+i,e_0+i,4*i+3))
            for j in range(2*i+2):
                edges.append((d_0+i,a_0+j,4*i+3))
            #From e_i
            edges.append((e_0+i,d_0+i,4*i+4))
            edges.append((e_0+i,h_0+i,4*i+4))
            #From g_i
            edges.append((g_0+i,f_0+i,4*i+6))
            edges.append((g_0+i,k_0+i,4*i+6))
            #From k_i
            edges.append((k_0+i,p,8*n+4*i+7))
            for j in range(i+1,n):
                edges.append((k_0+i,g_0+j,8*n+4*i+7))
            #From f_i
            edges.append((f_0+i,e_0+i,8*n+4*i+9))
            #From h_i
            edges.append((h_0+i,k_0+i,8*n+4*i+10))
        edges.append((q,q,1))
        edges.append((p,q,12*n+8))
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