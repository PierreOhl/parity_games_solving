import random as rand
from copy import deepcopy
import games

#outputs a random element of a (non-empty) list
def pickrandom(l):
    return(l[rand.randrange(len(l))])

'''
************************
*  ATTRACTOR-ROUTINES  *
************************
'''

#computes set of states from which player can immediately force
#to see an edge of priority p
#we assume that all edges from vert_set arrive in vert_set
def one_step_to_priority(vert_set, succ, vert_player, p, player):
    return({i for i in vert_set if 
            (vert_player[i] == player      and any([suc[1] == p for suc in succ[i]]) )
        or  (vert_player[i] == 1 - player  and all([suc[1] == p for suc in succ[i]]))})

#computes one-step attractor to set of vertices
#we assume that all edges from vert_set arrive in vert_set
def one_step_to_set_of_vertices(vert_set, succ, vert_player, target_set, player):
    return({i for i in vert_set if 
            (vert_player[i] == player      and any([suc[0] in target_set for suc in succ[i]]))
        or  (vert_player[i] == 1 - player  and all([suc[0] in target_set for suc in succ[i]]))})
    
#computes attractor to set of priorities    
#we assume that all edges from vert_set arrive in vert_set
def attractor_to_priority(vert_set, succ, vert_player, p, player):
    rep = one_step_to_priority(vert_set, succ, vert_player, p, player)
    add = one_step_to_set_of_vertices(vert_set, succ, vert_player, rep, player)
    while(any([i not in rep for i in add])):
        rep=rep.union(add)
        add = one_step_to_set_of_vertices(vert_set, succ, vert_player, rep, player)
    return(rep)

#computes attractor to set of vertices    
#we assume that all edges from vert_set arrive in vert_set
def attractor_to_set_of_vertices(vert_set, succ, vert_player, target_set, player):
    rep = deepcopy(target_set)
    add = one_step_to_set_of_vertices(vert_set, succ, vert_player, rep, player)
    while(any([i not in rep for i in add])):
        rep=rep.union(add)
        add = one_step_to_set_of_vertices(vert_set, succ, vert_player, rep, player)
    return(rep)

        

class partition_plus_node_data:
    '''
    describes a partition of [0,1, ..., number_of_elements -1] together
    with a different value for each subset
    - number of elements is the total number of elements
    - nparts is the number of subsets
    - values is a list of distinct values of size nparts
    - index is a list of size number_of_elements -1
    which gives index of each elements
    '''
    
    #we initialize the partition with one subset
    def __init__(self, number_of_elements, value):
        self.number_of_elements = number_of_elements
        self.nparts = 1
        self.values = [value]
        self.index = [0 for i in range(number_of_elements)]

    def is_a_value(self, value):
        return(value in self.values)
    
    def is_a_singleton(self, i):
        return(all([self.index[j] != self.index[i] for j in range(self.number_of_elements) if j != i]))

    #moves i to part with given value.
    #returns true if it has emptied i's initial subset
    def move(self, i, value):
        rep = self.is_a_singleton(i)
        
        if(rep): #reindexing
            for j in range(self.number_of_elements):
                if self.index[j] > self.index[i]:
                    self.index[j] -= 1
            self.values.pop(self.index[i])
            self.nparts -= 1
            
        #if value exists, add i there
        if(self.is_a_value(value)):
            self.index[i] = self.values.index(value)
        
        #otherwise, create new (singleton) part
        else:
            self.values.append(value)
            self.index[i] = self.nparts
            self.nparts += 1
        
        return(rep)
    
    def value_of(self, i):
        return(self.values[self.index[i]])
    
    
#returns true iff list1 is a prefix of list2
#assuming list1 is shorter than list2 
def is_prefix(list1, list2):
    ind=0
    while(ind < len(list1)):
        if(list1[ind] != list2[ind]):
            return(False)
        ind+=1
    return(True)

#returns the smallest index larger than start which is in
#given list of indices and has value
#false in the given list of booleans, and len(list) if
#there is no such index
def smallest_false_index_from_list_larger_than(start, list_of_booleans, list_of_indices):
    j=start
    while(j < len(list_of_booleans) and (list_of_booleans[j] or j not in list_of_indices)):
        j+=1
    return(j)

'''
********************************
*  GENERATION OF RANDOM GAMES  *
********************************
'''

def generate_random(size, average_deg):
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
    eve=[i<size//2 for i in range(size)]
    rep = games.parity_game(size, size, edges, eve)
    return(rep)

#generates a game in max semantics
def generate_random_fast(size, degree, max_prio):
    edges=[]
    for i in range(size):
        for h in range(degree):
            j = rand.randrange(size)
            p = rand.randrange(max_prio) +1
            edges.append((i,j,p))
    player=[i<size//2 for i in range(size)]
    rep = games.parity_game(size, max_prio, edges, player)
    return(rep)

#generates a bipartite game (max semantics)
def generate_random_fast_bipartite(size, degree, max_prio):
    edges=[]
    med = size//2
    for i in range(size):
        for h in range(degree):
            j = rand.randrange(med) + (i < med) * med
            p = rand.randrange(max_prio) +1
            edges.append((i,j,p))
    player=[i<med for i in range(size)]
    rep = games.parity_game(size, max_prio, edges, player)
    return(rep)

def generate_random_fast_bipartite_opponent_edges(size, degree, max_prio):
    edges=[]
    med = size//2
    for i in range(size):
        for h in range(degree):
            j = rand.randrange(med) + (i < med) * med
            p = 2*(rand.randrange(max_prio//2)) + (i<med) +1
            edges.append((i,j,p))
    player=[i<med for i in range(size)]
    rep = games.parity_game(size, max_prio, edges, player)
    return(rep)



#compares two positions in alternating lexicographic order
def is_smaller_alt_lex(map1, map2, height):
    h=0
    while(h<height):
        if(map1[h] == map2[h]):
            h+=1
        else:
            return(((map1[h] > map2[h]) + h) % 2)
    return(True)