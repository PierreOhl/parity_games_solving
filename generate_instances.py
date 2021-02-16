import os
import games
import util
    
size= 25000
max_param= 25000
degree= 2
number_of_instances=100
typ="parity"
labels_on_vertices=True

if(labels_on_vertices):
    dir_name = "instances/" + typ + "_vertices/size" + str(size) + "max" + str(max_param) + "deg" + str(degree)


else:
    dir_name = "instances/" + typ + "/size" + str(size) + "max" + str(max_param) + "deg" + str(degree)


if not os.path.exists(dir_name):
    os.makedirs(dir_name)

for inst in range(number_of_instances):
    if(typ == "parity"):
        if(labels_on_vertices):
            g = games.parity_game_priorities_on_vertices.generate_random_bipartite(size, max_param, degree)
        else:
            g = games.parity_game.generate_random_fast(size, degree, max_param)
    elif(typ == "energy"):
        g = games.energy_game.generate_random_fast(size, degree, max_param)
    f = open(dir_name + "/" + "{:04d}".format(inst), "w+")
    f.write(g.to_string())
    f.close()
