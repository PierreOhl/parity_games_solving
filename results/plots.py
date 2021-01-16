import matplotlib.pyplot as plt


file = open("size600deg2prio600")

file.readline()
file.readline()

info = [[0 for i in range(100)] for j in range(4)]

for i in range(100):
    s = file.readline()[:-1]
    l = s.split(",")
    print(l)
    for j in range(4):
        if(j%2 == 1):
            info[j][i] = int(l[j])
        else:
            info[j][i] = float(l[j])

no_timeout = [[info[j][i] for i in range(100) if info[2][i] < 180] for j in range(4)]
timeout = [[info[j][i] for i in range(100) if info[2][i] >= 180] for j in range(4)]

plt.plot(no_timeout[3], no_timeout[1], "ro")
plt.plot(timeout[3], timeout[1], "rv")
plt.plot([0,10000], [0,10000])



plt.xlabel("Zielonka equivalent updates ({:2d}% timeout)".format(len(timeout[0])))
plt.ylabel("Symmetric no reset updates")
plt.title("100 instances of size 600 with 600 priorities and degree 2 (updates)")

plt.show()
