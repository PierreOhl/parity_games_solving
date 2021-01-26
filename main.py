import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript

edges = [(0, 1, 1), (1, 0, 2)]
g = games.parity_game(2, 2, edges, [1,0])

g = games.parity_game.from_file("size600max600deg2/0000")

g_en = games.energy_game.DKZ19_worst_case(50)


'''
ziel = parity_executions.execution(g, 1)
ziel.zielonka_algorithm()
ziel.printinfos()
print(ziel.solution)
'''
snar = energy_executions.execution(g_en, 100000)
snar.asymmetric_snare_update(0)
snar.printinfos()
print(snar.solution)

'''
while True:
    g = games.parity_game.generate_random_fast(2,2,2)
    g_en = games.energy_game.from_parity_game(g)

    ziel = parity_executions.execution(g, 1)
    ziel.zielonka_algorithm()
    ziel.printinfos()
    
    snar = energy_executions.execution(g_en, 10)
    snar.asymmetric_snare_update(0)
    snar.printinfos()
    
    if(snar.solution != ziel.solution):
        print(g.edges)
        break

'''