import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript

g = games.game.generate_random_fast_parity(10,2,5)
g_en = games.game.to_energy_small_weights(g)

exec = energy_executions.execution(g_en,10)
exec.snare_update(draw_transcript=True, transcript_filename="transcripts/test1")
