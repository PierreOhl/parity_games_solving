import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util

edges = [(0, 0, 6), (0, 3, 10), (1, 3, 9), (1, 2, 1), (2, 2, 7), (2, 3, 8), (3, 1, 7), (3, 0, 9)]
g = games.parity_game(4, 10, edges, [1,1,0,0])
g = games.parity_game.generate_random(10,2)

g_en = games.energy_game.from_parity_game(g)

ziel = parity_executions.execution(g,100000)
ziel.zielonka_algorithm()
ziel.printinfos()
print(ziel.solution)

snare = energy_executions.execution(g_en, 10000)
snare.asymmetric_snare_update(0)
snare.printinfos()
print(snare.solution)


while True:
    g = games.parity_game.generate_random_fast(600,2,600)
    
    ziel = parity_executions.execution(g,10)
    ziel.zielonka_algorithm()
    ziel.printinfos()
    
    g_en = games.energy_game.from_parity_game(g)
    snare = energy_executions.execution(g_en,10)
    snare.asymmetric_snare_update(0)
    snare.printinfos()
    
    if(ziel.solution != snare.solution):
        print(g.edges)
        break
    
