import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript

g=games.game.generate_random(3,3,typ="energy")

exec=energy_executions.execution(g,10)
exec.snare_update()
exec.printinfos()

execGKK=energy_executions.execution(g,10000)
execGKK.solve_GKK()
execGKK.printinfos()

print(exec.solution)
print(execGKK.solution)