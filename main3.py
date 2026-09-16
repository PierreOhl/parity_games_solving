import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript
import time

tries=100000
ex=1
size=3
maxedge=2

if ex==1:
    #g=games.game.generate_random(3,8)
    g = games.game.from_file("instances/debug-bipotential")
    g.save_to_file("debug-bipotential")

    exec=energy_executions.execution(g,1000000)

    exec.bipotential_iteration()

    exec.printinfos()

    print("solution set is " + str(exec.solution))

else:
    for i in range(tries):
        print(i)
        g=games.game.generate_random(size,maxedge,no_zero_cycles=True)
        
        g.save_to_file("debug-bipotential2")

        exec=energy_executions.execution(g,10)

        exec.bipotential_iteration()

        exec.printinfos()

        print("solution set is " + str(exec.solution))