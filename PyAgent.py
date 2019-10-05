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
        self._arrow = True     # Agent starts with arrow
        self._gold = False     # Agent starts w/o gold
        self.visited = [(1,1)] # all locations the agent has visited
        self.stenches = []     # all of the stench locations visited
        self.wumpus = []       # wumpus locations
        self.gold_road = []    # path to previous gold 
        self.golden_ticket = False   # let agent know they are on previous known gold path
        self._wumpus = True    # wumpus alive ? true : false
        self._sorted = True    # whether or not the visited list is sorted
        self.orientation = Orientation.RIGHT # Agent starts right
        
        # flags for when bump is true
        self.bump = False 
        self.x = False 
        self.y = False


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
    
        # only when the bump flag is false increment the x & y
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


    #returns an array of all possible safe moves from given location
    def possible_moves(self):
        # unvisited flag will determine whether or not you want
        # to get all possible moves that are safe
        moves = []

        # ensure the UP and RIGHT directions are safe 
        if (self.loc[0] + 1, self.loc[1]) not in self.wumpus:
            moves.append((self.loc[0] + 1, self.loc[1])) # x + 1
        if (self.loc[0], self.loc[1] + 1) not in self.wumpus:
            moves.append((self.loc[0], self.loc[1] + 1)) # y + 1

        # ensure LEFT and DOWN directions are in bounds and safe
        if self.loc[0] > 1:
            if (self.loc[0]-1, self.loc[1]) not in self.wumpus:
                moves.append((self.loc[0] - 1, self.loc[1])) # x - 1
        if self.loc[1] > 1:
            if (self.loc[0], self.loc[1] - 1) not in self.wumpus:
                moves.append((self.loc[0], self.loc[1]-1)) # y - 1
        
        return moves



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
    def calc_wumpus_loc(self):
        if not self.bump:
            if (self.loc[0],self.loc[1]) not in self.stenches:
                self.stenches.append((self.loc[0],self.loc[1]))

            # if there is only one wumpus location then we know where the wumpus is
            if len(self.wumpus) is not 1:
                self.wumpus = self.find_wumpus() #list of potential wumpus locations
                
                # check if a potential wumpus location has already been 
                # visited. If it has, then there is no wumpus there.
                for i in range(len(self.visited)):
                    if self.visited[i] in self.wumpus:
                        self.wumpus.remove(self.visited[i])
                
                # calc all stench locations from potential wumpus locations
                wump_stenches = self.wump_to_stench() 

                # if potential stench location is in visited[] but not in stenches[],
                # there can't be a wumpus at that potential wumpus location
                for loc, stench_list in wump_stenches.items():
                    # print(loc, stench_list)
                    for item in stench_list:
                        if item in self.visited and item not in self.stenches:
                            # print(item)
                            if loc in self.wumpus:
                                self.wumpus.remove(loc)

                print("WUMPUS POTENTIAL LOC UPDATED: ", self.wumpus)
                print("STENCHES UPDATED: ", agent.stenches)

                   
    # return True or False whether or not the go forward action is rational
    def logical_move(self):
        move = ()
        x, y = self.loc
        safe = False 
        self.update_location(False) # set the agent forward theoretically
        print("WUMPUS POTENTIAL LOC UPDATE 2.0: ", self.wumpus)

        if self._gold is False and len(self.gold_road) > 0:
            gold_move = self.gold_road.pop()
            if gold_move not in self.wumpus:
                print("HIHIHIHIHH")
                safe = True
                move = gold_move
                self.golden_ticket = True
            elif (self.loc[0], self.loc[1]) not in self.wumpus:
                safe = True 
                move = (self.loc[0], self.loc[1])
        else:
            if (self.loc[0], self.loc[1]) not in self.wumpus:
                safe = True 
                move = (self.loc[0], self.loc[1])

        # decrement the theoretical location back to actual location
        self.dec_location()
        self.loc[0] = x
        self.loc[1] = y

        return safe, move


    # set a path for the agent to return home on the quickest path it has traveled
    def go_home(self):
        safe_moves = self.possible_moves() 
        print("SAFE MOVES: ", safe_moves)

        self.visited.sort() # sort all visited space ascending 

        # go through all locations in ascending order (1,1) (1,2) ...
        for loc in self.visited:
            if loc in safe_moves:
                # if the loc in the safe moves then you 
                # know the next best move
                print("NEXT BEST MOVE: ", loc)
                return loc


    # push the cells on the path back from the gold to [1,1] in a stack.
    # the stack will be used to for the agent to move to first (if safe)
    def money_grabber(self, cell=None):
        if cell is None:
            self.gold_road.append((self.loc[0], self.loc[1]))
        elif cell not in self.gold_road:
            print('MONEY GRABBER: ', self.gold_road)
            self.gold_road.append(cell)

    
    # return True if the next_move param is closer to [1,1] than the best move
    def is_closer(self, next_move, best_move):
        # this does not account for closest to [1,1] yet
        # needs work... ... ...
        self.visited.sort()
        if next_move < best_move:
            return True

        return False


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
    print("GOLD ROAD:", agent.gold_road)
    perceptStr = ""
    _flag = random.randint(0,10001)
    print('location: ', agent.loc)
    print('orientation: ', agent.orientation)
    print('arrow: ', agent._arrow)
    print('gold: ', agent._gold)
    print('VISITED: ', agent.visited)
    print("STENCHES: ", agent.stenches)
    print("WUMPUS POTENTIAL LOC: ", agent.wumpus)
    
    # if agent has gold; GO HOME or CLIMB
    if agent._gold and bump != 1:
        if agent.loc == [1,1]:
            return Action.CLIMB

        best_move = agent.go_home() # return on quickest path back to start one cell at a time
        safe, next_move = agent.logical_move()  # check if going forward is safe

        print('NEXT MOVE: ', next_move)
        # the best theoretical move to get to [1,1] 
        # from current location is also the next potential move
        if next_move == best_move:
            agent.update_location()
            agent.money_grabber(best_move)
            return Action.GOFORWARD

        # if you were to move forward and the area is safe (visited or unvisited)
        # and it gets you closer to [1,1] than your best move. Then GOFORWARD!!
        elif safe is True and agent.is_closer(next_move,best_move):
            agent.update_location()
            agent.money_grabber(next_move)
            return Action.GOFORWARD

        # your best theoretical move is not your potential next move. And your
        # potential next move is either not safe, or will take you in the wrong direction
        else:
            action = Action.TURNLEFT
            agent.update_orientation(action)
            return action

        


    if (stench == 1):
        perceptStr += "Stench=True,"
        agent.calc_wumpus_loc()
        # don't kill wumpus for this sim
        #if agent._arrow:
        #   agent._arrow = False
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
       
        agent.money_grabber()
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
    # randomly turn or go forward (if can) otherwise turn 
    safe, move = agent.logical_move()

    if safe is True:
        if agent.golden_ticket is True:
            agent.golden_ticket = False
            print('TO MOVE GOLDEN TICKET: ', move)
            agent.update_location()
            return Action.GOFORWARD
        if _flag % 2 == 0:
            print('TO MOVE: ', move)
            agent.update_location()
            return Action.GOFORWARD
        
    # randomly turn
    action = agent.random_turn()
    agent.update_orientation(action)
    return action
    


def PyAgent_GameOver (score):
    print("PyAgent_GameOver: score = " + str(score))

