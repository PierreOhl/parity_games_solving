import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript
import time

size=100
thrshold=size-1
maxparam=10
once=False
choice_mode="smallest"
if once:
    g=games.game.from_file("instances/test11")
    phi = energy_progress_measures.progress_measure(g)
    phi.draw("drawings/draw11")
    exec=energy_executions.execution(g,10)

    exec.recursive_reduction(choice_mode="alwaysZN_top_level")

    print(exec.infos["iter_top_level"])



else:
    mm=0
    for k in range(100000000):
        g=games.game.generate_random(size,maxparam,typ="energy", no_zero_cycles=True, well_spread_degree=0)


        g.save_to_file("test11")
        exec=energy_executions.execution(g,10)

        exec.recursive_reduction(choice_mode=choice_mode)

        m=exec.infos['iter_top_level']
        if m>mm:
            mm=m
            if(m>thrshold):
                filename="size"+str(size)+"_"+choice_mode+"_"+str(m)+"iter"
                if(choice_mode=="random"):
                    file = open("instances/"+ filename +"_infos", 'w+')
                    file.write(str(exec.infos))
                    file.close()
        print(mm,k)
            