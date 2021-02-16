import matplotlib.pyplot as plt
import transcript
import math 

size = 20000
max_param = 20000
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

log_ratio = [math.log(transcripts[1][inst].infos["runtime"] / transcripts[0][inst].infos["runtime"],10) for inst in range(number_of_instances)]

hi = math.floor(max(log_ratio))
lo = math.floor(min(log_ratio))

print(log_ratio)

levels = [len([1 for i in range(number_of_instances) if math.floor(log_ratio[i]) == l]) for l in range(lo, hi+1)]

rang = [lo] + sorted(([i for i in range(lo+1, hi+1)] + [i for i in range(lo+1, hi+1)])) + [hi+1]

stutlev = [levels[i//2] for i in range(2*(hi - lo + 1))]

plt.plot(rang, stutlev)

print(sum(levels))

plt.xlabel("log(snare_runtime / uzlk_runtime)")

plt.ylabel("number of instances")
plt.title("buckets for log ratio" + str(size))

plt.savefig("some_plots/buckets_for_thomas"+ str(size))
