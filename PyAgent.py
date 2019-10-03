# PyAgent.py   #
# Zane Partain #
# CS 440       #

import Action # GOFORWARD, GRAB, CLIMB, SHOOT, TURNLEFT, TURNRIGHT
import Orientation # RIGHT: 0, UP: 1, LEFT: 2, DOWN: 3

import random
import math

class PyAgent:

    def __init__(self):
        self.loc = [1,1]    # Agent start location
        self._arrow = True  # Agent starts with arrow
        self._gold = False  # Agent starts w/o gold
        self.orientation = Orientation.RIGHT # Agent starts right
        self.visited = []   # all locations the agent has visited
        self.stenches = []  # all of the stench locations visited
        self.wumpus = []    # wumpus locations
        self._wumpus = True # wumpus alive ? true : false
        
        self.x = False 
        self.y = False
        self.bump = False


    # return a random action turn 
    def random_turn (self):
        r = random.randint(0,10000)
        if r % 2 == 0:
            return Action.TURNRIGHT
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
    def dec_location(self):
        if  self.x == True:
            self.loc[0] -= 1
            self.x = False
        if self.y == True:
            self.loc[1] -= 1
            self.y = False
        self.bump = False
                

    # update the current location of agent
    def update_location (self, real=True):
        x,y = self.loc
        orientation = self.orientation

        if orientation == Orientation.RIGHT:
            if self.bump is False:
                x += 1
                self.x = True
        elif orientation == Orientation.LEFT and x > 1:
            x -= 1
        elif orientation == Orientation.UP:
           if self.bump is False:
                y += 1
                self.y = True
        elif orientation == Orientation.DOWN and y > 1:
            y -= 1

        self.loc[0] = x
        self.loc[1] = y

        #only update visited if its a real move and not used for agent logic 
        if real is True:
            if (self.loc[0], self.loc[1]) not in self.visited:
                self.visited.append((self.loc[0], self.loc[1]))


    # find all potential wumpus locations given 
    # current stench locations on the board
    def find_wumpus(self):
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

            wump_stenches[wump_loc] = {w1,w2,w3,w4} # add to dictionary
        
        return wump_stenches
            

    #calculate all potential wumpus locations.
    #keeping in mind all visited and stench locations.
    def calc_wumpus_loc(self):
        print('VISITED: ', self.visited)
        if (self.loc[0],self.loc[1]) not in self.stenches:
            self.stenches.append((self.loc[0],self.loc[1]))

        # if there is only one wumpus location then we know where the wumpus is
        if len(self.wumpus) is not 1:
            self.wumpus = self.find_wumpus() #list of potential wumpus locations
            print("WUMPUS POTENTIAL LOC: ", self.wumpus)
            print("STENCHES: ", self.stenches)

            # check if a potential wumpus location has already been 
            # visited. If it has, then there is no wumpus there.
            for i in range(len(self.visited)):
                if self.visited[i] in self.wumpus:
                    self.wumpus.remove(self.visited[i])
            
            print("WUMPUS POTENTIAL LOC UPDATE: ", self.wumpus)

            # calc all stench locations from potential wumpus locations
            wump_stenches = self.wump_to_stench() 

            # in visited but not in stench, so therefore there can't be a wumpus
            for loc, stench_list in wump_stenches.items():
                # print(loc, stench_list)
                for item in stench_list:
                    if item in self.visited and item not in self.stenches:
                        # print(item)
                        if loc in self.wumpus:
                            self.wumpus.remove(loc)

            print("WUMPUS POTENTIAL LOC UPDATE 2.0: ", self.wumpus)

                   
    # return True or False whether or not the go forward action is rational
    def logical_move(self):
        x, y = self.loc
        safe = False 
        self.update_location(False) # set the agent forward theoretically
        print('THEORETICAL LOC ', self.loc)
        print("WUMPUS POTENTIAL LOC UPDATE 2.0: ", self.wumpus)

        if (self.loc[0], self.loc[1]) not in self.wumpus:
            safe = True 
        
        # decrement the theoretical location back to actual location
        self.dec_location()
        print(x, y)
        self.loc[0] = x
        self.loc[1] = y
        print(self.loc)

        return safe



    
agent = PyAgent() # init agent

def PyAgent_Constructor ():
    print("PyAgent_Constructor")

def PyAgent_Destructor ():
    print("PyAgent_Destructor")

def PyAgent_Initialize ():
    print("PyAgent_Initialize")


def PyAgent_Process (stench,breeze,glitter,bump,scream):
    global agent
    perceptStr = ""
    print('location: ', agent.loc)
    print('orientation: ', agent.orientation)
    print('arrow: ', agent._arrow)
    print('gold: ', agent._gold)
    
    if agent.loc is [1,1] and agent._gold:
        return Action.CLIMB

    if (stench == 1):
        perceptStr += "Stench=True,"
        agent.calc_wumpus_loc()
        #don't kill wumpus for this sim
        #if agent._arrow:
        #    agent._arrow = False
        #   return Action.SHOOT
    else:
        perceptStr += "Stench=False,"
    if (breeze == 1):
        perceptStr += "Breeze=True,"
    else:
        perceptStr += "Breeze=False,"
    if (glitter == 1):
        perceptStr += "Glitter=True,"
        agent._gold = True
        return Action.GRAB
    else:
        perceptStr += "Glitter=False,"
    if (bump == 1):
        perceptStr += "Bump=True,"
        agent.bump = True
        action = agent.random_turn()
        agent.update_orientation(action)
        agent.dec_location()
        return action
    else:
        perceptStr += "Bump=False,"
    if (scream == 1):
        perceptStr += "Scream=True"
    else:
        perceptStr += "Scream=False"
    print("PyAgent_Process: " + perceptStr)
    
    # update location then move
    _flag = random.randint(0,10000)
    if _flag % 2 == 0:
        action = agent.random_turn()
        agent.update_orientation(action)
        print(agent.loc)
        return action
    else:
        if agent.logical_move() is True:
            agent.update_location()
            return Action.GOFORWARD
        else:
            action = agent.random_turn()
            agent.update_orientation(action)
            print(agent.loc)
            return action
        

def PyAgent_GameOver (score):
    print("PyAgent_GameOver: score = " + str(score))

