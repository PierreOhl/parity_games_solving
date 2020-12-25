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
            self.succ[t[0]].append((t[1],t[2]))
            self.pred[t[1]].append((t[0],t[2]))
            
    def print(self):
        print("PARITY GAME:")
        print("game size: ", self.size)
        print("maximal priority", self.max_priority)
        print("number of edges", len(self.edges))
        print("set of edges:")
        print(self.edges)
        print("list of successors:")
        for i in range(self.size):
            print("successors of state %d: (index, priority)" % i)
            print(self.succ[i])
        print("players:", self.player)
