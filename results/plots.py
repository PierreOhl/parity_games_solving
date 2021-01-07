import matplotlib.pyplot as plt


file = open("size600deg2")

file.readline()
file.readline()

info = [[0 for i in range(200)] for j in range(4)]

for i in range(200):
    s = file.readline()[:-2]
    l = s.split(",")
    print(l)
    for j in range(4):
        if(j%2 == 1):
            info[j][i] = int(l[j])
        else:
            info[j][i] = float(l[j])
    
    
plt.plot(info[2], info[0], "ro")
plt.show()
