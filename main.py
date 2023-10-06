import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript

g=games.game.generate_random(10,100,typ="energy",one_player=True)


exec=energy_executions.execution(g,10)
exec.snare_update(alternating=True, write_transcript=True)
exec.printinfos()
exec.draw_transcript(filename="drawings/test1")
print(exec.does_type_vector_repeat())

print(exec.solution)