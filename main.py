import games
import progress_measures
import executions
import trees
import random as rand


def generate_random(size, average_deg):
    invproba = size * size // average_deg
    edges=[]    
    for i in range(size):
        for j in range(size):
            for p in range(1,size):
                r = rand.randrange(invproba)
                if(r==0):
                    edges.append((i,j,p))
    eve=[i<size//2 for i in range(size)]
    rep = games.parity_game(size, size, edges, eve)
    return(rep)



'''
# a trivial game won by Adam
edges=[(0,1,2), (1,0,2), (1,1,1)]
g=games.parity_game(2, 2, edges, [0,1])
'''
'''
# a trivial game won by Eve 
edges=[(0,1,2), (1,0,2), (1,1,1), (0,0,2)]
g=games.parity_game(2, 2, edges, [0,1])
'''
'''
# a trivial game which has a sink
edges=[]
g=games.parity_game(2, 2, edges, [1,1])
'''

'''
# a game of size 20
edges=[(0, 9, 8), (0, 13, 0), (0, 16, 2), (0, 18, 17), (1, 4, 13), (1, 12, 1), (2, 4, 6), (3, 7, 14), (3, 18, 0), (3, 19, 1), (4, 0, 1), (4, 1, 12), (4, 1, 17), (4, 2, 10), (4, 5, 17), (4, 12, 17), (5, 0, 4), (5, 0, 8), (5, 9, 7), (6, 4, 15), (6, 4, 16), (6, 8, 2), (7, 18, 11), (8, 7, 8), (12, 13, 3), (12, 13, 6), (13, 8, 14), (13, 19, 11), (14, 2, 3), (14, 2, 11), (14, 14, 0), (15, 8, 4), (15, 11, 14), (18, 11, 17), (19, 10, 10), (19, 13, 16)]
g=games.parity_game(20, 20, edges, [i<10 for i in range(20)])
'''
'''
# a game of size 5
edges=[(0, 2, 0), (0, 2, 3), (0, 4, 2), (1, 1, 2), (1, 1, 4), (1, 4, 0), (1, 4, 3), (2, 0, 3), (3, 2, 3), (3, 3, 0), (3, 3, 2), (3, 3, 4), (3, 4, 3)]
g=games.parity_game(5, 5, edges, [i<2 for i in range(20)])
'''
'''
# a hard instance of size 50
edges=[(0, 8, 19), (0, 24, 44), (0, 31, 29), (0, 40, 28), (1, 39, 36), (2, 34, 41), (3, 8, 36), (3, 18, 40), (4, 32, 41), (5, 9, 24), (5, 16, 39), (5, 18, 30), (5, 19, 10), (6, 5, 5), (6, 42, 39), (7, 3, 2), (7, 9, 19), (7, 20, 30), (7, 31, 11), (7, 45, 14), (7, 47, 44), (8, 37, 15), (9, 8, 41), (9, 33, 46), (10, 9, 12), (10, 11, 42), (11, 20, 40), (11, 30, 15), (12, 10, 42), (13, 6, 11), (14, 3, 15), (15, 2, 26), (15, 43, 32), (16, 17, 17), (16, 25, 0), (17, 31, 1), (17, 49, 45), (18, 41, 4), (18, 45, 5), (19, 16, 18), (20, 0, 42), (20, 4, 21), (21, 8, 24), (21, 23, 28), (21, 26, 40), (21, 31, 42), (22, 16, 45), (22, 21, 34), (23, 1, 33), (23, 17, 5), (24, 13, 40), (25, 33, 26), (25, 38, 2), (27, 8, 38), (27, 26, 42), (27, 33, 12), (27, 38, 39), (27, 39, 35), (28, 26, 27), (28, 30, 10), (28, 41, 12), (28, 46, 16), (29, 6, 37), (30, 17, 46), (30, 36, 26), (31, 15, 6), (31, 17, 45), (31, 38, 6), (31, 40, 1), (31, 41, 31), (32, 21, 40), (32, 23, 40), (32, 34, 27), (33, 48, 33), (34, 6, 42), (34, 8, 36), (34, 26, 16), (34, 31, 28), (35, 9, 29), (35, 19, 24), (37, 40, 2), (38, 31, 21), (38, 41, 29), (39, 10, 31), (40, 28, 41), (41, 35, 21), (41, 41, 2), (41, 43, 45), (42, 2, 6), (42, 7, 15), (42, 17, 11), (42, 18, 33), (43, 6, 20), (43, 11, 31), (44, 3, 39), (45, 0, 13), (46, 1, 32), (46, 6, 35), (46, 7, 13), (46, 10, 10), (46, 48, 19), (47, 15, 14), (47, 16, 37), (48, 34, 0), (48, 46, 3), (48, 49, 2), (49, 25, 14)]
g=games.parity_game(50,50, edges, [i<25 for i in range(50)])
'''
'''
#an instance where some algorithms fail
edges=[(0, 4, 6), (1, 11, 10), (1, 16, 17), (1, 17, 8), (2, 1, 12), (2, 11, 4), (2, 17, 15), (2, 17, 19), (3, 2, 11), (3, 4, 0), (3, 19, 19), (4, 4, 5), (4, 6, 16), (4, 8, 0), (4, 9, 2), (5, 2, 13), (5, 14, 13), (6, 8, 16), (6, 11, 17), (6, 18, 0), (7, 15, 6), (7, 18, 19), (8, 1, 10), (8, 2, 13), (8, 4, 5), (8, 4, 12), (8, 5, 18), (8, 12, 12), (8, 18, 0), (8, 18, 9), (9, 0, 16), (9, 5, 19), (9, 14, 2), (9, 18, 18), (9, 19, 9), (10, 5, 4), (10, 9, 10), (10, 9, 18), (10, 11, 4), (10, 18, 0), (11, 2, 17), (11, 8, 12), (11, 11, 16), (12, 12, 7), (13, 13, 4), (14, 7, 3), (14, 8, 6), (14, 11, 17), (14, 14, 0), (16, 16, 19), (17, 0, 1), (17, 3, 13), (17, 4, 2), (17, 12, 1), (18, 8, 4), (18, 18, 10), (18, 19, 18), (19, 2, 11), (19, 2, 12), (19, 4, 6), (19, 7, 12)]
g=games.parity_game(20, 20, edges, [i<10 for i in range(20)])
'''
'''
#to debug zielonka
edges=[(1, 0, 1), (1, 1, 2), (1, 2, 1), (1, 2, 2), (1, 3, 0), (1, 3, 3), (2, 1, 0), (2, 2, 2), (2, 3, 0), (2, 3, 1), (3, 0, 2), (3, 0, 3), (3, 1, 1), (3, 1, 2)]
g=games.parity_game(4, 4, edges, [1,1,0,0])
'''
'''
# an instance of size 100
edges=[(0, 25, 51), (0, 29, 56), (1, 19, 51), (1, 91, 31), (2, 12, 36), (2, 39, 35), (4, 15, 19), (4, 35, 66), (5, 7, 40), (5, 28, 5), (5, 29, 8), (5, 61, 7), (5, 71, 65), (5, 89, 96), (6, 1, 93), (6, 33, 62), (6, 74, 28), (6, 76, 49), (7, 15, 17), (7, 49, 82), (8, 17, 7), (8, 23, 41), (9, 7, 36), (9, 52, 17), (9, 74, 85), (11, 51, 62), (11, 96, 93), (11, 98, 55), (12, 22, 86), (12, 45, 81), (12, 63, 45), (12, 91, 2), (13, 82, 41), (13, 83, 75), (14, 9, 20), (14, 14, 55), (15, 1, 95), (15, 56, 38), (16, 5, 96), (16, 30, 71), (16, 45, 42), (16, 60, 95), (16, 72, 96), (16, 78, 16), (17, 82, 83), (18, 2, 91), (18, 17, 67), (18, 49, 31), (18, 55, 43), (18, 71, 39), (19, 27, 77), (19, 91, 14), (19, 95, 62), (20, 13, 70), (20, 16, 17), (20, 26, 43), (20, 79, 42), (21, 92, 55), (22, 10, 31), (22, 22, 54), (22, 28, 70), (22, 66, 35), (22, 93, 24), (23, 69, 72), (23, 84, 50), (24, 58, 92), (24, 90, 77), (24, 92, 28), (24, 93, 73), (25, 20, 74), (25, 20, 98), (25, 52, 86), (25, 82, 30), (26, 93, 82), (27, 22, 49), (27, 84, 25), (27, 87, 85), (28, 5, 84), (28, 19, 97), (28, 41, 98), (28, 87, 71), (29, 1, 65), (29, 84, 51), (30, 45, 48), (30, 57, 65), (32, 63, 27), (33, 23, 54), (33, 61, 50), (34, 7, 19), (34, 83, 41), (34, 86, 92), (34, 90, 89), (35, 16, 24), (35, 57, 66), (35, 65, 81), (35, 72, 19), (36, 9, 20), (36, 31, 52), (36, 67, 9), (36, 87, 39), (36, 96, 25), (37, 83, 96), (37, 91, 34), (38, 9, 9), (38, 16, 64), (38, 23, 7), (38, 49, 12), (38, 62, 87), (38, 77, 99), (39, 15, 10), (39, 20, 84), (39, 41, 42), (39, 66, 58), (39, 68, 10), (39, 79, 84), (40, 47, 28), (40, 50, 90), (40, 64, 4), (40, 97, 21), (40, 98, 20), (41, 62, 45), (41, 63, 13), (41, 69, 42), (41, 70, 34), (41, 87, 69), (41, 92, 78), (42, 17, 6), (42, 47, 56), (42, 49, 69), (42, 56, 75), (43, 17, 67), (43, 85, 86), (43, 95, 52), (44, 34, 33), (45, 51, 38), (45, 77, 95), (46, 11, 32), (46, 73, 32), (47, 11, 16), (47, 32, 87), (47, 75, 75), (47, 97, 17), (48, 34, 97), (48, 35, 94), (48, 73, 96), (50, 67, 50), (50, 77, 40), (50, 89, 81), (51, 70, 61), (52, 27, 1), (52, 49, 78), (52, 64, 14), (52, 70, 19), (53, 61, 52), (53, 72, 7), (54, 11, 77), (54, 28, 29), (54, 99, 37), (55, 8, 89), (55, 22, 41), (55, 85, 19), (56, 28, 76), (56, 34, 99), (56, 90, 50), (57, 2, 21), (57, 24, 77), (57, 38, 74), (58, 69, 28), (59, 20, 79), (59, 29, 89), (59, 55, 98), (59, 68, 7), (59, 68, 25), (60, 18, 95), (60, 61, 12), (61, 33, 40), (61, 47, 18), (61, 80, 72), (61, 83, 9), (62, 21, 14), (62, 81, 71), (62, 90, 1), (63, 42, 75), (63, 61, 45), (63, 95, 61), (63, 99, 97), (64, 17, 9), (64, 67, 18), (65, 95, 28), (66, 2, 47), (66, 19, 9), (66, 38, 35), (67, 40, 90), (67, 89, 27), (68, 9, 48), (68, 44, 31), (68, 62, 31), (68, 63, 57), (68, 75, 64), (68, 85, 20), (69, 16, 27), (69, 29, 75), (69, 45, 12), (70, 30, 57), (70, 67, 53), (70, 70, 24), (70, 80, 8), (70, 89, 55), (70, 95, 57), (70, 95, 61), (71, 12, 38), (71, 31, 24), (71, 57, 3), (71, 69, 65), (72, 36, 96), (72, 51, 85), (72, 65, 64), (72, 84, 46), (73, 44, 10), (73, 46, 24), (73, 61, 75), (74, 13, 35), (74, 86, 53), (75, 8, 69), (75, 74, 90), (75, 80, 44), (76, 0, 32), (77, 29, 31), (77, 30, 53), (77, 45, 53), (77, 65, 60), (77, 67, 7), (78, 3, 16), (78, 11, 72), (78, 37, 49), (78, 41, 19), (78, 41, 26), (79, 8, 13), (79, 37, 71), (79, 39, 18), (79, 78, 56), (79, 88, 44), (79, 90, 41), (80, 7, 28), (80, 42, 94), (80, 96, 35), (81, 6, 62), (81, 54, 34), (82, 14, 85), (82, 14, 93), (82, 29, 50), (82, 50, 76), (82, 72, 25), (82, 84, 48), (83, 23, 65), (84, 8, 92), (84, 26, 69), (84, 51, 36), (84, 92, 25), (86, 11, 37), (86, 51, 41), (86, 62, 1), (87, 65, 47), (87, 67, 23), (87, 91, 77), (87, 99, 85), (88, 10, 84), (88, 45, 57), (88, 85, 95), (89, 34, 79), (89, 39, 61), (89, 43, 8), (89, 48, 2), (89, 57, 13), (89, 68, 38), (90, 92, 1), (91, 9, 20), (91, 12, 6), (91, 40, 86), (92, 80, 6), (92, 95, 62), (93, 13, 30), (93, 15, 75), (93, 78, 54), (93, 84, 76), (94, 33, 38), (94, 40, 97), (94, 87, 85), (95, 44, 15), (95, 93, 65), (96, 39, 16), (96, 47, 1), (97, 5, 71), (97, 9, 55), (97, 50, 52), (97, 71, 3), (98, 10, 14), (98, 13, 38), (98, 43, 92), (98, 75, 9), (98, 95, 82), (99, 63, 79), (99, 64, 54), (99, 68, 55), (99, 99, 26)]
g=games.parity_game(100,100, edges, [i<50 for i in range(100)])
'''
'''
# an instance of size 100
edges = [(0, 17, 72), (1, 59, 72), (1, 80, 12), (1, 97, 29), (3, 53, 73), (4, 7, 78), (4, 13, 87), (4, 19, 8), (4, 60, 86), (5, 18, 28), (5, 32, 14), (5, 60, 29), (6, 6, 63), (6, 26, 56), (6, 40, 5), (6, 72, 36), (6, 91, 37), (7, 8, 16), (7, 37, 30), (7, 91, 53), (8, 50, 42), (8, 70, 63), (9, 73, 21), (9, 76, 70), (10, 36, 16), (10, 64, 74), (11, 5, 55), (11, 86, 34), (12, 29, 71), (12, 35, 7), (12, 38, 14), (12, 41, 36), (12, 66, 4), (12, 71, 81), (12, 88, 42), (12, 92, 74), (13, 5, 9), (13, 27, 31), (13, 46, 11), (13, 47, 1), (13, 65, 8), (13, 83, 50), (14, 3, 43), (14, 11, 32), (14, 23, 51), (14, 28, 28), (14, 83, 47), (15, 12, 21), (15, 58, 82), (15, 76, 62), (15, 82, 83), (16, 45, 43), (16, 60, 59), (16, 61, 54), (16, 64, 2), (17, 37, 68), (17, 79, 71), (18, 1, 56), (18, 7, 46), (19, 51, 14), (21, 5, 82), (21, 41, 42), (21, 44, 78), (21, 46, 36), (21, 65, 41), (21, 75, 83), (21, 86, 34), (22, 5, 11), (22, 22, 76), (22, 37, 47), (23, 16, 21), (23, 28, 79), (23, 31, 8), (23, 38, 98), (23, 40, 6), (24, 3, 5), (24, 37, 76), (24, 45, 9), (24, 51, 34), (24, 85, 90), (25, 77, 51), (25, 89, 56), (26, 21, 86), (26, 28, 15), (26, 44, 9), (26, 54, 71), (26, 54, 95), (26, 55, 17), (27, 22, 29), (27, 41, 18), (27, 58, 46), (27, 99, 84), (28, 2, 63), (28, 22, 5), (28, 28, 68), (28, 31, 59), (29, 34, 80), (29, 55, 70), (29, 71, 86), (29, 86, 71), (30, 93, 70), (30, 99, 85), (32, 50, 26), (33, 51, 67), (33, 63, 82), (33, 83, 64), (35, 24, 37), (35, 74, 72), (35, 85, 74), (36, 70, 36), (38, 30, 87), (38, 72, 37), (38, 81, 36), (39, 31, 12), (39, 45, 48), (39, 50, 11), (39, 76, 49), (40, 40, 20), (40, 40, 68), (40, 79, 10), (40, 81, 20), (42, 7, 61), (42, 40, 19), (43, 8, 73), (44, 11, 20), (44, 20, 52), (44, 34, 6), (44, 34, 39), (45, 30, 25), (45, 99, 24), (46, 12, 35), (46, 33, 13), (47, 22, 8), (47, 53, 22), (47, 63, 3), (47, 76, 15), (47, 93, 73), (48, 33, 30), (48, 43, 16), (48, 43, 61), (48, 57, 97), (48, 68, 99), (48, 84, 44), (49, 7, 71), (49, 9, 9), (49, 35, 19), (49, 51, 36), (50, 1, 89), (50, 45, 41), (50, 57, 21), (52, 31, 26), (52, 96, 57), (53, 19, 21), (53, 48, 27), (53, 93, 86), (54, 31, 55), (54, 45, 86), (54, 69, 22), (54, 96, 78), (55, 1, 73), (55, 18, 63), (55, 29, 99), (55, 49, 92), (55, 56, 31), (55, 86, 76), (55, 90, 62), (55, 93, 8), (56, 6, 17), (56, 16, 28), (56, 26, 83), (56, 33, 39), (56, 70, 12), (56, 85, 73), (57, 25, 17), (57, 42, 16), (57, 64, 74), (58, 30, 78), (58, 56, 15), (58, 68, 75), (58, 75, 80), (59, 46, 66), (59, 50, 9), (59, 97, 54), (59, 99, 88), (60, 65, 87), (60, 78, 77), (61, 14, 43), (63, 6, 51), (63, 50, 20), (63, 50, 34), (63, 54, 29), (64, 22, 15), (64, 58, 48), (64, 80, 11), (65, 63, 41), (66, 13, 57), (66, 30, 37), (66, 41, 63), (66, 78, 63), (67, 4, 63), (68, 12, 21), (68, 82, 62), (68, 85, 38), (69, 54, 9), (69, 95, 8), (70, 64, 35), (71, 24, 38), (72, 4, 24), (72, 8, 8), (72, 12, 51), (73, 8, 86), (73, 20, 37), (73, 94, 86), (74, 44, 15), (74, 66, 47), (75, 17, 10), (75, 64, 82), (75, 68, 14), (75, 92, 51), (76, 7, 57), (76, 13, 43), (76, 69, 19), (76, 71, 24), (77, 38, 66), (77, 97, 88), (78, 22, 63), (78, 25, 80), (79, 17, 82), (79, 24, 89), (79, 89, 60), (80, 33, 37), (80, 70, 66), (80, 82, 44), (80, 92, 11), (81, 57, 92), (82, 44, 1), (82, 63, 26), (82, 69, 79), (82, 90, 50), (83, 23, 88), (83, 81, 46), (85, 10, 46), (85, 12, 61), (85, 41, 6), (86, 7, 31), (86, 37, 41), (86, 67, 91), (86, 70, 28), (86, 76, 32), (86, 97, 19), (87, 40, 88), (88, 3, 95), (88, 25, 37), (88, 29, 23), (88, 31, 73), (88, 59, 45), (88, 63, 74), (88, 88, 87), (88, 89, 75), (88, 98, 20), (89, 72, 50), (89, 86, 79), (89, 97, 57), (90, 6, 27), (90, 33, 96), (91, 7, 29), (91, 22, 22), (92, 90, 36), (93, 18, 84), (93, 99, 87), (94, 10, 43), (94, 39, 3), (94, 46, 40), (94, 50, 49), (94, 73, 98), (95, 36, 46), (95, 59, 85), (96, 22, 71), (96, 67, 7), (96, 99, 3), (97, 4, 52), (97, 23, 31), (97, 47, 24), (97, 76, 13), (97, 83, 64), (98, 15, 96), (98, 26, 44), (98, 76, 21), (99, 14, 96), (99, 43, 81), (99, 83, 45)]
g=games.parity_game(100,100, edges, [i<50 for i in range(100)])
'''

# an instance of size 4 where sym does more recursive calls than Ziel
edges = [(1, 3, 2), (2, 3, 3), (3, 1, 1), (3, 2, 1), (3, 3, 3)]
g=games.parity_game(4,4,edges,[1,1,0,0])

exec_sym = executions.execution(g, 10)
exec_sym.symmetric_lifting_strong()
exec_sym.printinfos()

exec_ziel = executions.execution(g, 10)
exec_ziel.zielonka_algorithm()
exec_ziel.printinfos()

'''
exec = executions.execution(g, 10)
exec.asymmetric_lifting(0)
exec.printinfos()

exec = executions.execution(g, 10)
exec.asymmetric_lifting(1)
exec.printinfos()
'''