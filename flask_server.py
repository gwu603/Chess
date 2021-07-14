from flask import Flask, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, send, join_room, leave_room, emit

from piece import Piece
from board import Board

# pieces = []
# board = Board(pieces)
# board.board = board.loadFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
game = {}

def updateBoard(fen):
    pieces = []
    board = Board(pieces)
    board.board, color = board.loadFen(fen)
    
    allMoves = board.allMoves(color, fen)
    movedict = {}
    for move in allMoves:
        newboard = Board(pieces)
        newboard.board, color = newboard.loadFen(fen)
        x = newboard.makeMove(color, move, fen)
        if x != "F":
            if color == "White":
                color = "Black"
            else:
                color = "White"
        

        newfen = newboard.getFen(fen)
        holderfen = newfen.split()

        if x != "F":

            if x == "xKside":
                holderfen[2] = "-" + holderfen[2][1:]
            elif x == "xQside":
                holderfen[2] = holderfen[2][0] + "-" + holderfen[2][2:]
            elif x == "xkside":
                holderfen[2] = holderfen[2][:2] + "-" + holderfen[2][3]
            elif x == "xqside":
                holderfen[2] = holderfen[2][:3] + "-"
            elif x == "xK":
                holderfen[2] = "--" + holderfen[2][2:]
            elif x == "xk":
                holderfen[2] = holderfen[2][:2] + "--"
            else:
                holderfen[3] = x
            if move[0] != "P" or abs(int(move[2])-int(move[-1])) != 2:
                holderfen[3] = "-"
            x = "T"

        newfen = holderfen[0] + " " + color + " " + holderfen[2] + " " + holderfen[3]
        movedict[move] = newfen

    return movedict


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins = "*")

@app.route("/")
def home():
    return render_template("loadscreen.html")

@app.route("/test")
def test():
    return render_template("index.html")

@app.route("/activegames")
def activegames():
    return str(game)


@socketio.on('message')
def handle_message(data):
    print(data)

@socketio.on("initialMoves")
def initialmoves():
    movedict = updateBoard("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR White KQkq -")
    emit("initialMoves", movedict)

@socketio.on("switchScreen")
def switchScreen():
    return render_template("index.html")

@socketio.on("makemove")
def makemove(gameCode, fen):
    

    movedict = updateBoard(fen)
    # holder = fen.split()



    if game[gameCode][0] == request.sid:
        emit("oppoMove", movedict, room = game[gameCode][1])
        emit("updatedFen", fen, room = game[gameCode][1])
    if game[gameCode][1] == request.sid:
        emit("oppoMove", movedict, room = game[gameCode][0])
        emit("updatedFen", fen, room = game[gameCode][0])

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
