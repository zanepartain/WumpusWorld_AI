# PyAgent.py   #
# Zane Partain #
# CS 440       #

import Action # GOFORWARD, GRAB, CLIMB, SHOOT, TURNLEFT, TURNRIGHT
import Orientation # RIGHT: 0, UP: 1, LEFT: 2, DOWN: 3

import random
import math

class PyAgent:

    def __init__(self):
        self.loc = [1,1]       # Agent start location
        self.path = [(1,1)]    # path of agent
        self._arrow = True     # Agent starts with arrow
        self.arrow_path = None # Arrow path ; orientation, and respective coord
           
        self._gold = False     # Agent starts w/o gold
        self.visited = [(1,1)] # all locations the agent has visited
        self.stenches = []     # all of the stench locations visited
        self.wumpus = []       # wumpus locations
        self._wumpus = True    # wumpus alive ? true : false
        self.orientation = Orientation.RIGHT # Agent starts right
        
        # flags for when bump is true
        self.bump = False 



    # return a random action turn 
    def random_turn (self):
        r = random.randint(0,10000)
        if r % 2 == 0:
            return Action.TURNLEFT
        else:
            return Action.TURNLEFT


    # adjust orientation of the agent
    def update_orientation (self, action):
        if action == Action.TURNLEFT:
            self.orientation = (self.orientation + 1) % 4
        if action == Action.TURNRIGHT:
            self.orientation = (self.orientation + 3) % 4 


    # this is for ensuring the locations stays in bounds
    # decrement the most recently updated direction by 1
    def dec(self):
        # print('(TO PREV LOC)')
        # print('(USING PREV LOC! )', self.path[-1])
        self.loc[0], self.loc[1] = self.path.pop()
        self.bump = False
        # print('UPDATED_LOC ', self.loc)

                

    # update the current location of agent
    def update_location (self, real=True):
        x,y = self.loc
        orientation = self.orientation
        self.path.append((self.loc[0], self.loc[1])) # before updating add to path
        # print('PREV LOC:', self.path[-1])
    
        # only when the bump flag is false increment the x & y
        if orientation == Orientation.LEFT and x > 1:
            x -= 1
        elif orientation == Orientation.DOWN and y > 1:
            y -= 1
        if orientation == Orientation.RIGHT:
            x += 1
        elif orientation == Orientation.UP:
            y += 1

        self.loc[0] = x
        self.loc[1] = y

        # print('UPDATED_LOC ', self.loc)


    def KB_AGENT(self, percept_str=str):
        percepts = percept_str.strip().split(',')
        rand_move = random.randint(1,51)
        
        percept_dict = {}
        for p in percepts:
            x,y = p.split('=')
            percept_dict[x] = y
        
        # agent has gold and is at start loc
        if self._gold and self.loc == [1,1]:
            return Action.CLIMB
            #implement logic for agent to find his way back home safely/ shortest path
            # A* search

        if percept_dict['Stench'] == 'True':
            # shoot arrow, and keep track of all cells that the arrow passes
            if self._arrow:
                self._arrow = False

                # TODO incorporate this into a function so you can ential wumpus locations in KB_entail_wumpus()
                # keep track of y coordinate for RIGHT or LEFT
                if self.orientation == Orientation.RIGHT:
                    # every cell right of the current position can't have a wumpus
                    print('Arrow path = every cell RIGHT of {} has no Wumpus'.format(self.loc))
                   
                elif self.orientation == Orientation.LEFT:
                    # every cell left of the current position can't have a wumpus
                    print('Arrow path = every cell LEFT of {} has no Wumpus'.format(self.loc))
                
                # keep track of x coordinate for UP or DOWN
                elif self.orientation == Orientation.UP:
                    # every cell above of the current position can't have a wumpus
                    print('Arrow path = every cell ABOVE {} has no Wumpus'.format(self.loc))                  
                    
                elif self.orientation == Orientation.DOWN:
                    # every cell below of the current position can't have a wumpus
                    print('Arrow path = every cell BELOW {} has no Wumpus'.format(self.loc))                   

                # save the orientation and current location
                self.arrow_path = (self.orientation, (self.loc[0],self.loc[1]))
                return Action.SHOOT
                
            # add current loc to KB stenches
            if (self.loc[0],self.loc[1]) not in self.stenches:
                self.stenches.append((self.loc[0],self.loc[1]))

            # entail wumpus locations from KB
            if self._wumpus is True:
                self.KB_entail_wumpus()

        if percept_dict['Breeze'] == 'True':
            pass
        if percept_dict['Glitter'] == 'True':
            self._gold = True
            return Action.GRAB
        if percept_dict['Bump'] == 'True':
            self.bump = True
            action = self.random_turn()
            self.update_orientation(action)
            self.dec()
            return action
        if percept_dict['Scream'] == 'True':
            # update all potential wumpus areas to safe
            self._wumpus = False
            self.wumpus = []####### ####### #######
        


        # randomly go forward or turn
        if (rand_move % 2 == 0):
            # add current location to visited if not already
            if (self.loc[0],self.loc[1]) not in self.visited:
                self.visited.append((self.loc[0],self.loc[1]))
            
            self.update_location()  # update current location

            # if the updated location is not safe then dec location
            # and dont go forward ; perform random turn
            if (self.loc[0], self.loc[1]) in self.wumpus:
                self.dec()
                # random turn
                action = self.random_turn()
                self.update_orientation(action)
                return action

            print('VISITED: ', self.visited)
            return Action.GOFORWARD
        else: 
            # random turn
            action = self.random_turn()
            self.update_orientation(action)
            return action



    # find all potential wumpus locations given KB
    # of current stench locations on the board
    def stench_to_wump(self):
        if not self.bump:
            if len(self.stenches) == 1:
                # this will be for when you only have 1 stench loc calculate 
                # all 4 potential wumpus locations w/o considering visited locations
                w1 = (self.stenches[0][0],self.stenches[0][1]+1) # y + 1
                w2 = (self.stenches[0][0],self.stenches[0][1]-1) # y - 1
                w3 = (self.stenches[0][0]+1,self.stenches[0][1]) # x + 1
                w4 = (self.stenches[0][0]-1,self.stenches[0][1]) # x - 1

                return [w1,w2,w3,w4] #return list of potential wumpus loc

            elif len(self.stenches) == 2:
                # this will be for when you only have 2 stench loc
                # if the two cells are in the same row, Top and Bottom stenches
                if (self.stenches[0][0] == self.stenches[1][0]):
                    y = math.floor(((self.stenches[0][1] + self.stenches[1][1]) / 2)) # e.g. 3+2 = 5/2 = floor(2.5) = 2
                    return [(self.stenches[0][0], y)]

                # if the two cells are in the same column, Left and Right stenches
                elif (self.stenches[0][1] == self.stenches[1][1]):
                    x = math.floor(((self.stenches[0][0] + self.stenches[1][0]) / 2)) # e.g. 3+2 = 5/2 = floor(2.5) = 2
                    return [(x, self.stenches[0][1])]

                # given 2 diagonalstench locations (s1,s2) simply swap the x, and y 
                # coordinates to find the potential wumpus locations
                w1 = ((self.stenches[0][0],self.stenches[1][1])) # (s1:x, s2:y)
                w2 = ((self.stenches[1][0],self.stenches[0][1])) # (s2:x, s1:y)
                    
                return [w1,w2]

            else:
                # at this point we have 3 or more stenches so we can find the Wumpus.
                # 2/3 or more cells will share a coordinate (x or y) that can we can use to
                # determine the location of the wumpus.
                x = -1
                y = -1
                self.stenches.sort() # sort stenches by x in (x,y)
                for i in range(len(self.stenches) - 1):
                    if self.stenches[i][0] == self.stenches[i+1][0]:
                        x = i # case of two x's the same 
                    if self.stenches[i][1] == self.stenches[i+1][1]:
                        y = i # case of two y's the same 
                
                if x is -1:
                    # x is -1, we know that the loc is between our coords with same y
                    return [(math.floor(((self.stenches[y][0] + self.stenches[y+1][0]) / 2)), self.stenches[y][1])]
                if y is -1:
                    # y is -1, we know that the loc is between our coords with same x
                    return [(self.stenches[x][0], math.floor(((self.stenches[x][1] + self.stenches[x+1][1]) / 2)))]
                else:
                    # we have both x and y
                    return [(self.stenches[x][0], self.stenches[y][1])]


    # calc all the potential stench locations for all potential wumpus locations.
    # if the potential stench cell is not in the stenches[] but is in visited[]
    # we can say that there is no wumpus in the potential wumpus location.
    def wump_to_stench(self):
        wump_stenches = {}
        for wump_loc in self.wumpus:
            w1 = (wump_loc[0],wump_loc[1]+1) # y + 1
            w2 = (wump_loc[0],wump_loc[1]-1) # y - 1
            w3 = (wump_loc[0]+1,wump_loc[1]) # x + 1
            w4 = (wump_loc[0]-1,wump_loc[1]) # x - 1

            wump_stenches[wump_loc] = {w1,w2,w3,w4} # add dictionary entry
        
        return wump_stenches
            

    #calculate all potential wumpus locations.
    #keeping in mind all visited and stench locations.
    def KB_entail_wumpus(self):
        print('STENCHES: ', self.stenches)
        if not self.bump:
            # if there is only one wumpus location then we know where the wumpus is
            if len(self.wumpus) != 1:
               
                # list[()] of potential wumpus locations by KB stenches
                self.wumpus = self.stench_to_wump()
                print('WUMPUS LOC: ', self.wumpus)
                
                # check if a potential wumpus location has already been visited.
                # If so, it is a safe location
                for space in self.wumpus:
                    if space in self.visited:
                        print(' REMOVE {} from potential wumpus locations | (VISITED) => ~WUMPUS'.format(space))
                        self.wumpus.remove(space)

                # TODO look at KB_AGENT() Stench=True for inspo
                # check if the potential wumpus locations are in KB arrow_path:
                if self.arrow_path is not None:
                    # compare the potential wumpus locations to the arrow path
                    # if they intersect, then delete the potential wumpus location
                    pass 

                # calc all stench locations from potential wumpus locations
                wump_stenches = self.wump_to_stench() 
                for loc, stench in wump_stenches.items():
                    print(" @ WUMPLOC {}: stenches = {}".format(loc,stench))

                # if potential stench location is in visited[] but not in stenches[],
                # there can't be a wumpus at that potential wumpus location
                for loc, stench_list in wump_stenches.items():
                    # print(loc, stench_list)
                    for item in stench_list:
                        if item in self.visited and item not in self.stenches:
                            if loc in self.wumpus:
                                print(' REMOVE {} from potential wumpus locations | (VISITED ^ ~STENCH) => ~WUMPUS'.format(loc))
                                self.wumpus.remove(loc)

                print("WUMPUS LOC UPDATED: ", self.wumpus)
            else:
                print('WUMPUS FOUND AT {}'.format(self.wumpus))

                   
    # return True or False whether or not the go forward action is rational
    def logical_move(self):
       pass


agent = PyAgent() # init agent

def PyAgent_Constructor ():
    print("PyAgent_Constructor")

def PyAgent_Destructor ():
    print("PyAgent_Destructor")

def PyAgent_Initialize ():
    print("PyAgent_Initialize")

count = 0

def PyAgent_Process (stench,breeze,glitter,bump,scream):
    global agent
    perceptStr = ""
    _flag = random.randint(0,10001)
    print('location: ', agent.loc)
    print('orientation: ', agent.orientation)
    print('arrow: ', agent._arrow)
    print('gold: ', agent._gold)

    if (stench == 1):
        perceptStr += "Stench=True,"
    else:
        perceptStr += "Stench=False,"
    if (breeze == 1):
        perceptStr += "Breeze=True,"
    else:
        perceptStr += "Breeze=False,"
    if (glitter == 1):
        perceptStr += "Glitter=True,"
    else:
        perceptStr += "Glitter=False,"
    if (bump == 1):
        perceptStr += "Bump=True,"
    else:
        perceptStr += "Bump=False,"
    if (scream == 1):
        perceptStr += "Scream=True"
    else:
        perceptStr += "Scream=False"

    return agent.KB_AGENT(perceptStr)
    


def PyAgent_GameOver (score):
    print("PyAgent_GameOver: score = " + str(score))

