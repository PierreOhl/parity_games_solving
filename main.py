import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript

for i in range(10):

    g = games.game.generate_random_fast_parity(10000,2,10000)
    g_en = g.to_energy()

    #g = games.game(3,4,[(0, 2, 3), (0, 0, 4), (1, 2, 1), (1, 0, 2), (2, 0, 4), (2, 1, 2)], [1,0,0],"parity")

    #print(g.to_string())


    exec_snare = energy_executions.execution(g_en, 100000)
    exec_snare.snare_update(alternating=False)
    exec_snare.printinfos()

    exec_snareb = energy_executions.execution(g_en, 100000)
    exec_snareb.snare_update()
    exec_snareb.printinfos()
    #print(exec_snareb.solution)