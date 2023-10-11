import util
import heapq

class progress_measure:
    
    def __init__(self, game):
        self.game = game
        
        # Change the game data structures so that things can be easily deleted
        self.remaining_vertices = {i for i in range(game.size)} # Keep only vertices not yet assigned +/-infty
        self.remaining_succ = [{} for _ in range(game.size)]
        self.remaining_pred = [{} for _ in range(game.size)]
        for edge in game.edges:
            self.remaining_succ[edge[0]][edge[1]] = edge[2] # ! Assume at most one edge between two directed vertices
            self.remaining_pred[edge[1]][edge[0]] = edge[2]
            
        # if game.typ == "energy":
        self.map = [None for _ in range(game.size)] # potential values
        # else:
        #    self.map = [util.sparse_tuple() for _ in range(game.size)]

    # TODO: Currently only implements the case player == 0, which is maximizing   
    def snare_lift(self, player):
        # --- Data structure initialisation ---
        
        # List the vertices of the main player going to the fixed region;
        # should only be accessed through functions from heapq
        heap_edges_to_fixed = []
        
        # Counts the number of nonpositive outgoing edges of each vertex of the opponent
        number_nonpositive_outgoing_edges = {}
        for v in self.remaining_vertices:
            self.map[v] = None
            if self.game.player[v] == 1:
                number_nonpositive_outgoing_edges[v] = sum(1 for w in self.remaining_succ[v].values() if w <= 0)
        
        # Vertices for which the value is known but must still be processed
        to_treat = []
        
        # Initialisation: fix vertices that reach a positive edge in one step
        for v in self.remaining_vertices:
            if self.game.player[v] == 0:
                if any(w > 0 for w in self.remaining_succ[v].values()):
                    to_treat.append(v)
                    self.map[v] = 0
            else: # player[v] == 1
                if all(w > 0 for w in self.remaining_succ[v].values()):
                    to_treat.append(v)
                    self.map[v] = 0
        
        # --- Main loop ---
        while to_treat or heap_edges_to_fixed:
            while to_treat:
                v2 = to_treat.pop()
                for (v1, w) in self.remaining_pred[v2].items():
                    if self.game.player[v1] == 0:
                        # Weight comes first to exploit the min lexicographic ordering, the "-" is a quick hack to inverse the ordering
                        heapq.heappush(heap_edges_to_fixed, (- (w + self.map[v2]), v1, v2))
                    elif w <= 0: # player[v1] == 1
                        number_nonpositive_outgoing_edges[v1] -= 1
                        if number_nonpositive_outgoing_edges[v1] == 0:
                            to_treat.append(v1)
                            self.map[v1] = min(self.map[v2] + w2 for (v2, w2) in self.remaining_succ[v1].items() if w2 <= 0)
            
            # If nothing to treat left, takes the smallest edge from the main player
            if heap_edges_to_fixed:
                w, v1, v2 = heapq.heappop(heap_edges_to_fixed) # smallest edge from player to fixed region
                if self.map[v1] == None: # Not fixed yet
                    to_treat.append(v1)
                    self.map[v1] = - w # Quick hack for the w here, as it was inverted earlier
        
        # --- Postprocessing ---
        # Remove vertices and outgoing edges that are +infty
        vertices_to_remove = [v for v in self.remaining_vertices if self.map[v] is None] # Not fixed
        for v in vertices_to_remove:
            self.map[v] = float("-inf")
            self.remaining_vertices.remove(v)
            for v2 in list(self.remaining_succ[v].keys()):
                del self.remaining_succ[v][v2]
                del self.remaining_pred[v2][v]
        
        # Update the value of the remaining edges using the potential value
        for v in self.remaining_vertices:
            for v2, w in self.remaining_succ[v].items():
                self.remaining_succ[v][v2] = w + self.map[v2] - self.map[v]
                self.remaining_pred[v2][v] = w + self.map[v2] - self.map[v]
        
        # Return True if it was not the last iteration (something changed), False otherwise
        return (vertices_to_remove and self.remaining_vertices) or any(self.map[v] != 0 for v in self.remaining_vertices)


    def attribute_of_edge(self, edge_ind):
        rep={}
        (i,j,w) = self.game.edges[edge_ind]
        modified_weight = self.map[j] - self.map[i] + w
        one_endpoint_infty = self.map[i].infty or self.map[j].infty
        rep["label"] = modified_weight.to_label()
        if(modified_weight.infty):
            rep["color"] = {1:"red", -1:"blue"}[modified_weight.infty]
        else:
            if(modified_weight.is_zero()):
                rep["color"] = "black"
            elif(modified_weight.is_positive()):
                rep["color"] = "red"
            else:
                rep["color"] = "blue"
        rep["fontcolor"] = rep["color"]
        return(rep)

        
    def attribute_of_vertex(self, i):
        rep={}
        rep["shape"] = ["circle", "box"][self.game.player[i]]
        rep["regular"] = 1
        rep["label"] = util.number_to_letters(i+1,len(util.base26(self.game.size)))
        if(self.map[i].infty):
            rep["color"] = {1:"red", -1:"blue"}[self.map[i].infty]
        else:
            if(self.validity_of_vert[i] == [1,0]):
                rep["color"] = "lightcoral"
            elif(self.validity_of_vert[i] == [0,1]):
                rep["color"] = "lightblue"
            else:
                rep["color"] = "lightgray"
        rep["style"] = "filled"
        return(rep)


    def type_config(self):
        rep=[0]*self.game.size
        for i in range(self.game.size):
            succweights=[(self.map[j] - self.map[i] + self.game.edges[edge_ind][2]) for (j,edge_ind) in self.game.succ[i]]
            if(all([w<0 for w in succweights])):
                rep[i]=-1
            if(any([w>0 for w in succweights])):
                rep[i]=1
        return(rep)

