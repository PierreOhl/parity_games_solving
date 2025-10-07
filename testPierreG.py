import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript
import time

g = games.game.from_file("instances/size6_alwaysZN_top_level_6iter")

exec = energy_executions.execution(g,10)

exec.recursive_reduction(choice_mode="alwaysZN_top_level",draw_top_level_filename="drawings/testPierreGDrawFolder/exec")




