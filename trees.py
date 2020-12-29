from copy import deepcopy

class node_in_infinite_tree:
    '''
    node_in_infinite_tree:
        - height_of_tree = height of the tree -1 (number of parameters)
        - depth = depth_of_node (root has depth 0, corresponds to [])
        - degree of tree
        - value is a list of size <= height
            -> now, the first component corresponds to **largest** priority
    ''' 
    
    def __init__(self, height, value):
        self.height_of_tree = height
        self.depth = len(value)
        self.value = value
        if(self.depth > height):
            print("SHOULD NOT BE HERE 1")
    
    def in_subtree(self, pos):
        l = 0
        if(pos.height != self.height_of_tree):
            print("SHOULD NOT BE HERE 2")
        while(l< self.depth and self.value[l] == pos.value[self.height_of_tree - l - 1]):
            l+=1
        return(l == self.depth)
    
    def first_not_in_subtree(self):
        rep = position_in_infinite_tree(self.height)
        if(self.depth == 0):
            rep.set_to_top()
        else:
            for l in range(self.depth):
                rep.value[self.height_of_tree - l - 1] = self.value[l]
            rep.value[self.height_of_tree - self.depth] +=1
        return(rep)
    
    
class node_in_complete_tree:
    ''' 
    node_in_complete_tree:
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

    def in_subtree(self, pos):
        l = 0
        if(pos.height != self.height_of_tree):
            print("SHOULD NOT BE HERE 2")
        while(l< self.depth and self.value[l] == pos.value[self.height_of_tree - l - 1]):
            l+=1
        return(l == self.depth)

    def first_not_in_subtree(self):
        rep = position_in_complete_tree(self.height_of_tree, self.degree)
        for l in range(self.depth):
            rep.value[self.height_of_tree - l - 1] = self.value[l]
        rep.set_to_next(self.height_of_tree - self.depth)
        return(rep)

    def children(self):
        if(self.depth > self.height_of_tree-1):
            print("SHOULD NOT BE HERE 3")
        return([node_in_complete_tree(self.height_of_tree, self.degree, self.value + [i]) for i in range(self.degree)])

class box:
    '''
    a box is a pair of nodes.
    it should be that the both have same depth
    or the first has one less.
    in the first case, player is 0, and player is
    1 in the second case.
    '''
    def __init__(self, node0, node1):
        self.pair = [node0, node1]
        if(node0.height_of_tree != node1.height_of_tree):
            print("SHOULD NOT BE HERE 4")
        if(not(node0.depth in [node1.depth, node1.depth -1])):
            print("SHOULD NOT BE HERE 5")
        self.player = node1.depth - node0.depth
        
    def in_box(self, pair_of_pos):
        return(    self.pair[0].in_subtree(pair_of_pos[0]) 
               and self.pair[1].in_subtree(pair_of_pos[1])
               and not(pair_of_pos[0].is_top)
               and not(pair_of_pos[1].is_top)
               )
    
    def subboxes(self):
        if(self.player == 0):
            return([box(self.pair[0], child1) for child1 in self.pair[1].children()])
        else:
            return([box(child0, self.pair[1]) for child0 in self.pair[0].children()])
        
    def parent(self):
        rep = deepcopy(self)
        if(rep.pair[self.player].value != []):
            rep.pair[self.player].value.pop()
            rep.pair[self.player].depth -= 1
        return(rep)
    
        
class position_in_infinite_tree:
    '''
    position_in_infinite_tree:
        (for now, leaf of an infinite complete tree)
        - height = of the tree -1 (number of parameters)
        - value is a list of size height
             -> the first component corresponds to small priority
        - is_top is true if we have reached top
    '''
    
    def __init__(self, height):
        self.height = height
        self.value = [0 for i in range(height)]
        self.is_top = False
    
    def __eq__(self, other):
        return( (self.height == other.height) and
                (self.value  == other.value ) and
                (self.is_top == other.is_top)     )

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
        
    def min_source_for_valid_edge(self, player, priority):
        '''
            returns the smallest position that has a valid edge
            with given priority towards self, in player's semantic
        '''
        rep = position_in_infinite_tree(self.height)
        if self.is_top:
            rep.set_to_top()
            return(rep)
        else:
            h=(priority-player)//2
            for i in range(h,self.height):
                rep.value[i]=self.value[i]
            if(priority%2 != player):
                rep.value[h] += 1
            return(rep)

    
class position_in_complete_tree:
    ''' 
    position_in_complete_tree:
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
        rep = position_in_complete_tree(self.height, self.degree)
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
