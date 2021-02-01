import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript

size=3
par=5
edges=[(0, 2, 4), (1, 2, 3), (2, 1, 1), (2, 1, 3), (2, 1, 6)]
g = games.parity_game(size, par, edges, [i<size//2 for i in range(size)])


g = games.parity_game.generate_random_fast(50000, 2, 50000)
g = games.parity_game_priorities_on_vertices.generate_random_bipartite(10000, 10000, 2)
g.save_to_file("0005")

g = games.parity_game.from_priority_on_vertices(g)


g_en = games.energy_game.from_parity_game(g)

'''
ziel = parity_executions.execution(g, 1000)
ziel.zielonka_algorithm()
ziel.printinfos()'''

snarfalt = energy_executions.execution(g_en, 1000)
snarfalt.fast_alternating_snare_update()
snarfalt.printinfos()



snarfast = energy_executions.execution(g_en, 1000)
snarfast.fast_asymmetric_snare_update(0)
snarfast.printinfos()
'''
snarfadam = energy_executions.execution(g_en, 1000)
snarfadam.fast_asymmetric_snare_update(1)
snarfadam.printinfos()
'''