# PyAgent.py

from random import randint
import Action
import Orientation
import itertools

    
class WorldState:
    def __init__(self):
        self.agentLocation = [1,1]
        self.agentOrientation = Orientation.RIGHT
        self.agentHasArrow = True
        self.agentHasGold = False
        
        # HW5
        self.goldLocation = [0,0]
        self.worldSize = 0
    
class Agent:
    def __init__(self):
        self.worldState = WorldState()
        self.previousAction = Action.CLIMB
        self.actionList = []
        
        # HW5
        self.firstTry = True
        self.pathToGold = []
        self.possibleWumpusLocations = []
        self.visitedLocations = []
        self.safeLocations = []
        self.stenchLocations = []
        self.clearLocations = []
        
        # HW9
        self.pitLocations = [[0.2 for i in range(5)]for j in range(5)]
        self.printPitLocs = [[0.2 for i in range(5)]for j in range(5)] # just for printing orientation
        self.breezeLocations = []
        self.noPitLocs = []
        self.pitLocs = []
    
    def Initialize(self):
        self.worldState.agentLocation = [1,1]
        self.worldState.agentOrientation = Orientation.RIGHT
        self.worldState.agentHasArrow = True
        self.worldState.agentHasGold = False
        self.previousAction = Action.CLIMB
        self.actionList = []
        self.pitLocations[0][0] = 0.0
        self.printPitLocs[0][0] = 0.0
        self.noPitLocs = [[1,1]]


        # HW5
        if (self.firstTry):
            self.worldState.goldLocation = [0,0] # unknown
            self.worldState.worldSize = 0 # unknown
            self.pathToGold.append([1,1]) # path starts in (1,1)
        else:
            if (self.worldState.goldLocation == [0,0]):
                # Didn't find gold on first try (should never happen, but just in case)
                self.pathToGold = []
                self.pathToGold.append([1,1])
            else:
                self.AddActionsFromPath(True) # forward through path from (1,1) to gold location

        # HW9
        self.pitLocations = [[0.2 for i in range(5)] for j in range(5)]

    def Process(self, percept):
        self.UpdateState(percept)
        if (not self.actionList):
            if (percept['Glitter']):
                self.actionList.append(Action.GRAB)
                self.AddActionsFromPath(False) # HW5: reverse path from (1,1) to gold location
            elif (self.worldState.agentHasGold and (self.worldState.agentLocation == [1,1])):
                self.actionList.append(Action.CLIMB)
            else:
                self.actionList.append(self.ChooseAction(percept)) # HW5
        action = self.actionList.pop(0)
        self.previousAction = action
        return action
    
    def GameOver(self, score):
        # HW5
        self.firstTry = False
    
    def UpdateState(self, percept):
        currentOrientation = self.worldState.agentOrientation
        
        if (self.previousAction == Action.GOFORWARD):
            # HW5
            if (percept['Bump']):
                # Check if we can determine world size
                if (self.worldState.agentOrientation == Orientation.RIGHT):
                    self.worldState.worldSize = self.worldState.agentLocation[0]
                if (self.worldState.agentOrientation == Orientation.UP):
                    self.worldState.worldSize = self.worldState.agentLocation[1]
                if (self.worldState.worldSize > 0):
                    self.FilterSafeLocations()
            else:
                self.worldState.agentLocation = self.GetGoForward()
                if (self.worldState.goldLocation == [0,0]):
                    # If haven't found gold yet, add this location to the pathToGold
                    self.AddToPath(self.worldState.agentLocation)

                
        if (self.previousAction == Action.TURNLEFT):
            self.worldState.agentOrientation = (currentOrientation + 1) % 4
            
        if (self.previousAction == Action.TURNRIGHT):
            currentOrientation -= 1
            if (currentOrientation < 0):
                currentOrientation = 3
            self.worldState.agentOrientation = currentOrientation
            
        if (self.previousAction == Action.GRAB):
            self.worldState.agentHasGold = True # Only GRAB when there's gold
            self.worldState.goldLocation = self.worldState.agentLocation # HW5
            
        if (self.previousAction == Action.SHOOT):
            self.worldState.agentHasArrow = False
            
            # HW5
            # The only situation where we shoot is if we start out in (1,1)
            # facing RIGHT, perceive a stench, and don't know the wumpus location.
            # In this case, a SCREAM percept means the wumpus is in (2,1) (and dead),
            # or if no SCREAM, then the wumpus is in (1,2) (and still alive).
            if self.worldState.agentLocation == [1,1]:
                self.possibleWumpusLocations = []
                if (percept['Scream']):
                    self.possibleWumpusLocations.append([2,1])
                else:
                    self.possibleWumpusLocations.append([1,2])

            # HW9 :: wumpus cannot be in location that agent shot
            else:
                # In this scenario an agent is facing a location where there might be a wumpus
                # But we definitely know there is not a pit. So after shooting the arrow, the are
                # can be considered safe as we know now there is no pit or wumpus in that location
                if self.GetGoForward() in self.possibleWumpusLocations:
                    self.possibleWumpusLocations.remove(self.GetGoForward())
                    self.AddNewLocation(self.safeLocations,self.GetGoForward())

            
        # Update visited locations and safelocations        
        self.AddNewLocation(self.visitedLocations, self.worldState.agentLocation)
        self.AddNewLocation(self.safeLocations, self.worldState.agentLocation)

        # HW5 | HW9
        # Update safe locations, stench locations, clear locations,
        # and possible wumpus locations.
        if (percept['Stench'] and percept['Breeze']):
            self.AddNewLocation(self.stenchLocations, self.worldState.agentLocation)
            # HW9 :: update pit prob if experienced breeze
            self.AddNewLocation(self.breezeLocations, self.worldState.agentLocation)
            self.UpdatePitProb()
        elif (percept['Stench']):
            self.AddNewLocation(self.stenchLocations, self.worldState.agentLocation)
            self.AddAdjacentLocations(self.noPitLocs, self.worldState.agentLocation)
        elif (percept['Breeze']):
            # HW9 :: update pit prob if experienced breeze
            self.AddNewLocation(self.breezeLocations, self.worldState.agentLocation)
            self.UpdatePitProb()
        else:
            self.AddNewLocation(self.clearLocations, self.worldState.agentLocation)
            self.AddAdjacentLocations(self.safeLocations, self.worldState.agentLocation)
        if (len(self.possibleWumpusLocations) != 1):
            self.UpdatePossibleWumpusLocations()
        # HW9 :: only update pit prob if we move
        if len(self.breezeLocations) > 0:
            if 0 < self.worldState.agentLocation[0] <= 5 and 0 < self.worldState.agentLocation[1] <= 5:
                print(self.worldState.agentLocation)
                self.UpdatePitProb()
        
        self.ClearPitLocs()
        self.PrintPitLocations()
        self.Output()


    # HW9 :: if it is a retrial populate all previously known pits (found or killed by)
    def PopulateKnownPits(self, pits):
        print('PIT LOCS:',pits)
        if pits:
            for loc in pits:
                self.pitLocations[loc[0]-1][loc[1]-1] = 1.00
                self.printPitLocs[loc[1]-1][loc[0]-1] = 1.00


    # HW9 :: ensure pit is within bounds of pit[5][5]
    def PitBounds(self,pit):
        if 0 < pit[0] <= 5 and 0 < pit[1] <= 5:
            return True
        return False

        
    # HW9
    # Print Pit Locations and their probabilities for 5x5 world  
    def PrintPitLocations(self):
        print('P(pit):')
        for i in range(5):
            for j in range(5):
                print('{:.2f} '.format(self.printPitLocs[4-i][j])), 
                pass
            print('\n')


    # HW9 :: set all pit probabilities to 0.0 if they are in clear 
    def ClearPitLocs(self):
        if self.safeLocations:
            for clearLoc in self.safeLocations:
                if 0 < clearLoc[0] <= 5 and 0 < clearLoc[1] <= 5:
                    self.pitLocations[clearLoc[0]-1][clearLoc[1]-1] = 0.0
                    self.printPitLocs[clearLoc[1]-1][clearLoc[0]-1] = 0.0
        if self.noPitLocs:
            for loc in self.noPitLocs:
                if 0 < loc[0] <= 5 and 0 < loc[1] <= 5:
                    self.pitLocations[loc[0]-1][loc[1]-1] = 0.0
                    self.printPitLocs[loc[1]-1][loc[0]-1] = 0.0
        

    # HW9
    # Iterate over all known breeze locations and update pit location probabilities
    def UpdatePitProb(self):
        self.ClearPitLocs()
        pitAlreadyCalc = []  # store already calculated pit probability locations
        # find all adjacent pit locations from a breeze given they aren't clear
        for breeze in self.breezeLocations:
            adjPits = []
            self.AddAdjacentLocations(adjPits, breeze)
            adjPits = [loc for loc in adjPits if loc not in self.safeLocations and loc not in self.noPitLocs and self.PitBounds(loc) and loc not in knownPits] # eliminate all clear locations
            for pit in adjPits:
                if pit not in pitAlreadyCalc:
                    prob = self.CalculatePitProbability(pit)
                    pitAlreadyCalc.append(pit)
                    self.pitLocations[pit[0]-1][pit[1]-1] = prob  # update prob of pit at given location
                    self.printPitLocs[pit[1]-1][pit[0]-1] = prob  # update prob of pit at given location
                    if prob == 1.00:
                       knownPits.append(pit)

        # self.PrintPitLocations()
    

    # HW9
    # calculate the distribution probability of a pit, then return the truth value
    def CalculatePitProbability(self, pit):
        frontier = self.GetFrontier(pit, self.visitedLocations) # get the frontier of the query pit
        dist = [0.00,0.00]
        alpha = 0.00

        print('----------------------------')
        print('query pit', pit)
        print('breezes:', self.breezeLocations)
        print('known:', self.visitedLocations)  # 
        print('frontier:', frontier)

        # avoid divide by 0 exception
        if pit not in self.noPitLocs:
            dist = self.DistProbPit(pit, frontier, self.breezeLocations) # get distribution probabilites of <pit, ~pit>
            if sum(dist) != 0:
                alpha = round(1/(dist[0] + dist[1]),2)

        print('alpha={}, dist={}'.format(alpha,dist))
        print('ans=<{},{}>'.format(round(dist[0]*alpha, 2),round(dist[1]*alpha,2)))
        
        return round(dist[0]*alpha, 2) # return probability pit is true


    # HW9
    # calculate the frontier from the pit query adjacent breeze's given they aren't clear
    def GetFrontier(self, pit, known):
        frontier = []
        for loc in known:
            adjPits = []
            self.AddAdjacentLocations(adjPits, loc)
            adjPits = [loc for loc in adjPits if loc not in self.safeLocations and loc != pit and self.PitBounds(loc)] # eliminate all clear locations
            # adjPits.remove(pit) # remove the query pit
            [frontier.append(x) for x in adjPits if x not in frontier]
        return frontier


    # HW9
    # return the permutations of pit probabilities given the number of frontier pits
    def GetFrontierPermutations(self, frontier):
        l = [ (0.2,), (0.8,) ]
        if len(frontier) > 1:  # there can only be two pits max in the frontier in this case
            perm = [0.2] * (len(frontier))
            perm.remove(0.2)  # enter loop with one frontier pit false
            perm.append(0.8)
            
            l = [(0.2,) * (len(frontier))]  # case wehre all frontier pits are true
            # loop until all pits are false
            while len(set(perm)) != 1:
                # append the permutation if not already in the list
                [l.append(x) for x in itertools.permutations(perm, len(frontier)) if x not in l]
                if 0.2 in perm:
                    perm.remove(0.2)
                    perm.append(0.8)
            l.append((0.8,)*(len(frontier)))  # case wehre all frontier pits are false

        return l


    # HW9
    # determine probability of a breeze given pit and frontier probabilities
    def BreezeProb(self, pit, frontier, Ppit, Pfrontier, allBreezes):
        # for the set of breezes calculate all pits each one depend on 
        breezes = {}
        for b in allBreezes:
            breezes[str(b)] = []
            self.AddAdjacentLocations(breezes[str(b)], b)
            breezes[str(b)] = [loc for loc in breezes[str(b)] if loc not in self.safeLocations and loc not in self.noPitLocs] # eliminate all clear locations

        #  -- truthPit = None
        #  -- print('////////////////')
        #  -- print('pits: {} {}'.format(pit,frontier))
        #  -- print('prob: {} {}'.format(Ppit, Pfrontier))
        #  -- print('Breeze dependencies: {}'.format(breezes))

        # parallel boolean array for indicating satisfied breezes in breeze set
        satisfied = []
        [satisfied.append(False) for x in breezes]  
        index = 0  # to specify which breeze we are currently looking at
        for key, val in breezes.items():
            for i in range(len(val)):
                if satisfied[index] is False:  # if the current breeze is not already satisfied
                    if val[i] == pit and Ppit == 0.2:
                        satisfied[index] = True
                        # -- truthPit = val[i]
                    elif val[i] in frontier:
                        j = frontier.index(val[i]) # get the index of the frontier pit
                        if Pfrontier[j] == 0.2:
                            satisfied[index] = True
                            # -- truthPit = val[i]
            # if a breeze in the set of breezes is not satisfied
            if satisfied[index] is False:
                # -- print('breeze ' + str(key) + ' is FALSE :: return 0')
                return 0
            # -- print('P(breeze = {} | {} ) is TRUE '.format(key,truthPit))
            index += 1

        return 1


    # HW9
    # calculate distribution probability of a pit using
    # P( Pit | breeze, known) = P(pit)E_frontier[P(breeze|pit, known, frontier)P(frontier)]
    def DistProbPit(self, pit, frontier, breezes):
        pTrueSum = 0.0
        pNotSum = 0.0
        frontierPerms = self.GetFrontierPermutations(frontier)
        # print('frontier perms:', frontierPerms)
        # calculate product of every permutation of frontier pit probabilites
        products = []
        for perm in frontierPerms:
            prod = 1.0
            for val in perm:
                prod *= val
            products.append(round(prod, 4))
            # print('perm = {}, product={}'.format(perm,product))
        # -- print('products', products)

        for i in range(len(products)):
            if i < (len(products)-1):
                # P(~pit)E_frontierP(breeze|~pit, known, frontier)P(frontier)
                pNotSum += (0.8)*self.BreezeProb(pit, frontier, 0.8, frontierPerms[i], breezes)*products[i]
            # P(pit)E_frontierP(breeze|pit, known, frontier)P(frontier)
            pTrueSum += (0.2)*self.BreezeProb(pit, frontier, 0.2, frontierPerms[i], breezes)*products[i]

        # -- print('PTrueSum:', round(pTrueSum,3))
        # -- print('PNotSum:', round(pNotSum,3))
        return [round(pTrueSum, 3),round(pNotSum, 3)]

    # HW5
    #
    # Update possible wumpus locations based on the current set of stench locations
    # and clear locations.
    #
    def UpdatePossibleWumpusLocations(self):
        self.possibleWumpusLocations = []
        # Determine possible wumpus locations consistent with available stench information
        for location1 in self.stenchLocations:
            # Build list of adjacent locations to this stench location
            adjacentLocations = []
            self.AddAdjacentLocations(adjacentLocations, location1)
            if (not self.possibleWumpusLocations):
                # Must be first stench location in list, so add all adjacent locations
                self.possibleWumpusLocations = adjacentLocations
            else:
                # Eliminate possible wumpus locations not adjacent to this stench location
                tmpLocations = self.possibleWumpusLocations
                self.possibleWumpusLocations = []
                for location2 in tmpLocations:
                    if (location2 in adjacentLocations):
                        self.possibleWumpusLocations.append(location2)
        # Eliminate possible wumpus locations adjacent to a clear location
        for location1 in self.clearLocations:
            # Build list of adjacent locations to this clear location
            adjacentLocations = []
            self.AddAdjacentLocations(adjacentLocations, location1)
            tmpLocations = self.possibleWumpusLocations
            self.possibleWumpusLocations = []
            for location2 in tmpLocations:
                if (location2 not in adjacentLocations):
                    self.possibleWumpusLocations.append(location2)

        # ensure that no potential wumpus location is a safe location
        self.possibleWumpusLocations = [x for x in self.possibleWumpusLocations if x not in self.safeLocations]

    # HW5
    #
    # Returns location resulting in a successful GOFORWARD.
    # Replaced Move() method from HW2.
    #
    def GetGoForward(self):
        X = self.worldState.agentLocation[0]
        Y = self.worldState.agentLocation[1]
        if (self.worldState.agentOrientation == Orientation.RIGHT):
            X = X + 1
        if (self.worldState.agentOrientation == Orientation.UP):
            Y = Y + 1
        if (self.worldState.agentOrientation == Orientation.LEFT):
            X  = X - 1
        if (self.worldState.agentOrientation == Orientation.DOWN):
            Y = Y - 1
        return [X,Y]
    
    # HW5
    #
    # Add given location to agent's pathToGold. But if this location is already on the
    # pathToGold, then remove everything after the first occurrence of this location.
    #
    def AddToPath(self, location):
        if (location in self.pathToGold):
            index = self.pathToGold.index(location)
            self.pathToGold = self.pathToGold[:index]
        self.pathToGold.append(location)
    
    # HW9/HW5
    #
    # Choose and return an action when we haven't found the gold yet.
    # Handle special case where we start out in (1,1), perceive a stench, and
    # don't know the wumpus location. In this case, SHOOT. Orientation will be
    # RIGHT, so if SCREAM, then wumpus in (2,1); otherwise in (1,2). This is
    # handled in the UpdateState method.
    #
    def ChooseAction(self, percept):
        forwardLocation = self.GetGoForward()
        if (percept['Stench'] and self.worldState.agentHasArrow):
            action = Action.SHOOT
        elif(percept['Breeze'] and self.worldState.agentLocation == [1,1]):
            # HW9 :: breeze in 1,1
            # both directions are unknown
            if [2,1] not in knownPits and [1,2] not in knownPits:
                action = Action.GOFORWARD
            elif forwardLocation in knownPits:
                action = randint(1,2) # random turn
            else:
                if self.previousAction == Action.GOFORWARD:
                    action = randint(1,2) # random turn so you don't continusouly keep going into wall
                else:
                    action = Action.GOFORWARD # in a new orientation so turn
            
        elif ((forwardLocation in self.safeLocations) and (forwardLocation not in self.visitedLocations)):
            # If happen to be facing safe unvisited location, then move there
            action = Action.GOFORWARD
        else:
            # Choose randomly from GOFORWARD, TURNLEFT, and TURNRIGHT, but don't
            # GOFORWARD into a possible wumpus location or a wall
            if ((forwardLocation in self.possibleWumpusLocations or self.OutsideWorld(forwardLocation)) 
                or (self.PitBounds(forwardLocation) and self.pitLocations[forwardLocation[0]-1][forwardLocation[1]-1] > 0.50)): # HW9
                    action = randint(1,2) # TURNLEFT, TURNRIGHT
            else:
                action = randint(0,2) # GOFORWARD, TURNLEFT, TURNRIGHT
            if ((percept['Stench']) and (forwardLocation in self.noPitLocs) and (self.worldState.agentHasArrow)):
                # HW9
                # If agent is not in [1,1] and there is no possible safe location to move due to a stench
                # If the agent is facing a location where we know there is no pit, but might be wumpus
                # Then the agent will shoot it's arrow  
                # (e.g pit(3,1) and stench(1,2) and breeze=(2,1) and visited=(1,1),(2,1),(1,2)) => safeLocations=(1,1), (2,1), (1,2) and noPitLocs=(2,2), (1,3)
                if forwardLocation not in self.safeLocations:
                    action = Action.SHOOT
                else: 
                    action = randint(0,2) # GOFORWARD, TURNLEFT, TURNRIGHT
        return action
    
    # HW5
    #
    # Add a sequence of actions to actionList that moves the agent along the
    # pathToGold if forward=true, or the reverse if forward=false. Assumes at
    # least one location is on pathToGold.
    #
    def AddActionsFromPath(self, forward):
        path = list(self.pathToGold)
        if (not forward):
            path = list(reversed(path))
        currentLocation = self.worldState.agentLocation
        currentOrientation = self.worldState.agentOrientation
        for nextLocation in path[1:]:
            if (nextLocation[0] > currentLocation[0]):
                nextOrientation = Orientation.RIGHT
            if (nextLocation[0] < currentLocation[0]):
                nextOrientation = Orientation.LEFT
            if (nextLocation[1] > currentLocation[1]):
                nextOrientation = Orientation.UP
            if (nextLocation[1] < currentLocation[1]):
                nextOrientation = Orientation.DOWN
            # Find shortest turn sequence (assuming RIGHT=0, UP=1, LEFT=2, DOWN=3)
            diff = (currentOrientation - nextOrientation)
            if ((diff == 1) or (diff == -3)):
                self.actionList.append(Action.TURNRIGHT)
            else:
                if (diff != 0):
                    self.actionList.append(Action.TURNLEFT)
                if ((diff == 2) or (diff == -2)):
                    self.actionList.append(Action.TURNLEFT)
            self.actionList.append(Action.GOFORWARD)
            currentLocation = nextLocation
            currentOrientation = nextOrientation
    
    # HW5
    #
    # Add location to given list, if not already present.
    #
    def AddNewLocation(self, locationList, location):
        if (location not in locationList):
            locationList.append(location)
    
    # HW5
    #
    # Add locations that are adjacent to the given location to the given location list.
    # Doesn't add locations outside the left and bottom borders of the world, but might
    # add locations outside the top and right borders of the world, if we don't know the
    # world size.
    #
    def AddAdjacentLocations(self, locationList, location):
        worldSize = self.worldState.worldSize
        if ((worldSize == 0) or (location[1] < worldSize)):
            self.AddNewLocation(locationList, [location[0], location[1] + 1]) # up
        if ((worldSize == 0) or (location[0] < worldSize)):
            self.AddNewLocation(locationList, [location[0] + 1, location[1]]) # right
        if (location[0] > 1):
            self.AddNewLocation(locationList, [location[0] - 1, location[1]]) # left
        if (location[1] > 1):
            self.AddNewLocation(locationList, [location[0], location[1] - 1]) # down
    
    # HW5
    #
    # Return true if given location is outside known world.
    #
    def OutsideWorld(self, location):
        worldSize = self.worldState.worldSize
        if ((location[0] < 1) or (location[0] < 1)):
            return True
        if ((worldSize > 0) and ((location[0] > worldSize) or (location[1] > worldSize))):
            return True
        return False
    
    # HW5
    #
    # Filters from safeLocations any locations that are outside the upper or right borders of the world.
    #
    def FilterSafeLocations(self):
        worldSize = self.worldState.worldSize
        tmpLocations = list(self.safeLocations)
        self.safeLocations = []
        for location in tmpLocations:
            if ((location[0] < 1) or (location[1] < 1)):
                continue
            if ((worldSize > 0) and ((location[0] > worldSize) or (location[1] > worldSize))):
                continue
            self.safeLocations.append(location)
    
    # HW5
    def Output(self):
        print("World Size: "+ str(self.worldState.worldSize))
        print("Visited Locations: " + str(self.visitedLocations))
        print("Safe Locations: " + str(self.safeLocations))
        print("Breeze Locations: " + str(self.breezeLocations))
        print("Possible Wumpus Locations: " + str(self.possibleWumpusLocations))
        print("Gold Location: " + str(self.worldState.goldLocation))
        print("Path To Gold: " + str(self.pathToGold))
        actionStrList = []
        for action in self.actionList:
            if action == Action.GOFORWARD:
                actionStrList.append('GOFORWARD')
            elif action == Action.TURNLEFT:
                actionStrList.append('TURNLEFT')
            elif action == Action.TURNRIGHT:
                actionStrList.append('TURNRIGHT')
            elif action == Action.GRAB:
                actionStrList.append('GRAB')
            elif action == Action.SHOOT:
                actionStrList.append('SHOOT')
            else:
                actionStrList.append('CLIMB')
        print("Action List: " + str(actionStrList))
        print('NOT PITS: ' + str(self.noPitLocs))
        print("")


# Global agent
myAgent = 0
knownPits = []
def PyAgent_Constructor ():
    print("PyAgent_Constructor")
    global myAgent, knownPits
    myAgent = Agent()
    # knownPits = []

def PyAgent_Destructor ():
    print("PyAgent_Destructor")

def PyAgent_Initialize ():
    print("PyAgent_Initialize")
    global myAgent, knownPits
    myAgent.Initialize()
    print(knownPits)
    myAgent.PopulateKnownPits(knownPits)

def PyAgent_Process (stench,breeze,glitter,bump,scream):
    global myAgent
    percept = {'Stench': bool(stench), 'Breeze': bool(breeze), 'Glitter': bool(glitter), 'Bump': bool(bump), 'Scream': bool(scream)}
    #print "PyAgent_Process: percept = " + str(percept)
    return myAgent.Process(percept)

def PyAgent_GameOver (score):
    global myAgent, knownPits
    print("PyAgent_GameOver: score = " + str(score))
    # keep track of known pits for trials
    if myAgent.GetGoForward() not in knownPits and myAgent.GetGoForward() != [1,0]:
        knownPits.append(myAgent.GetGoForward())
    print('KNOWN PITS:', knownPits)
    myAgent.GameOver(score) # HW5

