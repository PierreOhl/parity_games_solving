import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript

i=0
while(True):
    print("try",i)
    i+=1
    g = games.game.generate_random_fast_energy(20,2,1000)
    e = energy_executions.execution(g,10)
    e.snare_update(write_transcript=True)
    md = e.any_increase_in_max_delta()
    if(any([(type(md[i]) is int and type(md[i+1]) is int and md[i+1] > md[i]) for i in range(len(md) -1)])):
        print("ici")
        print(md)
        e.draw_transcript("transcripts/test3")
        break