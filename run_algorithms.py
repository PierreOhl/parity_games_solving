import parity_executions
import energy_executions
import games
import os

size= 25000
max_param= 25000
degree=2
typ="parity"
labels_on_vertices=True
start = 48
end = 49
timeout = 1000

algorithms={}
algorithms["parity"]=[]
algorithms["energy"]=["fast_alternating_snare"]

dir_name = "size" + str(size) + "max" + str(max_param) + "deg" + str(degree)

for ty in ["parity", "energy"]:
    for alg in algorithms[ty]:
        if(labels_on_vertices):
            if not os.path.exists("executions/" + ty + "/on_vert/" + alg + "/" + dir_name):
                os.makedirs("executions/" + ty + "/on_vert/" + alg + "/" + dir_name)
        else:
            if not os.path.exists("executions/" + ty + "/" + alg + "/" + dir_name):
                os.makedirs("executions/" + ty + "/" + alg + "/" + dir_name)

for inst in range(start, end):
    if(typ == "parity"):
        if(labels_on_vertices):
            g_vert = games.parity_game_priorities_on_vertices.from_file(dir_name + "/" + "{:04d}".format(inst))
            g = games.parity_game.from_priority_on_vertices(g_vert)
        else:
            g = games.parity_game.from_file(dir_name + "/" + "{:04d}".format(inst))
    
    if(len(algorithms["energy"])>0):
        g_energy = games.energy_game.from_parity_game(g)
    
    for parity_alg in algorithms["parity"]:
        
        exe = parity_executions.execution(g, timeout)
        
        if(parity_alg == "zielonka"):
            exe.zielonka_algorithm()
        #add other algorithms
        
        exe.save_to_file(parity_alg + "/" + dir_name + "/" + "{:04d}".format(inst))

    for energy_alg in algorithms["energy"]:
        
        exe = energy_executions.execution(g_energy, timeout)
        
        if(energy_alg == "asym_snare_eve"):
            exe.asymmetric_snare_update(0)
        
        if(energy_alg == "asym_snare_adam"):
            exe.asymmetric_snare_update(1)
        
        if(energy_alg == "brim_et_al"):
            exe.asymmetric_lifting_standard(0)
        
        if(energy_alg == "alternating_snare"):
            exe.alternating_snare_update()
            
            
        if(energy_alg == "fast_asym_snare_eve"):
            exe.fast_asymmetric_snare_update(0)
        
        if(energy_alg == "fast_asym_snare_adam"):
            exe.fast_asymmetric_snare_update(1)
        
        if(energy_alg == "fast_alternating_snare"):
            exe.fast_alternating_snare_update()
    
        if(labels_on_vertices):
            exe.save_to_file("on_vert/" + energy_alg + "/" + dir_name + "/" + "{:04d}".format(inst))
        else:
            exe.save_to_file(energy_alg + "/" + dir_name + "/" + "{:04d}".format(inst))
        