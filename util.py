import random as rand
from copy import deepcopy
import games

#outputs a random element of a (non-empty) list
def pickrandom(l):
    return(l[rand.randrange(len(l))])

def truncate_to_one(x):
    if(x==0):
        return(x)
    else:
        return(x//abs(x))
class possibly_infinite_integer:
    '''
    defines possibly infinite integers by two fields:
        - value is the value if it is finite
        - times_infinity is an integer in -1,0,1, and
        is set to -1 for - infty and 1 for + infty, in
        which case the value is discarded
    
    '''
    def __init__(self, value, infinity=0): #initialises an integer
        self.value = value
        self.times_infinity = infinity
    
    def __eq__(self, b):
        if(type(b) is int):
            return(self.times_infinity==0 and self.value == b)
        if(self.times_infinity or b.times_infinity):
            return(self.times_infinity == b.times_infinity)
        else:
            return(self.value == b.value)
    
    def __add__(self, b):
        if(type(b) is int):
            if(self.times_infinity):
                return(possibly_infinite_integer(0,self.times_infinity))
            return(possibly_infinite_integer(self.value + b))
        infval = truncate_to_one(b.times_infinity + self.times_infinity)
        if(infval):
            return(possibly_infinite_integer(0, infval))
        return(possibly_infinite_integer(self.value + b.value))
    
    def __sub__(self, b):
        if(type(b) is int):
            if(self.times_infinity):
                return(possibly_infinite_integer(0, self.times_infinity))
            return(possibly_infinite_integer(self.value - b))
        if(self.times_infinity):
            infval = self.times_infinity
        else:
            infval = - b.times_infinity
        if(infval):
            return(possibly_infinite_integer(0, infval))
        return(possibly_infinite_integer(self.value - b.value))
    
    def __mul__(self, b):
        if(type(b) is int):
            if(self.times_infinity):
                return(possibly_infinite_integer(0, truncate_to_one(b*self.times_infinity))) #infinity absorbs 0 (should not be reached either way)
            return(possibly_infinite_integer(self.value * b, 0))
        infval = truncate_to_one(self.value * b.times_infinity)
        if(infval):
            return(possibly_infinite_integer(0,infval))
        return(possibly_infinite_integer(self.value * b.value))
    
    
    def __lt__(self, b):
        if(type(b) is int):
            return(self.times_infinity == -1 or self.value < b)
        return(self.times_infinity < b.times_infinity or (self.times_infinity == 0 and b.times_infinity == 0 and self.value < b.value))
    
    def __gt__(self, b):
        if(type(b) is int):
            return(self.times_infinity == 1 or self.value > b)
        return(self.times_infinity > b.times_infinity or (self.times_infinity == 0 and b.times_infinity == 0 and self.value > b.value))
    
    def __le__(self, b):
        if(type(b) is int):
            return(self.times_infinity == -1 or (self.times_infinity == 0 and self.value <= b))
        return(self.times_infinity == -1 or b.times_infinity == 1 or (self.times_infinity == 0 and b.times_infinity == 0 and self.value <= b.value))
    
    def __ge__(self, b):
        if(type(b) is int):
            return(self.times_infinity == 1 or (self.times_infinity == 0 and self.value >= b))
        return(self.times_infinity == 1 or b.times_infinity == -1 or (self.times_infinity == 0 and b.times_infinity == 0 and self.value >= b.value))
    
class partition_plus_node_data:
    '''
    describes a partition of [0,1, ..., number_of_elements -1] together
    with a different value for each subset
    - number of elements is the total number of elements
    - nparts is the number of subsets
    - values is a list of distinct values of size nparts
    - index is a list of size number_of_elements -1
    which gives index of each elements
    '''
    
    #we initialize the partition with one subset
    def __init__(self, number_of_elements, value):
        self.number_of_elements = number_of_elements
        self.nparts = 1
        self.values = [value]
        self.index = [0 for i in range(number_of_elements)]

    def is_a_value(self, value):
        return(value in self.values)
    
    def is_a_singleton(self, i):
        return(all([self.index[j] != self.index[i] for j in range(self.number_of_elements) if j != i]))

    #moves i to part with given value.
    #returns true if it has emptied i's initial subset
    def move(self, i, value):
        rep = self.is_a_singleton(i)
        
        if(rep): #reindexing
            for j in range(self.number_of_elements):
                if self.index[j] > self.index[i]:
                    self.index[j] -= 1
            self.values.pop(self.index[i])
            self.nparts -= 1
            
        #if value exists, add i there
        if(self.is_a_value(value)):
            self.index[i] = self.values.index(value)
        
        #otherwise, create new (singleton) part
        else:
            self.values.append(value)
            self.index[i] = self.nparts
            self.nparts += 1
        
        return(rep)
    
    def value_of(self, i):
        return(self.values[self.index[i]])
    
    
#returns true iff list1 is a prefix of list2
#assuming list1 is shorter than list2 
def is_prefix(list1, list2):
    ind=0
    while(ind < len(list1)):
        if(list1[ind] != list2[ind]):
            return(False)
        ind+=1
    return(True)

#returns the smallest index larger than start which is in
#given list of indices and has value
#false in the given list of booleans, and len(list) if
#there is no such index
def smallest_false_index_from_list_larger_than(start, list_of_booleans, list_of_indices):
    j=start
    while(j < len(list_of_booleans) and (list_of_booleans[j] or j not in list_of_indices)):
        j+=1
    return(j)

#compares two positions in alternating lexicographic order
def is_smaller_alt_lex(map1, map2, height):
    h=0
    while(h<height):
        if(map1[h] == map2[h]):
            h+=1
        else:
            return(((map1[h] > map2[h]) + h) % 2)
    return(True)

#compues first component of minimal elt
#on second component. If player is 1, then
#computes max instead.
#if list is empty, returns None
def argmin(li, player):
    if(len(li)==0):
        return(None)
    ind_min=0
    mi=li[0][1]
    for i in range(1,len(li)):
        if(player):
            if(li[i][1] > mi):
                mi = li[i][1]
                ind_min = i
        else:
            if(li[i][1] < mi):
                mi = li[i][1]
                ind_min = i
    return(li[ind_min][0])
        