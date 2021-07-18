from flask import Flask, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, send, join_room, leave_room, emit

from piece import Piece
from board import Board
from stockfish import Stockfish


# pieces = []
# board = Board(pieces)
# board.board = board.loadFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
game = {}

def updateBoard(fen):
    pieces = []
    board = Board(pieces)
    board.board, xcolor = board.loadFen(fen)
    
    allMoves = board.allMoves(xcolor, fen)
    movedict = {}
    for move in allMoves[0]:
        newboard = Board(pieces)
        newboard.board, color = newboard.loadFen(fen)
        x = newboard.makeMove(color, move, fen, allMoves[1], allMoves[2], allMoves[3])
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
            if move[0] == "P" or move[3] == "x":
                holderfen[4] = "0"
            else:
                holderfen[4] = str(int(holderfen[4]) + 1)
            if xcolor == "Black":
                holderfen[5] = str(int(holderfen[5]) + 1)

            x = "T"

        newfen = holderfen[0] + " " + color + " " + holderfen[2] + " " + holderfen[3] + " " + holderfen[4] + " " + holderfen[5]
        movedict[move] = newfen
    if not movedict:

        if board.checkmateChecker(xcolor, board.board):
            movedict = "checkmate"
        else:
            movedict = "stalemate"
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
    movedict = updateBoard("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR White KQkq - 0 1")
    emit("initialMoves", movedict)

@socketio.on("chatmessage")
def chatmessage(code,msg):
    if game[code][0] == request.sid:
        emit("chatmessage", msg, room = game[code][1])
    else:
        emit("chatmessage", msg, room = game[code][0])

@socketio.on("switchScreen")
def switchScreen():
    return render_template("index.html")

@socketio.on("makemove")
def makemove(gameCode, fen):
    
    # holder = fen.split()
    if gameCode[0:3] != "CPU":
        movedict = updateBoard(" ".join(fen.split()[1:]))
        if game[gameCode][0] == request.sid:
            emit("oppoMove", movedict, room = game[gameCode][1])
            emit("updatedFen", fen, room = game[gameCode][1])
        if game[gameCode][1] == request.sid:
            emit("oppoMove", movedict, room = game[gameCode][0])
            emit("updatedFen", fen, room = game[gameCode][0])
    else:
        send("before stockfish instantiation")
        stockfish = Stockfish(r"stockfish_14_win_x64_avx2\stockfish_14_x64_avx2.exe")
        send("after stockfish instantiation")

        fen = mine2stockfish(" ".join(fen.split()[1:]))
        send("after fen conversion")

        stockfish.set_fen_position(fen)
        send("after setting fen")

        bestmove = stockfish.get_best_move()
        send("after getting best move")

        stockfish.make_moves_from_current_position([bestmove])
        send("making move")

        newfen = bestmove + " " + stockfish2mine(stockfish.get_fen_position())
        

        movedict = updateBoard(" ".join(newfen.split()[1:]))
        emit("oppoMove", movedict, room = game[gameCode][0])
        emit("updatedFen", newfen, room = game[gameCode][0])


def stockfish2mine(fen):
    placeholder = fen.split()
    if placeholder[1] == "w":
        placeholder[1] ="White"
    else:
        placeholder[1] = "Black"
    castling = ["K", "Q", "k", "q"]
    for castle in castling:
        if castle not in placeholder[2]:
            placeholder[2] += "-"
    columns = "abcdefgh"
    if placeholder[3] != "-":
        col = placeholder[3][0]
        newcol = columns.find(col) + 1
        placeholder[3] = newcol + placeholder[3][1]
    fen = " ".join(placeholder)
    return fen

def mine2stockfish(fen):
    placeholder = fen.split()
    if placeholder[1] == "White":
        placeholder[1] = "w"
    else:
        placeholder[1] = "b"
    x = ""
    for char in placeholder[2]:
        if char != "-":
            x += char
    placeholder[2] = x
    columns = "abcdefgh"
    if placeholder[3] != "-":
        col = placeholder[3][0]
        newcol = columns[int(col)-1]
        row = placeholder[3][1]
        placeholder[3] = newcol + row
    
    fen = " ".join(placeholder)
    return fen

@socketio.on("createGame")
def createGame(code):
    if code[0:3] != "CPU":
        game[code] = [request.sid]
        print(game)
    else:
        game[code] = [request.sid, "CPU"]
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

@socketio.on("gameOver")
def gameOver(code, ending):
    emit("gameOver", ending, room = game[code][0])
    emit("gameOver", ending, room = game[code][1])

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
