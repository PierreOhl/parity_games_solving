import random as rand
from copy import deepcopy

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