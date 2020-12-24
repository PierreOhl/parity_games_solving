import games
import trees
import progress_measures
import executions
import random as rand
import time
import util

#returns true if times out
def empty(phi, box, timeout, start_time, infos):
    infos["number of recursive calls"]+=1
    if(time.time() > start_time + timeout):
        return(True)        
    if(phi.accelerate(box)):
        return(False)
    scope_init = phi.list_in_box(box)
    very_invalid = phi.list_dest_not_in_box(box)
    while(very_invalid != []):
        i = util.pickrandom(very_invalid)
        phi.lift(i)
        infos["number of updates"]+=1
        very_invalid=phi.list_dest_not_in_box(box)
    if(phi.accelerate(box)):
        return(False)
    for sub in box.subboxes():
        if empty(phi, sub, timeout, start_time, infos):
            return(True)
    return(False)

def symetric_lifting(game, timeout):
    phi = progress_measures.sym_progress_measure_strong(game)  
    start_time = time.time()
    b = trees.box(trees.node(game.max_priority//2, game.size, []), trees.node(game.max_priority//2, game.size, []) )
    rep = executions.execution(game, timeout)
    
    rep.infos["number of updates"]=0
    rep.infos["number of recursive calls"]=0    
    
    rep.is_timeout = empty(phi, b, start_time, timeout, rep.infos)
    rep.runtime = time.time() - start_time
    rep.solution = [i for i in range(game.size) if not(phi.pair[0].map[i].is_top)]
    return(rep)
    
