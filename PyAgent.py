# PyAgent.py   #
# Zane Partain #
# CS 440       #

import Action # GOFORWARD, GRAB, CLIMB, SHOOT, TURNLEFT, TURNRIGHT
import Orientation # RIGHT: 0, UP: 1, LEFT: 2, DOWN: 3

import random

class PyAgent:

    def __init__(self):
        self.loc = [1,1]   # Agent start location
        self._arrow = True # Agent starts with arrow
        self._gold = False # Agent starts w/o gold
        self.orientation = Orientation.RIGHT # Agent starts right
        
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

    def dec_location(self):
        if  self.x == True:
            self.loc[0] -= 1
            self.x = False
        if self.y == True:
            self.loc[1] -= 1
            self.y = False
        self.bump = False
                

    # update the current location of agent
    def update_location (self):
        x,y = self.loc
        orientation = self.orientation

        if orientation == Orientation.RIGHT:
            if self.bump == True:
                self.dec_location()
            else:    
                x += 1
                self.x = True
        elif orientation == Orientation.LEFT and x > 1:
            x -= 1
        elif orientation == Orientation.UP:
            if self.bump == True:
                self.dec_location()
            else:    
                y += 1
                self.y = True
        elif orientation == Orientation.DOWN and y > 1:
            y -= 1


        self.loc[0] = x
        self.loc[1] = y


    
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

    if agent.loc == [1,1] and agent._gold:
        return Action.CLIMB

    if (stench == 1):
        perceptStr += "Stench=True,"
        if agent._arrow:
            agent._arrow = False
            return Action.SHOOT
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
    agent.update_location()
    return Action.GOFORWARD

def PyAgent_GameOver (score):
    print("PyAgent_GameOver: score = " + str(score))
