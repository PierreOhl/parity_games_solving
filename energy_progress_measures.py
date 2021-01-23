import util
import time

class progress_measure:
    
    def __init__(self, game):
        self.game = game
        self.map = [util.possibly_infinite_integer(0) for i in range(game.size)]
        self.dest = [util.possibly_infinite_integer(0) for i in range(game.size)]
        for i in range(game.size):
            self.update_dest(i)

    def update_dest(self,i):
        if(self.map[i].times_infinity):
            self.dest[i] = util.possibly_infinite_integer(0,self.map[i].times_infinity)
            return()
        
        if(self.game.player[i]): #Adam vertex
            if(len(self.game.succ[i]) > 0):
                self.dest[i] = min([self.map[succ] + weight for (succ, weight) in self.game.succ[i]])
            else:
                self.dest[i] = util.possibly_infinite_integer(0, 1) # + infinity
        else: #Eve vertex
            if(len(self.game.succ[i]) > 0):
                self.dest[i] = max([self.map[succ] + weight for (succ, weight) in self.game.succ[i]])
            else:
                self.dest[i] = util.possibly_infinite_integer(0, 1) # - infinity
        
        
    def update_predecessors(self, i):
        for (pred, _,_) in self.game.pred[i]:
            self.update_dest(pred)
        
        
    def simple_lift(self, i):
        self.map[i] = self.dest[i]
        self.update_predecessors(i)
            
    
    def list_invalid(self, player):
        return([i for i in range(self.game.size) if self.dest[i] * (-1)**player < self.map[i] * (-1)**player or self.map[i].times_infinity == (-1)**(player +1)])
    
    
    def player_vert_to_be_fixed(self, fixed, player):  #auxiliary function for snare_lift
        return(
            [
                i for i in range(self.game.size) if 
                    i not in fixed 
                    and self.game.player[i] == player 
                    and all([succ in fixed for (succ, weight) in self.game.succ[i] if (self.map[succ] + weight) * (-1)**player >= self.map[i] * (-1)**player])
                    #all valid outgoing edges go to fixed   
            ]
        )
    
    def find_player_vert_to_be_fixed(self, fixed, player):
        i=0
        while(i<self.game.size):
            if i not in fixed and self.game.player[i] == player:
                if all([succ in fixed for (succ, weight) in self.game.succ[i] if (self.map[succ] + weight) * (-1)**player >= self.map[i] * (-1)**player]):
                    return(i)
            i+=1
        
    def threshold_lift(self, i):
        self.simple_lift(i)
        if(self.map[i] >= self.game.size * self.game.max_absolute_value + 1):
            self.map[i] = util.possibly_infinite_integer(0,1)
            self.update_predecessors(i)
        elif(self.map[i] <= - self.game.size * self.game.max_absolute_value - 1):
            self.map[i] = util.possibly_infinite_integer(0,-1)
            self.update_predecessors(i)
    
    def snare_lift(self, player):
        fixed = self.list_invalid(player)
        spent = 0
        equiv_updates = 0
        while(len(fixed) < self.game.size):
            
            #first deal with player vertices   (could be optimized)
            start=time.time()
            to_fix = self.find_player_vert_to_be_fixed(fixed, player)
            while to_fix != None:
                if(self.map[to_fix] != self.dest[to_fix]):
                    equiv_updates += 1
                self.simple_lift(to_fix)
                fixed.append(to_fix)
                to_fix = self.find_player_vert_to_be_fixed(fixed, player)
            
            #now deal with opponent vertices
            #compute delta and vertices to be fixed (argmin)
            delta = util.possibly_infinite_integer(0,(-1) ** player) #+- infinity
            to_be_fixed = []
            for i in range(self.game.size):
                if self.game.player[i] != player and i not in fixed:
                    l = [self.map[succ] - self.map[i] + weight for (succ, weight) in self.game.succ[i] if succ in fixed]
                    if l:
                        if player:
                            m=max(l)
                        else:
                            m=min(l)
                        if(m == delta):
                            to_be_fixed.append(i)
                        elif(m * (-1)**player < delta * (-1) ** player):
                            delta = m
                            to_be_fixed = [i]
            spent+=time.time() - start
            
            if(delta != 0):
                equiv_updates += len(to_be_fixed)
            
            for i in range(self.game.size):
                if(i not in fixed):
                    self.map[i] += delta
            
            for i in range(self.game.size):
                self.update_dest(i)
            
            if(delta.times_infinity):
                break
            
            fixed += to_be_fixed
        return(spent, equiv_updates)
            
    def terminate(self):
        return(all([self.dest[i] <= self.map[i] for i in range(self.game.size)]) or 
               all([self.dest[i] >= self.map[i] for i in range(self.game.size)]))