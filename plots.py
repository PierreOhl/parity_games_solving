import matplotlib.pyplot as plt
import transcript

size = 25000
max_param = 25000
deg = 2
number_of_instances=100

display_diagonal = True

number_of_algorithms = 2

display_axis_and_title = True

labels_on_vertices = True

logscale = [False, True]

typs = ("energy", "oink")
algs = ("fast_alternating_snare", "uzlk")

param = ("runtime", "runtime")

instances = [i for i in range(number_of_instances)]

transcripts = ([],[])

for inst in instances:
    for alg_ind in range(number_of_algorithms):
        if(typs[alg_ind] != "oink"):
            if(labels_on_vertices):
                transcripts[alg_ind].append(transcript.transcript.from_file(
                typs[alg_ind],
                "on_vert/" + algs[alg_ind],
                size,
                max_param,
                deg,
                inst
            ))
            else:
                transcripts[alg_ind].append(transcript.transcript.from_file(
                typs[alg_ind],
                algs[alg_ind],
                size,
                max_param,
                deg,
                inst
            ))
        else:
            transcripts[alg_ind].append(transcript.transcript.from_oink(
                "uzlk",
                size, 
                max_param, 
                deg, 
                inst
            ))

timeouts = [any([transcripts[alg_ind][inst].is_timeout for alg_ind in range(number_of_algorithms)]) for inst in range(number_of_instances)]

plt.rcParams["axes.titlesize"] = 8

axis_no_timeout = [[transcripts[alg_ind][inst].infos[param[alg_ind]] for inst in range(number_of_instances) if not(timeouts[inst])] for alg_ind in range(number_of_algorithms)]
axis_timeout = [[transcripts[alg_ind][inst].infos[param[alg_ind]] for inst in range(number_of_instances) if timeouts[inst]] for alg_ind in range(number_of_algorithms)]

if(logscale[0]):
    plt.xscale("log")

if(logscale[1]):
    plt.yscale("log")

plt.plot(axis_no_timeout[0], axis_no_timeout[1], "ro")
plt.plot(axis_timeout[0], axis_timeout[1], "r^")

if(display_diagonal):
    axes=plt.gca()
    xmin, xmax = axes.get_xlim()
    res = 1000
    delta= (xmax - xmin) / res
    diag_points = [xmin + i*delta for i in range(res)]
    plt.plot(diag_points, diag_points)


for inst in range(number_of_instances):
    if(transcripts[0][inst].infos["runtime"]>100):
        print(inst)

if display_axis_and_title:
    plt.title(algs[0] + " " + param[0] + " vs " + algs[1] + " " + param[1] + " on " + str(number_of_instances) + " instances of size" + " " + str(size))
    plt.xlabel(algs[0] + " " + param[0] + ["", " (logscale)"][logscale[0]])
    plt.ylabel(algs[1] + " " + param[1] + ["", " (logscale)"][logscale[1]])

plt.savefig("some_plots/" + algs[0] + "_" + param[0] + ["", "(logscale)" ][logscale[0]] + "_vs_" + algs[1] + "_" + param[1] + ["", "(logscale)" ][logscale[1]] + "_on_" + str(number_of_instances) + "_instances_of_size" + "_" + str(size))
