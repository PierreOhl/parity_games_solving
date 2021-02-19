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
    
    def is_zero(self):
        return(not(self.infty) and not(self.value))
    
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
    
    
    
    def min_of_tuple_list_with_additionnal_value(list, player):
        '''
        given a list of tuples (st,p) where st is a sparse tuple,
        computes the min value of st + p
        and returns corresponding index
        '''
        
        trivial_version = False
        if(trivial_version):
            list_with_added = [st + sparse_tuple(value=[(p,1)]) for (st,p) in list]
            if(player==0):
                return(min(list_with_added))
            else:
                return(max(list_with_added))
        
        
        if(any([st.infty == (-1)**(player +1) for (st,p) in list])):
            return(sparse_tuple(infty=(-1)**(player +1)))
        if(all([st.infty == (-1)**(player) for (st, p) in list])):
            return(sparse_tuple(infty=(-1)**(player)))
        
        
        alive=[(l,0,False,None) for l,(st,p) in enumerate(list) if st.infty != (-1)**player]
        rep=[]
        rep_in_list=False
        #assume for now player = 0 --> compute a min
        while(alive):
            for (i,(l,ind,used,_)) in enumerate(alive):
                #compute next contribution (there is one)
                (st,p) = list[l]
                if(ind == len(st.value)):
                    alive[i] = (l, ind, True, (p,1))
                else:
                    (ps,ks) = st.value[ind]
                    if(used or ps > p):
                        alive[i] = (l, ind+1, used, (ps,ks))                        
                    elif(p == ps):
                        alive[i] = (l, ind+1, True, (ps,ks+1))
                    else:
                        alive[i] = (l, ind, True, (p,1))
                        
            #if rep is a candidate min, kill those that have positive contribution
            if(rep_in_list):
                i = 0
                new_alive = []
                while(i < len(alive)):
                    if(((alive[i][3][0] < 0) + alive[i][3][0] + player) % 2):
                        new_alive.append(alive[i])
                    i += 1
                rep_in_list = False
                alive = new_alive
            if(not(alive)):
                break
            
            #kill non minimal
            new_alive = []
            mi = alive[0][3] #min if player = 0
            (l,ind,used,cand) = alive[0]
            (st,p) = list[l]
            if(ind < len(st.value) or not(used)):
                new_alive.append(alive[0])
            else:
                rep_in_list = True
            i=1
            while(i<len(alive)):
                (l,ind,used,cand) = alive[i]
                add=False
                if((player == 0 and sparse_tuple.pair_smaller(cand, mi)) or
                   (player == 1 and sparse_tuple.pair_smaller(mi, cand))):
                    mi = cand
                    new_alive = []
                    rep_in_list = False
                    add=True
                elif(cand == mi):
                    add=True
                if(add):
                    (st,p) = list[l]
                    if(ind < len(st.value) or not(used)):
                        new_alive.append(alive[i])
                    else:
                        rep_in_list = True
                i+=1
            rep.append(mi)
            alive = new_alive
        
        return(sparse_tuple(value=rep))
            
                

        
    
    def compute_edge_validity(pos, neg, p):
        '''
        given two sparse tuples pos and neg, a priority p, and a player
        returns True iff pos - neg + p >= 0 if player = 0, and <= 0 o/w
        assumes neg to be finite TOFIX
        '''
        ver1 = False
        if ver1:
            res = pos - neg + sparse_tuple(value=[(p,1)])
            if(res.is_zero()):
                return((1,1))
            elif(res > 0):
                return((1,0))
            else:
                return((0,1))
            
            
        if(pos.infty):
            if(pos.infty == 1):
                return((1,0))
            else:
                return((0,1))
        
        
        indpos=0
        indneg=0
        used=False
        contin = True
        
        while(contin):
            if(indpos < len(pos.value)):
                (pp,pk) = pos.value[indpos]
            else:
                (pp,pk) = (0,0)
            if(indneg < len(neg.value)):
                (np,nk) = neg.value[indneg]
            else:
                (np,nk) = (0,0)
            
            if(np == 0 and nk == 0 and used):
                contin = False
        
            if(not(used)):
                ma = max(pp, np, p)
            else:
                ma = max(pp, np)
            s=0
            
            if(pp == ma):
                s += pk
                indpos += 1
            if(np == ma):
                s -= nk
                indneg += 1
            if(not(used) and p == ma):
                s += 1
                used = True
            if(s != 0):
                if(((s >= 0) + ma) %2):
                    return((1,0))
                else:
                    return((0,1))
        return((1,1))
    
    def pair_smaller(p1,p2):
        if(p1[0] == p2[0]):
            if(p1[1] == p2[1]):
                return(False)
            return(((p1[1] < p2[1]) + p1[0]) % 2)
        elif(p1[0] > p2[0]):
            return(((p1[1] < 0) + p1[0]) % 2)
        else:
            return(((p2[1] > 0) + p2[0]) % 2)
        
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
                return(min(l))
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
        

def color_of_validity(vtype,ev):
    if(ev=="edge"):
        if(vtype==(1,0)):
            return("red")
        elif(vtype==(0,1)):
            return("blue")
        else:
            return("black")
    else:
        if(vtype==[1,0]):
            return("lightcoral")
        elif(vtype==[0,1]):
            return("lightblue")
        else:
            return("gray89")

def base26(n):
    rep=[]
    p=n
    while(p > 0):
        rep.append(p % 26)
        p = p // 26
    return(rep)

def number_to_letters(n,l):
    b26 = base26(n)
    rep="A" * (len(b26) - l)
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i in range(len(b26)):
        rep+=alphabet[b26[i]]
    return(rep)