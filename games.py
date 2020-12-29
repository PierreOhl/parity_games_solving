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
        str_edges = file.readline().replace(" ", "")
        str_player = file.readline().replace(" ", "")
        player = list(map(int, str_player.split(",")))
        edges = str_edges.split("),(")
        m = len(edges)
        edges[0] = edges[0][1:]
        edges[m-1] = edges[m-1][:-2]
        for i in range(m):
            edges[i] = tuple(map(int, edges[i].split(",")))        
        file.close()
        return(parity_game(n, d, edges, player))
        
    def tostring(self):
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
