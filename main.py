import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript

n=15
maxw = 150
for i in range(100):
    g = games.game.generate_random_fast_energy(n,2,maxw)

    exec = energy_executions.execution(g,10)
    exec.snare_update(draw_transcript=True, transcript_filename="transcripts/random15ene_sym/inst{:02d}_iter".format(i), alternating=True)
