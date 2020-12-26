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
            
    def save_to_file(self, name):
        file = open("instances/"+name, 'w')
        file.write(self.tostring())
        file.close()
    
    @classmethod
    def fromfile(cls, filename):
        file = open("instances/" + filename, 'r')
        n = int(file.readline())
        d = int(file.readline())
        str_edges = file.readline()
        str_player = file.readline()
        player = list(map(int, str_player.split(", ")))
        edges = str_edges.split("), (")
        m = len(edges)
        edges[0] = edges[0][1:]
        edges[m-1] = edges[m-1][:-2]
        for i in range(m):
            edges[i] = tuple(map(int, edges[i].split(", ")))        
        file.close()
        return(parity_game(n, d, edges, player))
        
    def tostring(self):
        return(str(self.size) + '\n'
            + str(self.max_priority) + '\n'
            + str(self.edges)[1:-1] + '\n'
            + str(self.player)[1:-1]
        )
        
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
