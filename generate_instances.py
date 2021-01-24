import os
import games
import util
    
size= 600
max_param= 600
degree= 2
number_of_instances=200
typ="parity"

dir_name = "instances/" + typ + "/size" + str(size) + "max" + str(max_param) + "deg" + str(degree)


if not os.path.exists(dir_name):
    os.makedirs(dir_name)

for inst in range(number_of_instances):
    if(typ == "parity"):
        g = games.parity_game.generate_random_fast(size, degree, max_param)
    elif(typ == "energy"):
        g = games.energy_game.generate_random_fast(size, degree, max_param)
    f = open(dir_name + "/" + "{:04d}".format(inst), "w+")
    f.write(g.to_string())
    f.close()
