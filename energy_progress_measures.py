from operator import truediv
import util
import time
from copy import deepcopy
import random
from networkx.drawing.nx_agraph import to_agraph
import networkx as nx
import os

class progress_measure:
    
    def __init__(self, game, map=0, infos=None, alg="snare"):
        self.game = game
        
        if(map==0):
            if(game.typ == "energy" and alg == "snare"):
                self.map = [util.possibly_infinite_integer(0) for i in range(game.size)]
            elif(game.typ == "energy"):
                self.map = [0] * game.size
            else:
                self.map = [util.sparse_tuple() for i in range(game.size)]
        else:
            self.map=map
        
        if(alg == "snare"):
            self.validity_of_edge = [None for e in range(game.number_edges)]  
            self.validity_of_vert = [[None, None] for i in range(game.size)]
            self.edge_needs_updating = [True for e in range(game.number_edges)]
            self.optimal_edge = [None for i in range(game.size)]
        
        if(infos):
            self.infos=infos
        
        elif(alg == "snare"):
            self.infos={"trajectory":[[] for i in range(game.size)], "chrono":0}
        else:
            self.infos={'zones':[], 'iter_top_level':0, 'iter_same_N':0, 'player':[], 'vertex layers':[0]*game.size, "opt_edge":[0]*len(self.game.edges)}
        
        if(game.typ == "energy" and alg == "snare"):
            self.dest_of_edge = [None for e in range(game.number_edges)] #map(j) + w(e) for e=(i,j), used only for typ="energy"
            for edge_ind in range(self.game.number_edges):
                self.update_dest_of_edge(edge_ind)
        
            self.globally_update_validity()

    def sub_progress_measure(self,S):
        game, incl=self.game.subgame(S)
        map=[self.map[incl[i]] for i in range(game.size)]
        return(progress_measure(game,map,self.infos, alg="recursive"),incl) #maybe put a deepcopy here for infos?
    
    #######################################################################################
    #### up to line 267 -> used for snare update algorithm (also called En+, or sup-) #####
    #######################################################################################

    def write_step_of_trajectory(self):
        for i in range(self.game.size):
            if(self.map[i].infty):
                self.infos["trajectory"][i].append(str(self.map[i].infty)[:-1] + "infty")
            else:
                self.infos["trajectory"][i].append(str(self.map[i].value))
                
    
    def update_validity_of_edge(self, edge_ind):
        if(self.edge_needs_updating[edge_ind]):
            (i,j,w) = self.game.edges[edge_ind]
            if(edge_ind == self.optimal_edge[i]):
                self.validity_of_edge[edge_ind] = (1,1)
            if(self.map[i].infty):
                if(self.map[i].infty == -1):
                    self.validity_of_edge[edge_ind] = (0, 1)
                else:
                    self.validity_of_edge[edge_ind] = (1, 0)
            else:
                if(self.game.typ == "energy"):
                    if(self.dest_of_edge[edge_ind] == self.map[i]):
                        self.validity_of_edge[edge_ind] = (1,1)
                    elif(self.dest_of_edge[edge_ind] > self.map[i]):
                        self.validity_of_edge[edge_ind] = (1,0)
                    else:
                        self.validity_of_edge[edge_ind] = (0,1)
                else:
                    self.validity_of_edge[edge_ind] = util.sparse_tuple.compute_edge_validity(self.map[j], self.map[i], w)
            self.edge_needs_updating[edge_ind] = False


    def update_validity_of_vertex(self, i):
        for pl in (0,1):
            validity_of_successors = [self.validity_of_edge[edge_ind][pl] for _,edge_ind in self.game.succ[i]]
            if(self.game.player[i] == pl):
                self.validity_of_vert[i][pl] = int(any(validity_of_successors))
            else:
                self.validity_of_vert[i][pl] = int(all(validity_of_successors))
                    

    def update_dest_of_edge(self, edge_ind):
        (_,j,w) = self.game.edges[edge_ind]
        self.dest_of_edge[edge_ind] = self.map[j] + w


    def globally_update_validity(self):
        for edge_ind in range(self.game.number_edges):
            self.update_validity_of_edge(edge_ind)
        for i in range(self.game.size):
            self.update_validity_of_vertex(i)

    
    def snare_lift(self, player):
        '''
        main function, computes update+ if player=0 and update- otherwise
        '''
        fixed = [not(self.validity_of_vert[i][player]) for i in range(self.game.size)]
        number_edges_towards_not_fixed = [len([1 for (s,edge_ind) in self.game.succ[i] if not(fixed[s]) and self.validity_of_edge[edge_ind][player]]) for i in range(self.game.size)]
        minimal_weight_towards_fixed = self.initialize_min_weights(fixed, player)
        order = self.initialize_order(minimal_weight_towards_fixed, player)
        max_to_fix = [i for i in range(self.game.size) if self.game.player[i] == player and number_edges_towards_not_fixed[i] == 0 and not(fixed[i])]

        while(order or max_to_fix):
            while(max_to_fix):
                i = max_to_fix.pop()
                self.update_map_at_vertex(i, self.compute_max_value([edge_ind for (s,edge_ind) in self.game.succ[i] if self.validity_of_edge[edge_ind][player]], player), player)
                fixed[i] = True
                self.treat_predecessors(i, order, max_to_fix, minimal_weight_towards_fixed, number_edges_towards_not_fixed, fixed, player)
            
            if(order):
                i = order.pop(0)
                self.update_map_at_vertex(i, minimal_weight_towards_fixed[i][0], player)
                fixed[i] = True
                self.treat_predecessors(i, order, max_to_fix, minimal_weight_towards_fixed, number_edges_towards_not_fixed, fixed, player)
    
        for i in range(self.game.size):
            if(not(fixed[i])):
                self.update_map_at_vertex_to_infty(i, player)
        
        self.globally_update_validity()


    def initialize_min_weights(self, fixed, player):
        '''
        (if player = 0, otherwise invert *)
        returns a list, containing for each non fixed min* vertex i that has a valid
        edge to fixed, the pair (m, m-map[i]), where m is the smallest*
        map[j] + w(e) of such an edge e=(i,j). For other i's, None.
        TODO: update optimal edge
        '''
        rep=[None for i in range(self.game.size)]
        for i in range(self.game.size):
            if(self.game.player[i] != player and not(fixed[i])):
                towards_fixed = [edge_ind for (s,edge_ind) in self.game.succ[i] if fixed[s]]
                if(towards_fixed):
                    if(self.game.typ == "energy"):
                        m = util.possibly_infinite_integer.min_of_list([self.dest_of_edge[edge_ind] for edge_ind in towards_fixed], player)
                    else:
                        m = util.sparse_tuple.min_of_tuple_list_with_additionnal_value([(self.map[self.game.edges[edge_ind][1]], self.game.edges[edge_ind][2]) for edge_ind in towards_fixed], player)
                    rep[i] = (m, m - self.map[i])
        return(rep)
    
    
    def initialize_order(self, minimal_weight_towards_fixed, player):
        '''
        (if player = 0, otherwise invert *)
        returns a list containing vertices i such that list[i] is not None,
        and sorted according to second coordinate (m - map[i]), in increasing*
        order.
        '''
        rep = [i for i in range(self.game.size) if minimal_weight_towards_fixed[i]]
        rep.sort(key = lambda i: minimal_weight_towards_fixed[i][1])
        if(player==1):
            rep.reverse()
        return(rep)
    
    
    def compute_max_value(self, edges, player):
        '''
        (if player = 0, otherwise invert *)
        returns max* value of an edge given in the list edges
        TODO: also updates optimal_edge
        '''
        if(self.game.typ == "energy"):
            rep = util.possibly_infinite_integer.min_of_list([self.dest_of_edge[edge_ind] for edge_ind in edges] ,1-player) #computes a max
        else:
            rep = util.sparse_tuple.min_of_tuple_list_with_additionnal_value([(self.map[self.game.edges[edge_ind][1]], self.game.edges[edge_ind][2]) for edge_ind in edges], 1-player)
        return(rep)
    
    
    def treat_predecessors(self, i, order, max_to_fix, minimal_weight_towards_fixed, number_edges_towards_not_fixed, fixed, player):
        '''
        (if player = 0, otherwise invert *)
        -   for max* predecessors p of i, decrement number_edges_towards_not_fixed[p],
            and add to max_to_fix if reached 0
        -   for min* predecessors p of i, update minimal_weight_towards_fixed, and
            if necessary, update order
        '''
        for (p,edge_ind) in [(p,edge_ind) for (p,edge_ind) in self.game.pred[i] if self.validity_of_edge[edge_ind][player] and not(fixed[p])]:
            if(self.game.player[p] == player): #max predecessors
                number_edges_towards_not_fixed[p] -= 1
                if(number_edges_towards_not_fixed[p] == 0):
                    max_to_fix.append(p)
            else: #min predecessors
                
                if(self.game.typ == "energy"):
                    dest_of_edge = self.dest_of_edge[edge_ind]
                else:
                    dest_of_edge = self.map[i] + util.sparse_tuple(value=[(self.game.edges[edge_ind][2],1)])
                    
                if(minimal_weight_towards_fixed[p] == None): #first edge towards fixed
                    minimal_weight_towards_fixed[p] = (dest_of_edge, dest_of_edge - self.map[p])
                    self.insert_in_order(p, order, minimal_weight_towards_fixed, player)
                    self.optimal_edge[p] = edge_ind
                else:
                    if((player == 0 and dest_of_edge < minimal_weight_towards_fixed[p][0]) or
                        (player == 1 and dest_of_edge > minimal_weight_towards_fixed[p][0])):
                        minimal_weight_towards_fixed[p] = (dest_of_edge, dest_of_edge- self.map[p])
                        order.remove(p)
                        self.insert_in_order(p, order, minimal_weight_towards_fixed, player)
                        self.optimal_edge[p] = edge_ind
    
    
    def update_map_at_vertex(self,i,dest,player):
        '''
        updates the map at vertex i to position dest
        if player = 0, then dest >= map[i]
        '''
        if(self.map[i] != dest):
            self.map[i] = dest
            
            for _,edge_ind in self.game.pred[i]:
                if self.validity_of_edge[edge_ind] != (1-player,player) :
                    self.edge_needs_updating[edge_ind] = True
            
            for _,edge_ind in self.game.succ[i]:
                if self.validity_of_edge[edge_ind] != (player, 1-player):
                   self.edge_needs_updating[edge_ind] = True
            
            
            if(self.game.typ == "energy"):
                for p,edge_ind in self.game.pred[i]:
                    self.dest_of_edge[edge_ind] = dest + self.game.edges[edge_ind][2]
        
    
    def update_map_at_vertex_to_infty(self,i, player):
        '''
        updates the map at vertex i to position (-1)**player * infty
        '''
        if(self.game.typ == "energy"):
            dest = util.possibly_infinite_integer(0, infty=(-1)**player)
        else:
            dest = util.sparse_tuple(infty=(-1)**player)
        self.update_map_at_vertex(i, dest, player)
        
    
    def insert_in_order(self, i, order, minimal_weight_towards_fixed, player):
        '''
        (if player = 0, otherwise invert *)
        inserts i in order at the right position such that order
        remains increasing* wrt second coord in mwtf
        '''
        lo=0
        hi=len(order)
        while lo < hi:
            mid = (lo+hi) // 2
            if ((player == 0 and minimal_weight_towards_fixed[i][1] < minimal_weight_towards_fixed[order[mid]][1]) or
                (player == 1 and minimal_weight_towards_fixed[i][1] > minimal_weight_towards_fixed[order[mid]][1])):
                hi = mid
            else:
                lo = mid+1
        order.insert(lo, i)
    
    ##################
    #### now GKK #####
    ##################
    
    def update_GKK(self):
        '''
        implements the algorithm of Gurvich, Karzanov and Khachyian
        supports only energy games (for now)
        '''
        #first, compute attractor to invalids
        fixed = [not(self.validity_of_vert[i][0]) for i in range(self.game.size)]
        number_zero_edges_towards_not_fixed = [len([1 for (s,edge_ind) in self.game.succ[i] if not(fixed[s]) and self.validity_of_edge[edge_ind]==(1,1)]) for i in range(self.game.size)]
        to_add = [i for i in range(self.game.size) if self.game.player[i] and not(fixed[i]) and any([fixed[s] for s,edge_ind in self.game.succ[i] if self.validity_of_edge[edge_ind]==(1,1)])] + [i for i in range(self.game.size) if not(self.game.player[i]) and self.validity_of_vert[i]==(1,1) and number_zero_edges_towards_not_fixed[i] == 0]
        while(to_add):
            i=to_add.pop()
            fixed[i]=True
            for pred,edge_ind in self.game.pred[i]:
                if(self.validity_of_edge[edge_ind]==(1,1)):
                    if(self.game.player[pred]):
                        to_add.append[pred]
                    else:
                        number_zero_edges_towards_not_fixed[pred] -=1
                        if(number_zero_edges_towards_not_fixed[pred]==0):
                            to_add.append[pred]
        #construct relevant sets of weights
        deltas=[[],[],[],[]]
        #non-extremal
        for edge_ind in range(self.game.number_edges):
            i,j,_ = self.game.edges[edge_ind]
            if(self.game.player[i] and not(fixed[i]) and fixed[j]):
                deltas[0].append(self.modified_weight[edge_ind])
            elif(not(self.game.player[i]) and fixed[i] and not(fixed[j])):
                deltas[1].append(-self.modified_weight[edge_ind])
        #extremal
        for i in range(self.game.size):
            if(self.game.player[i] and fixed[i] and all([not(fixed[s]) for s,edge_ind in self.game.succ[i] if self.validity_of_edge[edge_ind][1]])):
                deltas[2].append(max([-self.modified_weight[edge_ind] for s,edge_ind in self.game.succ[i]]))
            elif(not(self.game.player[i]) and not(fixed[i]) and all([fixed[s] for s,edge_ind in self.game.succ[i] if self.validity_of_edge[edge_ind][0]])):
                deltas[3].append(max([self.modified_weight[edge_ind] for s,edge_ind in self.game.succ[i]]))
        #termination case
        if(all([not(deltas[k]) for k in range(4)])):
            for i in range(self.game.size):
                if(fixed[i]):
                    self.map[i].set_to_infty(-1)
                else:
                    self.map[i].set_to_infty(1)
                return("stop")
        #compute min
        delta=[]
        for k in range(4):
            if(deltas[k]):
                delta.append(min(deltas[k]))
        delta=min(delta)
        #update
        for i in range(self.game.size):
            if(not(fixed[i])):
                self.map[i] += delta
        
        for edge_ind in range(self.game.number_edges):
            i,j,w = self.game.edges[edge_ind]
            if(fixed[i] and not(fixed[j])):
                self.modified_weight[edge_ind] += delta
                self.validity_of_edge[edge_ind]=(self.modified_weight[edge_ind] >= 0, self.modified_weight[edge_ind] <= 0)
            elif(fixed[j] and not fixed[i]):
                self.modified_weight[edge_ind] -= delta
                self.validity_of_edge[edge_ind]=(self.modified_weight[edge_ind] >= 0, self.modified_weight[edge_ind] <= 0)
        for i in range(self.game.size):
            self.update_validity_of_vertex(i)
        
        return("continue")


    ###################################################
    #### some functions for displaying graphs etc #####
    ###################################################


    def draw(self, filename, layers=False, display_title=False, map=None):
        (N,P,ZN,ZP, resolved)=self.compute_zones()

        color=[0]*self.game.size
        for i in range(self.game.size):
            if(N[i]):
                color[i]="blue"
            elif(ZN[i]):
                color[i]="lightblue"
            elif(P[i]):
                color[i]="red"
            else:
                color[i]="lightcoral"

        edges_with_attributes = [(i,j,self.attribute_of_edge(edge_ind)) for edge_ind, (i,j,_) in enumerate(self.game.edges)]
        nodes_with_attributes = [(i,self.attribute_of_vertex(i, color[i], xlabel=str(map[i]) if map else None)) for i in range(self.game.size)]
       
        G = nx.MultiDiGraph()

        G.add_nodes_from(nodes_with_attributes)
        G.add_edges_from(edges_with_attributes)

        G.graph['edge'] = {'arrowsize': '0.6', 'splines': 'curved'}
        G.graph['graph'] = {'scale': '1'}

        
        A = to_agraph(G)

    
        if(layers):#does not really work...
            lay = self.infos["vertex layers"]
            # define your global node order

            order = sorted(range(len(lay)), key=lambda i: lay[i])
            
            
            # enforce that all nodes are on the same rank
            for node in order:
                A.get_node(node).attr['rank'] = 'same'

            # add invisible edges to force horizontal order
            for u, v in zip(order[:-1], order[1:]):
                A.add_edge(u, v, style="invis", weight="1000")

            # tweak graph attributes if you want left-to-right
        A.graph_attr.update(rankdir="LR")  # top-to-bottom layering
            # or rankdir="LR" if you want the order vertically instead

        if(display_title):
            A.graph_attr.update(
                label=display_title,
                labelloc="t",   # "t" = top, "b" = bottom
                fontsize="20",   # adjust size
                fontcolor="blue" if display_title[0]=='s' else 'red' if display_title[0]=='i' else "black"
            )

        # creating folder if necessary
        if("/" in filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        A.layout('dot')                                                                 
        A.draw(filename + ".png")


    

    def attribute_of_edge(self, edge_ind):
        rep={}
        (i,j,w) = self.game.edges[edge_ind]
        modified_weight = self.map[j] - self.map[i] + w
        if(str(type(self.map[i])) != "<class 'int'>"):
            rep["label"] = modified_weight.to_label()
            if(modified_weight.infty):
                rep["color"] = {1:"red", -1:"blue"}[modified_weight.infty]
            else:
                if(modified_weight.is_zero()):
                    rep["color"] = "black"
                elif(modified_weight.is_positive()):
                    rep["color"] = "red"
                else:
                    rep["color"] = "blue"
        else:
            rep["label"] = str(modified_weight)
            if(modified_weight==0):
                    rep["color"] = "black"
            elif(modified_weight>0):
                rep["color"] = "red"
            else:
                rep["color"] = "blue"
        
        if("opt_edge" in self.infos.keys() and self.infos['opt_edge'][edge_ind]):
            rep["penwidth"]=2.5
        rep["fontcolor"] = rep["color"]
        return(rep)
        
        
    def attribute_of_vertex(self, i, color, xlabel=None):
        rep={}
        rep["shape"] = ["box", "circle"][self.game.player[i]]
        rep["regular"] = 1
        rep["label"] = util.number_to_letters(i+1,len(util.base26(self.game.size)))
        rep["color"] = color
        rep["style"] = "filled"
        if(xlabel):
            rep["xlabel"]=xlabel
        return(rep)
        
        
    def threshold_lift(self, i, growing): #DEPRECATED, NEEDS UPDATING FOR BCDGR
        if(self.dest_of_vert[i] > self.game.size * self.game.max_absolute_value):
            self.dest_of_vert[i] = util.possibly_infinite_integer(0,1) #set dest to +infinity
        elif(self.dest_of_vert[i] < - self.game.size * self.game.max_absolute_value):
            self.dest_of_vert[i] = util.possibly_infinite_integer(0,-1) #set dest to -infinity
        self.update_map(i, self.dest_of_vert[i], growing)
    

    def type_config(self):
        rep=[0]*self.game.size
        for i in range(self.game.size):
            succweights=[(self.map[j] - self.map[i] + self.game.edges[edge_ind][2]) for (j,edge_ind) in self.game.succ[i]]
            if(all([w<0 for w in succweights])):
                rep[i]=-1
            if(any([w>0 for w in succweights])):
                rep[i]=1
        return(rep)


    #######################################
    #### code for recursive algorithm #####
    #######################################
    
    def resolve_game(self, choice_mode='smallest', transcript_mode='top_level', pivot_on_N=False, draw_top_level_filename=False, forgetfull = True):
        #main procedure
        #updates self.map in place until game is resolved
        #returns winning regions and potential
        #choice_mode tells us how we determine if we pivot over ZN or ZP
        #transcript_mode just tells us what information to store for later study
        #if pivot_on_N is true, we pivot on N always, recursively

        #first, compute zones
        (N,P,ZN,ZP, resolved)=self.compute_zones()

        #main top-level loop: iterates either supZN or infZP
        #until either a dominion is found (in which case we will recurse)
        #or the game is resolved
        while(not(resolved)):


            if(draw_top_level_filename):#store a copy for drawing
                to_be_drawn = deepcopy(self)
            

            player, rec_choice_mode, attr_choice_mode = self.player_and_choice_modes(ZN,ZP,choice_mode)
            #deciding player and choice_mods for future calls according to prescribed options
            #below, for explanations, we always assume Player = 1 (= Min)

            #deciding starting value for F
            F = ZN.copy() if player else ZP.copy()
            if(pivot_on_N):
                F = N.copy()
                player = 1

            ########## main computation happens here ###########
            Hplus,phiH = self.compute_sup_or_inf_to_F_or_return_dominion(player, F, rec_choice_mode, pivot_on_N=pivot_on_N, forgetfull=forgetfull)
            ####################################################
            if(draw_top_level_filename):
                fn = draw_top_level_filename + str(self.infos["iter_top_level"])
                title = "supZN" if player else "supN" if pivot_on_N else "infZP"
                to_be_drawn.infos["opt_edge"]=self.infos["opt_edge"].copy()
                to_be_drawn.draw(fn, display_title=title)

            if Hplus: #found a (resolved) Max dominion 

                #update map over H+ to correspond to phiH
                for i in range(self.game.size):
                    if Hplus[i]:
                        self.map[i]=phiH[i]
                
                #attract to H+ while updating map in place
                A=self.attract(Hplus,1-player)

                #complement of A
                Acompl=[1-A[i] for i in range(self.game.size)]
                
                if(sum(Acompl)):#if the complement is non-empty

                    #then we recurse of the complement
                    nnpg,incl = self.sub_progress_measure(Acompl)
                    (nZNrec, nZPrec, nphirec)= nnpg.resolve_game(attr_choice_mode, transcript_mode=None, pivot_on_N=pivot_on_N, forgetfull=forgetfull)

                    #convert vertex indices
                    _,_,nphi = self.reindex(nZNrec,nZPrec,nphirec,incl,nnpg.game.size)

                    #merge the two potentials (self.map over A and nphi over Acompl)
                    #with the right delta
                    #updates self.map in place
                    self.merge_resolving_potentials(player, nphi, A)

            #if no dominion, then we have computed supZN everywhere, so we continue the top-loop
            #we just need to update the zones
            oldN = N.copy()
            (N,P,ZN,ZP, resolved)=self.compute_zones()

            if(transcript_mode == 'top_level'): #storing some information
                self.infos['zones'].append((N.copy(),P.copy(),ZN.copy(),ZP.copy(),resolved))
                self.infos['iter_top_level']+=1
                self.infos['player'].append(player)
                if(oldN == N):
                    self.infos['iter_same_N']+=1
        
        if(draw_top_level_filename):
                fn = draw_top_level_filename + str(self.infos["iter_top_level"]+1)
                title = "resolved"
                self.draw(fn, display_title=title)

        #return winning regions
        return(ZN,ZP, self.map)
    


    def compute_sup_or_inf_to_F_or_return_dominion(self, player, F, rec_choice_mode, pivot_on_N=False, store_layers=False, forgetfull = True):
        #if player = 1, either return a set H+ where Max can win while avoiding F
        #or compute sup^N over the whole game (in this case, return None, None)
        #updates self.map in place
        #the recursive calls are done according to the prescribed choice_mode, and whether we pivot on N
        #if store_layers is True, then we additionally store the layers (TODO: to be fixed)
        
        if(store_layers):
            l=1 #initialising layer index
            mult=2*player -1 #1 if player is Min and -1 otherwise
            for i in range(self.game.size): #erasing layer info for vertices not in F
                if(not(F[i])):
                    self.infos["vertex layers"][i]=0

        if(not(forgetfull)):#in this case we should already initialise the subgame
            npg = deepcopy(self)
            incl = [i for i in range(self.game.size)]

        while 1: #main loop
            #updates F and self.map in place, adding vertices whose paths
            #all go to F
            self.backtrack_all_paths(F)

            attr_layer_empty=True
            if(store_layers): #add new layer info for vertices just added to F
                for i in range(self.game.size):
                    if(F[i] and self.infos["vertex layers"]):
                        self.infos["vertex layers"][i]= mult * l
                        attr_layer_empty = attr_layer_empty and False
                        
            #if attractor is non empty, increment l
            if(not(attr_layer_empty)):
                l+=1

            #H is the complement of F
            H=[1-F[i] for i in range(self.game.size)]

            #recursive call on H, returns winning regions and resolving potential
            if(forgetfull):#in this case we redefine the new game from the original one
                npg, incl = self.sub_progress_measure(H)
            else:#in this case we keep the same potential that was previously computed
                #we need to be extra careful here with updating inclusions
                nH = [H[incl[j]] for j in range(npg.game.size)]
                npg, nincl = npg.sub_progress_measure(nH)
                incl = [incl[nincl[k]] for k in range(npg.game.size)]

            (Hminusrec, Hplusrec, phiHrec) = npg.resolve_game(rec_choice_mode, transcript_mode=None,pivot_on_N=pivot_on_N, forgetfull=forgetfull)
            
            #convert to correct vertex indexing
            Hm,Hp,phiH = self.reindex(Hminusrec, Hplusrec,phiHrec, incl, npg.game.size)

            #possibly reverse according to player    
            Hplus = Hp if player else Hm


            if sum(Hplus): #there is an opponent dominion. Does someone want to escape?
                #first compute which edges escape from H+ cap Vmin to F
                edges_from_Hplus_cap_Vmin_to_F = [(i,j,w,e) for e,(i,j,w) in enumerate(self.game.edges) if Hplus[i] and self.game.player[i]==player and F[j]]
                
                if(edges_from_Hplus_cap_Vmin_to_F): # if there is an edge from H+ cap Vmin to F

                    #look for minimising edge (updates map in place)
                    i0,_,_ = self.optimal_escaping_edge(edges_from_Hplus_cap_Vmin_to_F, player, phiH)
                    #add to F, and continue
                    F[i0]=1

                    #store layer information
                    if(store_layers):
                        self.infos["vertex layers"][i0]=mult*l
                        l+=1
                        
                    continue


                else: #no escapes! so we have found a Max dominion a return it

                    if(store_layers):#add layer info if needed
                        for i in range(self.game.size):
                            if Hplus[i]:
                                self.infos["vertex layers"][i]=mult*(l+2)

                    return(Hplus, phiH)


            else: #case where H+ is empty
                if(sum(H)): #if H is non-empty
                    #compute escaping edges (there must be one) ie from H cap Vmax to F
                    edges_from_H_cap_Vmax_to_F = [(i,j,w,e) for e,(i,j,w) in enumerate(self.game.edges) if H[i] and self.game.player[i] != player and F[j]]

                    #compute maximising edge and update in place
                    i0,_,_ = self.optimal_escaping_edge(edges_from_H_cap_Vmax_to_F,1-player,phiH)
                    
                    #add to F and continue 
                    F[i0]=1

                    #store layer information
                    if(store_layers):
                        self.infos["vertex layers"][i0]=mult*l
                        l+=1
                    
                    continue

                else: #H is empty, so we are done
    
                    return(None,None)
                    


    def compute_zones(self):  #recall, Min = 1, Max=0
        #computes zones of the game, and whether it is resolved
        N=[0]*self.game.size
        P=[0]*self.game.size
        Z=[0]*self.game.size
        for i in range(self.game.size):
            succweights=[(self.map[j] - self.map[i] + self.game.edges[edge_ind][2]) for (j,edge_ind) in self.game.succ[i]]
            if(self.game.player[i]):
                N[i]=any([w < 0 for w in succweights])
                P[i]=all([w > 0 for w in succweights])
            else:
                N[i]=all([w < 0 for w in succweights])
                P[i]=any([w > 0 for w in succweights])
            Z[i]=(not(N[i] or P[i]))
        esc=[0]*self.game.size
        for i in range(self.game.size):
            if (Z[i] and not(self.game.player[i])):
                esc[i]=sum([(self.map[j] - self.map[i] + self.game.edges[edge_ind][2] == 0 and not(N[j])) for (j,edge_ind) in self.game.succ[i]])
        Q=[i for i in range(self.game.size) if (Z[i] and self.game.player[i] and any([N[j] and self.map[j] - self.map[i] + self.game.edges[edge_ind][2] == 0 for (j,edge_ind) in self.game.succ[i]])) or (Z[i] and not(self.game.player[i]) and esc[i]==0)]
        ZN=N.copy()
        while(Q):
            i=Q.pop()
            ZN[i]=1
            for (j,edge_ind) in self.game.pred[i]:
                if(not(j in Q) and not(ZN[j]) and (self.map[i] - self.map[j] + self.game.edges[edge_ind][2] == 0)):
                    if self.game.player[j]:
                        Q.append(j)
                    else:
                        esc[j]-=1
                        if(esc[j]==0):
                            Q.append(j)
        resolved=True #we also return a boolean telling if the game is resolved or not
        for i in range(self.game.size):
            if ZN[i]:
                if self.game.player[i]:
                    i_is_resolved=False
                    for j,edge_ind in self.game.succ[i]:
                        weight = self.map[j] - self.map[i] + self.game.edges[edge_ind][2]
                        i_is_resolved=i_is_resolved or (ZN[j] and weight<=0)
                    resolved=resolved and i_is_resolved
                else:
                    for j,edge_ind in self.game.succ[i]:
                        weight = self.map[j] - self.map[i] + self.game.edges[edge_ind][2]
                        resolved= resolved and (ZN[j] and weight <= 0)
            else:
                if not(self.game.player[i]):
                    i_is_resolved=False
                    for j,edge_ind in self.game.succ[i]:
                        weight = self.map[j] - self.map[i] + self.game.edges[edge_ind][2]
                        i_is_resolved=i_is_resolved or (not(ZN[j]) and weight>=0)
                    resolved=resolved and i_is_resolved
                else:
                    for j,edge_ind in self.game.succ[i]:
                        weight = self.map[j] - self.map[i] + self.game.edges[edge_ind][2]
                        resolved= resolved and (not(ZN[j]) and weight >= 0)
        return(N,P,ZN,[1-ZN[i] for i in range(self.game.size)],resolved)

    def backtrack_all_paths(self, F):
        #updates F and self.map in place to encapsulate vertices whose paths all go to F
        esc = [0]*self.game.size
        for i in range(self.game.size):
            if not(F[i]):
                esc[i]=sum([not(F[j]) for (j,_) in self.game.succ[i]])
        Q = [i for i in range(self.game.size) if not(F[i]) and not(esc[i])]
        while Q:
            i=Q.pop()
            F[i]=1
            #compute optimal outgoing edge
            self.compute_optimal_outgoing_edge(i)

            #update queue and counts over predecessors
            for (j,_) in self.game.pred[i]:
                if(not(j in Q) and not(F[j])):
                    esc[j]-=1
                    if(esc[j]==0):
                        Q.append(j)
        return

    def attract(self,T,player):
        #updates self.map in place and returns player-attractor to T
        A=T.copy()
        esc = [0]*self.game.size
        for i in range(self.game.size):
            if not(T[i]) and (self.game.player[i] != player):
                esc[i]=sum([not(T[j]) for (j,_) in self.game.succ[i]])
        Q=[i for i in range(self.game.size) if (not(T[i]) and self.game.player[i] != player and esc[i]==0) or (not(T[i]) and self.game.player[i] == player and any([T[j] for (j,_) in self.game.succ[i]]))]
        while Q:
            i=Q.pop()
            A[i]=1
            if(self.game.player[i] != player):
                self.compute_optimal_outgoing_edge(i)
            else:
                j,edge_ind=min([(j,edge_ind) for (j,edge_ind) in self.game.succ[i] if A[j] and j != i])
                self.map[i] = self.map[j] + self.game.edges[edge_ind][2]
                self.infos["opt_edge"][edge_ind]=1

            for j,_ in self.game.pred[i]:
                if(not(j in Q) and not(A[j])):
                    if self.game.player[j] != player:
                        esc[j]-=1
                        if(esc[j]==0):
                            Q.append(j)
                    else:
                        Q.append(j)
        return(A)

    def compute_optimal_outgoing_edge(self, i):
        #compute optimal outgoing edge from i, update self.map in place and store opt edge
        j0,e0=self.game.succ[i][0]
        w0=self.game.edges[e0][2]
        opt=self.map[j0] + w0
        player_mult = 2 * self.game.player[i] -1
        for j, edge_ind in self.game.succ[i]:
            w=self.game.edges[edge_ind][2]
            if(player_mult * (self.map[j] + w) < player_mult * opt):
                opt = self.map[j] + w
                e0 = edge_ind

        #store optimal edge
        self.infos["opt_edge"][e0]=1

        #update map
        self.map[i] = opt


    def player_and_choice_modes(self, ZN, ZP, choice_mode):
        #computes player and choice_modes for future calls according to different
        #possible options (specified in the string choice_mode)
        rec_choice_mode=choice_mode
        attr_choice_mode=choice_mode
        if(choice_mode=='smallest'):
            player=(sum(ZP)<=sum(ZN)) #min if we pivot on ZN (ie compute sup^ZN)
        if(choice_mode=='alwaysZN'):
            player=1
        if(choice_mode=='alwaysZN_top_level'):
            player=1
            rec_choice_mode='smallest'
            attr_choice_mode='smallest'
        if(choice_mode=='alwaysZP'):
            player=0
        if(choice_mode=='random'):
            player=random.randrange(0,2)
        if(choice_mode=='top_level_prescribed'):
            player=self.infos["prescribed_choices"].pop(0) if self.infos["prescribed_choices"] else 0
            rec_choice_mode='smallest'
            attr_choice_mode='smallest'
        return(player, rec_choice_mode, attr_choice_mode)
        

    def reindex(self, setNrec, setPrec, phirec, incl, subgame_size):
        #reindexing zones and potential according to inclusion incl
        setN=[0]*self.game.size            
        setP=[0]*self.game.size
        phi=[0]*self.game.size
        for i in range(subgame_size):
            setN[incl[i]] = setNrec[i]
            setP[incl[i]] = setPrec[i]
            phi[incl[i]] = phirec[i]
        return(setN,setP,phi)
    
    
    def optimal_escaping_edge(self, edge_set, player, phiH):
        #computes optimal (ie minimal if player=1) edge within the edge set
        (i0,j0,w0,e0)=edge_set[0]
        opt=self.map[j0]-phiH[i0] + w0
        for (i,j,w,edge_ind) in edge_set:
            nopt=self.map[j] - phiH[i] + w
            if ((player and nopt < opt) or (not(player) and nopt > opt)):
                opt=nopt
                (i0,j0,w0)=(i,j,w)
                e0=edge_ind
        self.map[i0]=self.map[j0]+w0
        self.infos["opt_edge"][e0] = 1
        return(i0,j0,w0)


    def merge_resolving_potentials(self,player, nphi,A):
        #merges the two reducing potentials (self.map over A and nphi over Acompl)
        #using the right bias delta
        if(player):
            delta1 = min([w for i,j,w in self.game.edges if not(A[i]) and A[j]]) if any([not(A[i]) and A[j] for i,j,_ in self.game.edges]) else 0
            delta2 = min([self.map[i] for i in range(self.game.size) if A[i]])
            delta3 = max([nphi[i] for i in range(self.game.size) if not(A[i])])
            delta =  - delta1 - delta2 + delta3 
            
        else:
            delta1 = max([w for i,j,w in self.game.edges if not(A[i]) and A[j]]) if any([not(A[i]) and A[j] for i,j,_ in self.game.edges]) else 0
            delta2 = max([self.map[i] for i in range(self.game.size) if A[i]])
            delta3 = min([nphi[i] for i in range(self.game.size) if not(A[i])])
            delta =  (-delta1 - delta2 + delta3 )
        
        for i in range(self.game.size):
            self.map[i] = self.map[i] + delta if A[i] else nphi[i]
        

