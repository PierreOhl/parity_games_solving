import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript
import time
import random

size=5
thrshold=size-2
maxparam=10
once=True
choice_mode="alwaysZN_top_level"
if once:
    g=games.game.generate_random(3000,3000)
    #g = games.game(g.size,g.max_param, [(i,j,w//2) for i,j,w in g.edges],g.player,g.typ)
    #g.save_to_file("size6_snare_update_8iterbis")

    exec=energy_executions.execution(g,10)
    exec2= energy_executions.execution(g,10)

    #exec.recursive_reduction(choice_mode="alwaysZN_top_level")
    #print(exec.infos["iter_top_level"])

    exec.recursive_reduction(forgetfull= False)
    exec2.recursive_reduction()

    print(exec.infos["runtime"])
    print(exec2.infos["runtime"])
    if(exec.solution != exec2.solution):
        print("probleme")




else:
    mm=0
    for k in range(100000000):
        #deg=random.randrange(2,size)
        deg=2
        g=games.game.generate_random(size,maxparam,typ="energy", no_zero_cycles=True, well_spread_degree=size, degree=deg)

        exec=energy_executions.execution(g,10)

        exec.recursive_reduction(choice_mode=choice_mode)
        #exec.snare_update()

        m=exec.infos['iter_same_N']
        if m>mm:
            mm=m
            if(m>thrshold):
                filename="size"+str(size)+"_"+choice_mode+"_"+str(m)+"iter_same_N"
                #filename="size"+str(size)+"_snare_update_"+str(m)+"iter"
                if(choice_mode=="random"):
                    file = open("instances/"+ filename +"_infos", 'w+')
                    file.write(str(exec.infos))
                    file.close()
                g.save_to_file(filename)
        print(mm,k)
            