from flask import Flask, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, send, join_room, leave_room, emit

from piece import Piece
from board import Board

# pieces = []
# board = Board(pieces)
# board.board = board.loadFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
game = {}

def updateBoard(move, fen):
    pieces = []
    board = Board(pieces)
    board.board, color = board.loadFen(fen)
    # print(color)
    x = board.makeMove(color, move)
    if x != "invalid move":
        if color == "White":
            color = "Black"
        else:
            color = "White"
    newfen = board.getFen(color)
    fen = newfen
    return x, newfen


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins = "*")

@app.route("/")
def home():
    return render_template("loadscreen.html")

@app.route("/templates/index.html")
def index():
    return render_template("index.html")

@app.route("/test")
def test():
    return render_template("index.html")

@socketio.on('message')
def handle_message(data):
    pass

@socketio.on("switchScreen")
def switchScreen():
    print("ran")
    return render_template("index.html")

@socketio.on("makemove")
def makemove(gameCode, data):
    print(request.sid)
    if data[6] == "x":
        move = data[0:6]
        fen = data[6:]
    else:
        move = data[0:5]
        fen = data[5:]
    print(move, fen)
    x, newfen = updateBoard(move, fen)
    print(fen[-5:])
    if game[gameCode][0] == request.sid and fen[-5:] != "White":
        x = "F"
    
    if game[gameCode][1] == request.sid and fen[-5:] != "Black":
        x = "F"
    
    output = x + newfen
    emit("makemove", output, room = game[gameCode][0])
    emit("makemove", output, room = game[gameCode][1])


@socketio.on("createGame")
def createGame(code):
    game[code] = [request.sid]
    print(game)

@socketio.on("playerJoin")
def playerJoin(code):
    print("second player joined")
    emit("playerJoin", room = game[gameCode][0])

@socketio.on("joinGame")
def joinGame(code):
    game[code].append(request.sid)
    emit("playerJoin", room = game[code][0])
    print(game)

@socketio.on("checkCode")
def checkCode(code):
    if code in game:
        if len(game[code]) == 1:
            emit("checkCode", True)
        else:
            emit("checkCode", False)
    else:
        emit("checkCode", False)

# @app.route('/')
# def hello_world():
#     return render_template('Hello, World!')

# @app.route("/get_moves", methods = ["GET"])
# def get_moves():
#     # print(allMoves)
#     return "success"
#     # if request.method == "POST":
#     #     return request.form['start'] + request.form['end']

# @app.route("/make_move", methods = ["POST"])
# def make_move():
#     if request.method == "POST":
#         data = str(request.data)
#         if data[6] == "x":
#             move = data[3:9]
#             fen = data[9:-2]
#         else:
#             move = data[3:8]
#             fen = data[8:-2]
#         x, newfen = updateBoard(move, fen)
#         output = x + newfen
#         return output

# @app.route("/create_game", methods = ["GET"])
# def create_game():
#     pass







if __name__ == '__main__':
    socketio.run(app)

# if __name__ == "__main__":
#     app.run(debug=True)
