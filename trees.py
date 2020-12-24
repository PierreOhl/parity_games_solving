

class node:
    ''' 
    node:
        (for now, in a complete tree)
        - height_of_tree = height of the tree -1 (number of parameters)
        - depth = depth_of_node (root has depth 0, corresponds to [])
        - degree of tree
        - value is a list of size <= height
            -> now, the first component corresponds to **largest** priority
    ''' 

    def __init__(self, height, degree, value):
        self.height_of_tree = height
        self.depth = len(value)
        self.degree = degree
        self.value = value
        if(self.depth > height):
            print("SHOULD NOT BE HERE 1")
            
    def print(self):
        print("NODE:")
        print("height %d, depth %d, degree %d, value:" % (self.height_of_tree, self.depth, self.degree))
        print(self.value)

    def in_subtree(self, pos):
        l = 0
        if(pos.height != self.height_of_tree):
            print("SHOULD NOT BE HERE 2")
        while(l< self.depth and self.value[l] == pos.value[self.height_of_tree - l - 1]):
            l+=1
        return(l == self.depth)

    def first_not_in_subtree(self):
        rep = position(self.height_of_tree, self.degree)
        for l in range(self.depth):
            rep.value[self.height_of_tree - l - 1] = self.value[l]
        rep.set_to_next(self.height_of_tree - self.depth)
        return(rep)

    def children(self):
        if(self.depth > self.height_of_tree-1):
            print("SHOULD NOT BE HERE 3")
        return([node(self.height_of_tree, self.degree, self.value + [i]) for i in range(self.degree)])

class box:
    '''
    a box is a pair of nodes.
    it should be that the both have same depth
    or the first has one less
    '''
    def __init__(self, node0, node1):
        self.pair=[node0, node1]
        if(node0.height_of_tree != node1.height_of_tree):
            print("SHOULD NOT BE HERE 4")
        if(not(node0.depth in [node1.depth, node1.depth -1])):
            print("SHOULD NOT BE HERE 5")
    
    def print(self):
        print("BOX:")
        print("node 0:")
        self.pair[0].print()
        print("node 1:")
        self.pair[1].print()
    
    def in_box(self, pair_of_pos):
        return(    self.pair[0].in_subtree(pair_of_pos[0]) 
               and self.pair[1].in_subtree(pair_of_pos[1])
               and not(pair_of_pos[0].is_top)
               and not(pair_of_pos[1].is_top)
               )
    
    def subboxes(self):
        if(self.pair[0].depth == self.pair[1].depth): #expand first node
            return([box(self.pair[0], child1) for child1 in self.pair[1].children()])
        else:
            return([box(child0, self.pair[1]) for child0 in self.pair[0].children()])
        
class position:
    ''' 
    position:
        (for now, leaf of a complete tree)
        - height = of the tree -1 (number of parameters) 
        - degree = degree of complete tree
        - value is a list of size height
             -> the first component corresponds to small priority
        - is_top is true if we have reached top
    ''' 

    def __init__(self, height, degree):
        self.height = height
        self.degree = degree
        self.value = [0 for i in range(height)]
        self.is_top = False

    def set_to_top(self):
        self.is_top = True

    def smaller(self, pos):
        if(pos.is_top):
            return(True)
        if(self.is_top):
            return(pos.is_top)
        h=self.height-1
        while(self.value[h] == pos.value[h] and h > 0):
            h=h-1
        return(self.value[h] <= pos.value[h])

    def set_to_next(self, lvl):
        '''
            changes the position to the next one at given lvl
        '''
        for i in range(lvl):
            self.value[i]=0
        i=lvl
        while(i < self.height and self.value[i] == self.degree - 1):
            self.value[i]=0
            i+=1
        if(i == self.height):
            self.set_to_top()
        else:
            self.value[i] += 1

    def min_source_for_valid_edge(self, player, priority):
        '''
            returns the smallest position that has a valid edge
            with given priority towards self, in player's semantic
        '''
        rep = position(self.height, self.degree)
        if self.is_top:
            rep.set_to_top()
            return(rep)
        else:
            h=(priority-player)//2
            for i in range(h,self.height):
                rep.value[i]=self.value[i]
            if(priority%2 != player):
                rep.set_to_next(h)
            return(rep)
        
    def print(self):
        print("POSITION:")
        print("height ", self.height)
        print("degree ", self.degree)
        print("is top ", self.is_top)
        print("value")
        print(self.value)
