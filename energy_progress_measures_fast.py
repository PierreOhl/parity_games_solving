import util
import heapq

class progress_measure:
    
    def __init__(self, game):
        self.game = game
        
        # Change the game data structures so that things can be easily deleted
        self.remaining_vertices = {v for v in range(game.size)} # Keep only vertices not yet assigned +/-infty
        self.remaining_succ = [set() for _ in range(game.size)]
        self.remaining_pred = [set() for _ in range(game.size)]
        self.current_weights = {}
        self.current_player = [self.game.player[v] == 0 for v in range(game.size)]
        for edge in game.edges:
            self.remaining_succ[edge[0]].add(edge[1]) # ! Assume at most one edge between two directed vertices
            self.remaining_pred[edge[1]].add(edge[0])
            self.current_weights[(edge[0], edge[1])] = edge[2]
        
        self.map = [None for _ in range(game.size)] # potential values
    
    def alternate_game(self):
        for v in range(self.game.size):
            self.current_player[v] = not self.current_player[v]
            if self.map[v] is not None:
                self.map[v] = - self.map[v]
        for pair, w in self.current_weights.items():
            self.current_weights[pair] = -w

    # Assumes player == 0 is the maximizing player. Use alternate_game() beforehand to "inverse" the valuation.
    def snare_lift(self):
        # --- Data structure initialisation ---
        
        # List the edges of the main player going to the fixed region;
        # should only be accessed through functions from heapq
        heap_edges_to_fixed = []
        
        # Counts the number of nonpositive outgoing edges of each vertex of the opponent
        number_nonpositive_outgoing_edges = {}
        for v in self.remaining_vertices:
            self.map[v] = None
            if not self.current_player[v]: # opponent
                number_nonpositive_outgoing_edges[v] = sum(1 for v2 in self.remaining_succ[v] if self.current_weights[(v, v2)] <= 0)
        
        # Vertices for which the value is known but must still be processed
        to_treat = []
        
        # Initialisation: fix vertices that reach a positive edge in one step
        for v in self.remaining_vertices:
            if self.current_player[v]:
                if any(self.current_weights[(v, v2)] > 0 for v2 in self.remaining_succ[v]):
                    to_treat.append(v)
                    self.map[v] = 0
            else: # vertex of the opponent
                if all(self.current_weights[(v, v2)] > 0 for v2 in self.remaining_succ[v]):
                    to_treat.append(v)
                    self.map[v] = 0
        
        # --- Main loop ---
        while to_treat or heap_edges_to_fixed:
            while to_treat:
                v2 = to_treat.pop()
                for v1 in self.remaining_pred[v2]:
                    w = self.current_weights[(v1, v2)]
                    if self.current_player[v1]:
                        # Weight comes first to exploit the min lexicographic ordering, the "-" is a quick hack to inverse the ordering
                        heapq.heappush(heap_edges_to_fixed, (- (w + self.map[v2]), v1))
                    elif w <= 0: # opponent vertex and nonpositive weight
                        number_nonpositive_outgoing_edges[v1] -= 1
                        if number_nonpositive_outgoing_edges[v1] == 0:
                            to_treat.append(v1)
                            self.map[v1] = min(self.map[v3] + self.current_weights[(v1, v3)] for v3 in self.remaining_succ[v1] if self.current_weights[(v1, v3)] <= 0)
            
            # If nothing to treat left, takes the smallest edge from the main player to the fixed region
            if heap_edges_to_fixed:
                w, v1 = heapq.heappop(heap_edges_to_fixed) # smallest edge from player to fixed region
                if self.map[v1] == None: # Not fixed yet
                    to_treat.append(v1)
                    self.map[v1] = - w # Quick hack for the w here, as it was inverted earlier
        
        # --- Postprocessing ---
        # Remove vertices and outgoing edges that are +infty
        vertices_to_remove = [v for v in self.remaining_vertices if self.map[v] is None] # Not fixed
        for v in vertices_to_remove:
            self.map[v] = float("-inf")
            self.remaining_vertices.remove(v)
            for v2 in list(self.remaining_succ[v]):
                self.remaining_succ[v].remove(v2)
                self.remaining_pred[v2].remove(v)
                del self.current_weights[(v, v2)]
        
        # Update the value of the remaining edges using the potential value
        for v in self.remaining_vertices:
            for v2 in self.remaining_succ[v]:
                if self.map[v] != self.map[v2]: # Used to limit the number of operations
                    self.current_weights[(v, v2)] += self.map[v2] - self.map[v]
        
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

