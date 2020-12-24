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


