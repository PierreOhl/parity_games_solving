import parity_executions
import energy_executions
import games
import os

size= 600
max_param= 600
degree=2
typ="parity"
start = 0
end = 200
timeout = 100

algorithms={}
algorithms["parity"]=["zielonka"]
algorithms["energy"]=[]

dir_name = "size" + str(size) + "max" + str(max_param) + "deg" + str(degree)

for ty in ["parity", "energy"]:
    for alg in algorithms[ty]:
        if not os.path.exists("executions/" + ty + "/" + alg + "/" + dir_name):
            os.makedirs("executions/" + ty + "/" + alg + "/" + dir_name)

for inst in range(start, end):
    if(typ == "parity"):
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
        
        exe.save_to_file(energy_alg + "/" + dir_name + "/" + "{:04d}".format(inst))
        