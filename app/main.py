import bottle
import json

global GAME_ID, WIDTH, HEIGHT, SNAKE_NAME, SNAKE_COLOR, SNAKE_TAUNT, TURN, LIFE, HEAD_URL
HEAD_URL = "http://i.imgur.com/T9Rw249.jpg"
SNAKE_NAME = "MarJo"
SNAKE_COLOR = "#221E1D"
SNAKE_TAUNT = "taunt"
LIFE = 100

def checkAround(pOurSnake, pBoard):
    coords = pOurSnake["coords"]
    headX, headY = coords[0]

    prevX, prevY = coords[1]

    if pBoard[headX + 1][headY]["state"] == "food":
        return "right" 
    elif pBoard[headX - 1][headY]["state"] == "food":
        return "left"
    elif pBoard[headX][headY + 1]["state"] == "food":
        return "up"
    elif pBoard[headX][headY -1]["state"] == "food":
        return "down"
    else:
        return "up"

def moveChoice(pOurSnake, pBoard, pSnakes, pFood):
    global WIDTH, HEIGHT, TURN, SNAKE_NAME, LIFE
    print "Where the magic is going to happen"


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