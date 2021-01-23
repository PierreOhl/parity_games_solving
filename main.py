import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util


#debug
edges =  [(0, 1, 1), (1, 0, 2)]
g = games.parity_game(2, 3, edges, [int(i<1) for i in range(2)])

print(g.to_string())
g2 = games.parity_game.from_string(g.to_string())
g2.save_to_file("game0")
print(g2.to_string())

g3 = games.parity_game.from_file("game0")
print(g3.to_string())

'''
i=0
n=600
max_prio=600
timeout=50
while(True):
    i = i+1
    print("instance ", i)
    
    g_par = util.parity_generate_random_fast(n,2,max_prio)
    g = games.energy_game.from_parity_game(g_par)

    exec_snare_eve = energy_executions.execution(g, timeout)
    exec_snare_eve.asymmetric_snare_update(0)
    exec_snare_eve.printinfos()
    
    exec_snare_adam = energy_executions.execution(g, timeout)
    exec_snare_adam.asymmetric_snare_update(1)
    exec_snare_adam.printinfos()
    
    exec_alt = energy_executions.execution(g, timeout)
    exec_alt.alternating_snare_update()
    exec_alt.printinfos()

    exec_ziel = parity_executions.execution(g_par, timeout)
    exec_ziel.zielonka_algorithm()
    exec_ziel.printinfos()
        
'''