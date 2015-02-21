import bottle
import json

from heapq import heappush, heappop # for priority queue
import math
import time
import random

global GAME_ID, WIDTH, HEIGHT, SNAKE_NAME, SNAKE_COLOR, SNAKE_TAUNT, TURN, LIFE, HEAD_URL
HEAD_URL = "http://i.imgur.com/T9Rw249.jpg"
SNAKE_NAME = "MarJo"
SNAKE_COLOR = "#221E1D"
SNAKE_TAUNT = "taunt"
LIFE = 100


# ADDED CODE --------------
class node:
    xPos = 0 # x position
    yPos = 0 # y position
    distance = 0 # total distance already travelled to reach the node
    priority = 0 # priority = distance + remaining distance estimate
    def __init__(self, xPos, yPos, distance, priority):
        self.xPos = xPos
        self.yPos = yPos
        self.distance = distance
        self.priority = priority
    def __lt__(self, other): # comparison method for priority queue
        return self.priority < other.priority
    def updatePriority(self, xDest, yDest):
        self.priority = self.distance + self.estimate(xDest, yDest) * 10 # A*
    # give higher priority to going straight instead of diagonally
    def nextMove(self, dirs, d): # d: direction to move
        if dirs == 8 and d % 2 != 0:
            self.distance += 14
        else:
            self.distance += 10
    # Estimation function for the remaining distance to the goal.
    def estimate(self, xDest, yDest):
        xd = xDest - self.xPos
        yd = yDest - self.yPos
        # Euclidian Distance
        d = math.sqrt(xd * xd + yd * yd)
        # Manhattan distance
        # d = abs(xd) + abs(yd)
        # Chebyshev distance
        # d = max(abs(xd), abs(yd))
        return(d)

# A-star algorithm.
# The path returned will be a string of digits of directions.
def pathFind(the_map, n, m, dirs, dx, dy, xA, yA, xB, yB):
    closed_nodes_map = [] # map of closed (tried-out) nodes
    open_nodes_map = [] # map of open (not-yet-tried) nodes
    dir_map = [] # map of dirs
    row = [0] * n
    for i in range(m): # create 2d arrays
        closed_nodes_map.append(list(row))
        open_nodes_map.append(list(row))
        dir_map.append(list(row))

    pq = [[], []] # priority queues of open (not-yet-tried) nodes
    pqi = 0 # priority queue index
    # create the start node and push into list of open nodes
    n0 = node(xA, yA, 0, 0)
    n0.updatePriority(xB, yB)
    heappush(pq[pqi], n0)
    open_nodes_map[yA][xA] = n0.priority # mark it on the open nodes map

    # A* search
    while len(pq[pqi]) > 0:
        # get the current node w/ the highest priority
        # from the list of open nodes
        n1 = pq[pqi][0] # top node
        n0 = node(n1.xPos, n1.yPos, n1.distance, n1.priority)
        x = n0.xPos
        y = n0.yPos
        heappop(pq[pqi]) # remove the node from the open list
        open_nodes_map[y][x] = 0
        closed_nodes_map[y][x] = 1 # mark it on the closed nodes map

        # quit searching when the goal is reached
        # if n0.estimate(xB, yB) == 0:
        if x == xB and y == yB:
            # generate the path from finish to start
            # by following the dirs
            path = ''
            while not (x == xA and y == yA):
                j = dir_map[y][x]
                c = str((j + dirs / 2) % dirs)
                path = c + path
                x += dx[j]
                y += dy[j]
            return path

        # generate moves (child nodes) in all possible dirs
        for i in range(dirs):
            xdx = x + dx[i]
            ydy = y + dy[i]
            if not (xdx < 0 or xdx > n-1 or ydy < 0 or ydy > m - 1
                    or the_map[ydy][xdx] == 1 or closed_nodes_map[ydy][xdx] == 1):
                # generate a child node
                m0 = node(xdx, ydy, n0.distance, n0.priority)
                m0.nextMove(dirs, i)
                m0.updatePriority(xB, yB)
                # if it is not in the open list then add into that
                if open_nodes_map[ydy][xdx] == 0:
                    open_nodes_map[ydy][xdx] = m0.priority
                    heappush(pq[pqi], m0)
                    # mark its parent node direction
                    dir_map[ydy][xdx] = (i + dirs / 2) % dirs
                elif open_nodes_map[ydy][xdx] > m0.priority:
                    # update the priority
                    open_nodes_map[ydy][xdx] = m0.priority
                    # update the parent direction
                    dir_map[ydy][xdx] = (i + dirs / 2) % dirs
                    # replace the node
                    # by emptying one pq to the other one
                    # except the node to be replaced will be ignored
                    # and the new node will be pushed in instead
                    while not (pq[pqi][0].xPos == xdx and pq[pqi][0].yPos == ydy):
                        heappush(pq[1 - pqi], pq[pqi][0])
                        heappop(pq[pqi])
                    heappop(pq[pqi]) # remove the target node
                    # empty the larger size priority queue to the smaller one
                    if len(pq[pqi]) > len(pq[1 - pqi]):
                        pqi = 1 - pqi
                    while len(pq[pqi]) > 0:
                        heappush(pq[1-pqi], pq[pqi][0])
                        heappop(pq[pqi])       
                    pqi = 1 - pqi
                    heappush(pq[pqi], m0) # add the better node instead
    return '' # if no route found


# ADDED CODE --------------

def checkAround(pOurSnake, pBoard):
    snakeCoords = pOurSnake["coords"]
    foodCoords = pBoard["food"]
    print "check around food coords:"
    print foodCoords
    closestFoodX, closestFoodY = foodCoords[0]
    snakeHeadX, snakeHeadY = snakeCoords[0]

    closestFoodDistance = abs(snakeHeadX - closestFoodX) + abs(snakeHeadY - closestFoodY)

    for foodPos in foodCoords:
        foodX, foodY = foodPos
        tempFoodDistance = abs(snakeHeadX - foodX) + abs(snakeHeadY - foodY)

        if (tempFoodDistance < closestFoodDistance):
            closestFoodDistance = tempFoodDistance
            closestFoodX = foodX
            closestFoodY = foodY


    prevX, prevY = snakeCoords[1]

    if pBoard[snakeHeadX + 1][snakeHeadY]["state"] == "food":
        return "right" 
    elif pBoard[snakeHeadX - 1][snakeHeadY]["state"] == "food":
        return "left"
    elif pBoard[snakeHeadX][snakeHeadY + 1]["state"] == "food":
        return "up"
    elif pBoard[snakeHeadX][snakeHeadY -1]["state"] == "food":
        return "down"
    else:
        return "up"

def moveChoice(pOurSnake, pBoardTest, pSnakes, pFood):
    global WIDTH, HEIGHT, TURN, SNAKE_NAME, LIFE

    data = bottle.request.json


    snakeCoords = pOurSnake["coords"]
    foodCoords = pFood #pBoardTest["food"]
    print "moveChoice food coords"
    print foodCoords
    closestFoodX, closestFoodY = foodCoords[0]
    snakeHeadX, snakeHeadY = snakeCoords[0]

    closestFoodDistance = abs(snakeHeadX - closestFoodX) + abs(snakeHeadY - closestFoodY)

    for foodPos in foodCoords:
        foodX, foodY = foodPos
        tempFoodDistance = abs(snakeHeadX - foodX) + abs(snakeHeadY - foodY)

        if (tempFoodDistance < closestFoodDistance):
            closestFoodDistance = tempFoodDistance
            closestFoodX = foodX
            closestFoodY = foodY

    dirs = 4 # number of possible directions to move on the map
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]

    n = data["width"] # horizontal size of the map
    m = data["height"] # vertical size of the map
    the_map = []
    row = [0] * n
    for i in range(m): # create empty map
        the_map.append(list(row))
    for i in range(len(the_map)):
        print(the_map[i])

    #fill map with obsticles
    for x in range(0, n):
        for y in range(0, m):
            if(data["board"][x][y] == "head" or data["board"][x][y] == "body"):
                the_map[y][x] = 1

    #position of the snake head and the closest food
    snaketofood = (snakeHeadX, snakeHeadY, closestFoodX, closestFoodY)

    (xA, yA, xB, yB) = snaketofood

    print 'Map size (X,Y): ', n, m
    print 'Start: ', xA, yA
    print 'Finish: ', xB, yB
    t = time.time()
    route = pathFind(the_map, n, m, dirs, dx, dy, xA, yA, xB, yB)
    print 'Time to generate the route (seconds): ', time.time() - t
    print 'Route:'
    print route

    # mark the route on the map
    if len(route) > 0:
        x = xA
        y = yA
        the_map[y][x] = 2
        for i in range(len(route)):
            j = int(route[i])
            x += dx[j]
            y += dy[j]
            the_map[y][x] = 3
        the_map[y][x] = 4

    # display the map with the route added
    print 'Map:'
    for y in range(m):
        for x in range(n):
            xy = the_map[y][x]
            if xy == 0:
                print '.', # space
            elif xy == 1:
                print 'O', # obstacle
            elif xy == 2:
                print 'S', # start
            elif xy == 3:
                print 'R', # route
            elif xy == 4:
                print 'F', # finish
        print

        return "left"

def getOurSnake(pData):
    global SNAKE_NAME
    for snake in pData["snakes"]:
        if snake["name"] == SNAKE_NAME:
            return snake

@bottle.get('/')
def index():
    return """
        <a href="https://github.com/marclave/battlesnake-python">
            ya-boi-battlesnake-python
        </a>
    """


@bottle.post('/start')
def start():
    global GAME_ID, WIDTH, HEIGHT
    data = bottle.request.json

    GAME_ID = data["game_id"] # TODO marc: check this
    WIDTH = data["width"]
    HEIGHT = data["height"]

    return json.dumps({
        'name': SNAKE_NAME,
        'color': SNAKE_COLOR,
        'head_url': HEAD_URL,
        'taunt': SNAKE_TAUNT
    })


@bottle.post('/move')
def move():
    global GAME_ID, WIDTH, HEIGHT, TURN, SNAKE_NAME
    data = bottle.request.json

    TURN = data["turn"]
    snakesObjects = data["snakes"]
    foodObject = data["food"]
    boardObject = data["board"]

    for obj in foodObject:
        print obj

    ourSnakeObject = getOurSnake(data)

    moveDirection = moveChoice(ourSnakeObject, boardObject, snakesObjects, foodObject)
    moveTestDirection = checkAround(ourSnakeObject, boardObject)

    return json.dumps({
        'move': moveTestDirection,
        'taunt': SNAKE_TAUNT
    })


@bottle.post('/end')
def end():
    data = bottle.request.json

    return json.dumps({})


# Expose WSGI app
application = bottle.default_app()