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

class sparse_tuple:
    '''
    defines alternating-lexicographically ordered sparse tuples
    value is a list of pairs (p,k) where p nonnegative and k nonzero.
    infty is 0 for finite, or +-1 for +- infty
    TODO: change to better data struct for actual log insertion
    '''
    def __init__(self, infty=0, value=[]):
        self.value = value
        self.infty = infty
    
    def set_to_infty(self, infty):
        self.infty=infty
    
    def __eq__(self, other):
        if(self.infty or other.infty):
            return(self.infty == other.infty)
        else:
            return(self.value == other.value)

    
    #performs addition in complexity O(l1 + l2)
    def __add__(self, other):
        if(self.infty):
            return(sparse_tuple(infty=self.infty))
        if(other.infty):
            return(sparse_tuple(infty=other.infty))
        inds = 0
        indo = 0
        value=[]
        while(inds < len(self.value) and indo < len(other.value)):
            (ps,ks)=self.value[inds]
            (po,ko)=other.value[indo]
            if(ps == po):
                if(ks + ko != 0):
                    value.append((ps, ks + ko))
                inds += 1
                indo += 1
            elif(ps > po):
                value.append((ps, ks))
                inds += 1
            else:
                value.append((po, ko))
                indo += 1
        if(inds == len(self.value)):
            value += other.value[indo:]
        else:
            value += self.value[inds:]
        return(sparse_tuple(value = value))
    
    
    #performs substraction in O(l1 + l2)
    def __sub__(self, other):
        if(self.infty):
            return(sparse_tuple(infty=self.infty))
        if(other.infty):
            return(sparse_tuple(infty=-other.infty))
        inds = 0
        indo = 0
        value=[]
        while(inds < len(self.value) and indo < len(other.value)):
            (ps,ks)=self.value[inds]
            (po,ko)=other.value[indo]
            if(ps == po):
                if(ks - ko != 0):
                    value.append((ps, ks - ko))
                inds += 1
                indo += 1
            elif(ps > po):
                value.append((ps, ks))
                inds += 1
            else:
                value.append((po, -ko))
                indo += 1
        if(inds == len(self.value)):
            value += [(p,-k) for (p,k) in other.value[indo:]]
        else:
            value += self.value[inds:]
        return(sparse_tuple(value = value))
        
    
    #compares in O(l1 + l2)
    def __lt__(self, other):
        if(type(other) is int): #comparison with integer 0
            return(self.__lt__(sparse_tuple()))
                
        if(self.infty or other.infty):
            return(self.infty <= other.infty) #by convention, infty < infty (check)
        
        ind=0
        while(ind < len(self.value) and ind < len(other.value)):
            (ps,ks)=self.value[ind]
            (po,ko)=other.value[ind]
            if(ps==po and ks==ko):
                ind+=1
            else:
                if(ps==po):
                    return(((ks <= ko) + ps) % 2) #invert order for odd priorities
                elif(ps > po):
                    return(((ks <= 0) + ps) % 2)
                else:
                    return(((ko >= 0) + po) % 2)
        if(len(self.value) == len(other.value)): #case of equality
            return(False)
        elif(len(self.value) < len(other.value)):
            (po,ko)=other.value[ind]
            return(((ko >= 0) + po) % 2)
        else:
            (ps,ks)=self.value[ind]
            return(((ks <= 0) + ps) % 2)


    #compares in O(l1 + l2)
    def __le__(self, other):
        if(type(other) is int): #comparison with integer 0
            return(self.__le__(sparse_tuple()))
        
        if(self.infty or other.infty):
            return(self.infty <= other.infty) #by convention, infty < infty (check)
        
        ind=0
        while(ind < len(self.value) and ind < len(other.value)):
            (ps,ks)=self.value[ind]
            (po,ko)=other.value[ind]
            if(ps==po and ks==ko):
                ind+=1
            else:
                if(ps==po):
                    return(((ks <= ko) + ps) % 2) #invert order for odd priorities
                elif(ps > po):
                    return(((ks <= 0) + ps) % 2)
                else:
                    return(((ko >= 0) + po) % 2)
                
        if(len(self.value) == len(other.value)): #case of equality
            return(True)
        elif(len(self.value) < len(other.value)):
            (po,ko)=other.value[ind]
            return(((ko >= 0) + po) % 2)
        else:
            (ps,ks)=self.value[ind]
            return(((ks <= 0) + ps) % 2)
    
    def __gt__(self, other):
        if(type(other) is int): #comparison with integer 0
            zero = sparse_tuple()
            return(zero.__lt__(self))
        
        return(other.__lt__(self))
    
    def __ge__(self, other):
        if(type(other) is int): #comparison with integer 0
            zero = sparse_tuple()
            return(zero.__le__(self))
        
        return(other.__le__(self))


    #performs addition in place in O(log(l))
    def add_priority_in_place(self, p):
        if(self.infty):
            return()
        lo=0
        hi=len(self.value)
        while(hi > lo):
            mid = (hi + lo)//2
            (ps,ks) = self.value[mid]
            if(ps == p):
                if(ks == -1):
                    self.value.pop(mid)
                else:
                    self.value[mid] = (ps, ks +1)
                return()
            elif(ps > p):
                lo = mid + 1
            else:
                hi = mid
        self.value.insert(hi, (p, 1)) #this is not real log(n), could optimize with better data struct
        
                
    
                    
class possibly_infinite_integer:
    '''
    defines possibly infinite integers by two fields:
        - value is the value if it is finite
        - infty is an integer in -1,0,1, and
        is set to -1 for - infty and 1 for + infty, in
        which case the value is discarded
    
    '''
    def __init__(self, value, infty=0): #initialises an integer
        self.value = value
        self.infty = infty
    
    def set_to_infty(self, infty):
        self.infty = infty
    
    def __eq__(self, b):
        if(type(b) is int):
            return(self.infty==0 and self.value == b)
        if(self.infty or b.infty):
            return(self.infty == b.infty)
        else:
            return(self.value == b.value)
    
    def __add__(self, b):
        if(type(b) is int):
            if(self.infty):
                return(possibly_infinite_integer(0,self.infty))
            return(possibly_infinite_integer(self.value + b))
        infval = truncate_to_one(b.infty + self.infty)
        if(infval):
            return(possibly_infinite_integer(0, infval))
        return(possibly_infinite_integer(self.value + b.value))
    
    def __sub__(self, b):
        if(type(b) is int):
            if(self.infty):
                return(possibly_infinite_integer(0, self.infty))
            return(possibly_infinite_integer(self.value - b))
        if(self.infty):
            infval = self.infty
        else:
            infval = - b.infty
        if(infval):
            return(possibly_infinite_integer(0, infval))
        return(possibly_infinite_integer(self.value - b.value))
    
    def __mul__(self, b):
        if(type(b) is int):
            if(self.infty):
                return(possibly_infinite_integer(0, truncate_to_one(b*self.infty))) #infinity absorbs 0 (should not be reached either way)
            return(possibly_infinite_integer(self.value * b, 0))
        infval = truncate_to_one(self.value * b.infty)
        if(infval):
            return(possibly_infinite_integer(0,infval))
        return(possibly_infinite_integer(self.value * b.value))
    
    
    def __lt__(self, b):
        if(type(b) is int):
            return(self.infty == -1 or self.value < b)
        return(self.infty < b.infty or (self.infty == 0 and b.infty == 0 and self.value < b.value))
    
    def __gt__(self, b):
        if(type(b) is int):
            return(self.infty == 1 or self.value > b)
        return(self.infty > b.infty or (self.infty == 0 and b.infty == 0 and self.value > b.value))
    
    def __le__(self, b):
        if(type(b) is int):
            return(self.infty == -1 or (self.infty == 0 and self.value <= b))
        return(self.infty == -1 or b.infty == 1 or (self.infty == 0 and b.infty == 0 and self.value <= b.value))
    
    def __ge__(self, b):
        if(type(b) is int):
            return(self.infty == 1 or (self.infty == 0 and self.value >= b))
        return(self.infty == 1 or b.infty == -1 or (self.infty == 0 and b.infty == 0 and self.value >= b.value))
    
    def min_of_list(l, player):
        '''
        performs min of list if player =0, max otherwise
        '''
        if(l):
            if(player == 0):
                return(min(l)) #could try to optimize (not sure if python intelligent when min of list of integers)
            else:
                return(max(l))
        else:
            return(possibly_infinite_integer(0, infty=(-1)**player))
        
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
        