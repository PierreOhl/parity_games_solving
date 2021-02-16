import games
import parity_progress_measures
import energy_progress_measures
import parity_executions
import energy_executions
import trees
import util
import transcript

g = games.parity_game.generate_random_fast_bipartite(100,2,4)
g_en = games.energy_game.from_parity_game(g)


i=0
while(True):
    i+=1
    print("instance ", i)
    g_en = games.energy_game.generate_random_fast_bipartite(100,2,5)
    g_en = g_en.boost_weights_to_remove_null_cycles()


    sneve = energy_executions.execution(g_en,10)
    sneve.fast_asymmetric_snare_update(0)
    sneve.printinfos()

    snadam = energy_executions.execution(g_en,10)
    snadam.fast_asymmetric_snare_update(1)
    snadam.printinfos()

    snalt = energy_executions.execution(g_en,10)
    snalt.fast_alternating_snare_update()
    snalt.printinfos()
    
    if(snalt.infos["snare updates"] > sneve.infos["snare updates"] + snadam.infos["snare updates"]):
        print("ici")
        break

    if(snalt.solution != sneve.solution):
        print("problem")
        break
        
conj=0
'''
for i in range(g.size):
    print("vertex", i)
    print("Max iteration: ", sneve.infos["trajectory"][i])
    print("Min iteration: ", snadam.infos["trajectory"][i])
    print("Alternating: ", snalt.infos["trajectory"][i])
    if(sneve.infos["trajectory"][i][0] == '0' and snalt.infos["trajectory"][i][1] < snadam.infos["trajectory"][i][0]):
        conj=i

print(conj)'''