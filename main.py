import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript

g = games.game.generate_random_fast_parity(1000,2,1000)
g_en = g.to_energy()

#g = games.game(3,4,[(0, 2, 3), (0, 0, 4), (1, 2, 1), (1, 0, 2), (2, 0, 4), (2, 1, 2)], [1,0,0],"parity")

#print(g.to_string())

exec_ziel = parity_executions.execution(g, 10)
#exec_ziel.zielonka_algorithm()
exec_ziel.printinfos()
#print(exec_ziel.solution)

exec_snare = energy_executions.execution(g, 100000)
exec_snare.fast_alternating_snare_update()
exec_snare.printinfos()
#print(exec_snare.solution)

exec_snareb = energy_executions.execution(g_en, 100000)
exec_snareb.fast_alternating_snare_update()
exec_snareb.printinfos()
#print(exec_snareb.solution)