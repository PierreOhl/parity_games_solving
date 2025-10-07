import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript
import time

g=games.game.Friedmann09bis(10)
g=g.to_energy()

if(False):
    for reverse_weights in [0,1]:
        for reverse_players in [0,1]:
            for solving_player in [0,1]:
                if(reverse_weights):
                    g=g.reverse_all_weights()
                if(reverse_players):
                    g=g.reverse_players()
                
                execsnare=energy_executions.execution(g,10)
                execsnare.snare_update(player=solving_player,write_transcript=True)

                print("reverse weights: " + str(reverse_weights) + "    reverse players: " + str(reverse_players) + "      solving player: " + str(solving_player)) 
                execsnare.printinfos()
        

for n in range(1,100):

    g=games.game.Friedmann09bis(n)
    g=g.to_energy()
    g.save_to_file("fried1")
    g=g.reverse_players()

    print("param = " + str(n))
    print("size = " + str(g.size))
    print("number edges = " + str(len(g.edges)))

    execsnare=energy_executions.execution(g,10)
    execsnare.recursive_reduction()

    print(execsnare.infos["iter_top_level"])