from flask_cors import CORS
from flask import Flask, render_template, session, request, jsonify
from flask_login import LoginManager, UserMixin, current_user, login_user, \
    logout_user
from flask_session import Session
from flask_socketio import SocketIO, send, emit


from piece import Piece
from board import Board
from stockfish import Stockfish

# from flask_sqlalchemy import SQLAlchemy




app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///C:\Users\yiqin\Desktop\Chess Project\test.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
# db2 = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'top-secret!'
app.config['SESSION_TYPE'] = 'filesystem'
login = LoginManager(app)
Session(app)
socketio = SocketIO(app, cors_allowed_origins = "*", manage_session = False)


sessions = {}


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

def updateBoard(fen):
    board = Board()
    board.board, xcolor = board.loadFen(fen)
    
    allMoves = board.allMoves(xcolor, fen)
    movedict = {}
    for move in allMoves[0]:
        newboard = Board()
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
    gameOver = ""
    if not movedict:

        if board.checkmateChecker(xcolor, board.board):
            gameOver = "checkmate"
        else:
            gameOver = "stalemate"
    return movedict, gameOver


class User(UserMixin, object):
    def __init__(self, id=None):
        self.id = id

@login.user_loader
def load_user(id):
    return User(id)

# class Games(db2.Model):
#     id = db2.Column(db.Integer, primary_key=True)
#     players = db2.Column(db.String(80), unique=True, nullable=False)
#     moves = db2.Column(db.String(80), unique=True, nullable=False)
#     fens = db2.Column(db.String(120), unique=True, nullable=False)

#     def __repr__(self):
#         return str(self.id) + " " + self.moves + " " + self.fens


gameInfo = {}
client = {}
gameFens = {}
gameMoves = {}
posMoves = {}
chatHistory = {}

@app.route("/")
def home():
    session.permanent = False;
    return render_template("loadscreen.html")

@app.route("/test")
def test():
    session.permanent = False;
    return render_template("index.html")

@app.route("/activegames")
def activegames():
    return str(gameInfo)


@socketio.on("get-data")
def get_data(code):
    twoplayer = False
    if code in gameInfo:
        if len(gameInfo[code]) > 1:
            twoplayer = True
    emit("posMoves", posMoves[code])
    emit("set-data", {"twoplayer": twoplayer, "pastFens":gameFens[code], "pastMoves":gameMoves[code], "chatHistory":chatHistory[code]})
    # print(gameFens[code])
# @socketio.on('disconnect')
# def test_disconnect():
#     if len(game[client[request.sid]]) <= 1:
#         del game[client[request.sid]]
#     elif game[client[request.sid]][0] == request.sid:
#         game[client[request.sid]].remove(0)
#     else:
#         game[client[request.sid]].remove(1)
#     print('Client disconnected')


@socketio.on('message')
def handle_message(data):
    print(data)

# @socketio.on("initialMoves")
# def initialmoves():
#     sessions[session.sid] = request.sid
#     movedict = updateBoard("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR White KQkq - 0 1")
#     emit("set-data", {"twoplayer":twoplayer, "posmoves": posMoves[code], "pastmoves":gameMoves[code]})

@socketio.on("chatmessage")
def chatmessage(data):
    sessions[session.sid] = request.sid
    code = data["gameCode"]
    chatHistory[code] = data["chatHistory"]
    if sessions[gameInfo[code][0]] == request.sid:
        emit("chatmessage", chatHistory[code], room = sessions[gameInfo[code][1]])
    else:
        emit("chatmessage", chatHistory[code], room = sessions[gameInfo[code][0]])

@socketio.on("switchScreen")
def switchScreen():
    return render_template("index.html")

@socketio.on("makemove")
def makemove(data):
    sessions[session.sid] = request.sid
    code = data["gameCode"]
    fen = data["fen"]
    move = data["move"]
    gameMoves[code].append(move)
    gameFens[code].append(fen)

    board = Board()
    board.board, xcolor = board.loadFen(fen)

    if board.checkChecker(xcolor, board.board):
        emit("check", xcolor, room = sessions[gameInfo[code][1]])
        emit("check", xcolor, room = sessions[gameInfo[code][0]])

    # holder = fen.split()
    posMoves[code] = updateBoard(fen)

    if code[0:3] != "CPU":
        movedict, gameOver = updateBoard(fen)

        if len(gameOver) > 1:
            emit("gameOver", gameOver, room = sessions[gameInfo[code][1]])
            emit("gameOver", gameOver, room = sessions[gameInfo[code][0]])

        if gameInfo[code][0] == session.sid:
            emit("oppoMove", {"gameOver":gameOver, "move":move, "fen":fen}, room = sessions[gameInfo[code][1]])
            emit("posMoves", posMoves[code], room = sessions[gameInfo[code][1]] )

        if gameInfo[code][1] == session.sid:
            emit("oppoMove", {"gameOver":gameOver, "move":move, "fen":fen}, room = sessions[gameInfo[code][0]])
            emit("posMoves", posMoves[code], room = sessions[gameInfo[code][0]])

    # else:

    #     pieces = []
    #     board = Board(pieces)

    #     board.board, xcolor = board.loadFen(" ".join(fen.split()[1:]))

    #     cols = "abcdefgh"

    #     stockfish = Stockfish(r"stockfish_14_win_x64_avx2\stockfish_14_x64_avx2.exe")
    #     fen = mine2stockfish(" ".join(fen.split()[1:]))
    #     stockfish.set_fen_position(fen)
    #     bestmove = stockfish.get_best_move()
    #     stockfish.make_moves_from_current_position([bestmove])
    #     # send("making move")
    #     startcol = int(cols.find(bestmove[0]))+1
    #     endcol = int(cols.find(bestmove[2]))+1

    #     extra = ""
    #     if board.board[int(bestmove[3])-1][endcol-1].name != ".":
    #         extra = "x"

    #     newbestmove = board.board[int(bestmove[1])-1][startcol-1].name + str(startcol) + str(bestmove[1]) + extra + str(endcol) + str(bestmove[3]) 
    #     newfen = newbestmove + " " + stockfish2mine(stockfish.get_fen_position())
    #     board.board, xcolor = board.loadFen(stockfish2mine(stockfish.get_fen_position()))

    #     if board.checkChecker(xcolor, board.board):
    #         emit("check", xcolor, room = game[gameCode][0])        

    #     movedict = updateBoard(" ".join(newfen.split()[1:]))
    #     emit("oppoMove", movedict, room = game[gameCode][0])
    #     emit("updatedFen", newfen, room = game[gameCode][0])



# @socketio.on("createGame")
# def createGame(code):
#     if code[0:3] != "CPU":
#         sessions[session.sid] = request.sid
#         game[code] = [session.sid]
#         print(game)
#     else:
#         game[code] = [session.sid, "CPU"]

# @socketio.on("playerJoin")
# def playerJoin(code):
#     emit("playerJoin", room = sessions[gameInfo[gameCode][0]])

@socketio.on("joinGame")
def joinGame(code):
    sessions[session.sid] = request.sid

    if code not in gameInfo:
        gameMoves[code] = []
        gameFens[code] = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR White KQkq - 0 1"]
        posMoves[code] = updateBoard("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR White KQkq - 0 1")
        gameInfo[code] = [session.sid]
        chatHistory[code] = []
    elif len(gameInfo[code]) == 1:
        gameInfo[code].append(session.sid)
        emit("playerJoin", room = sessions[gameInfo[code][0]])

    print(gameInfo)

@socketio.on("checkCode")
def checkCode(code):
    if code in gameInfo:
        if len(gameInfo[code]) == 1:
            emit("checkCode", True)
        else:
            emit("checkCode", False)
    else:
        emit("checkCode", False)

@socketio.on("gameOver")
def gameOver(code, ending):
    emit("gameOver", ending, room = sessions[gameInfo[code][0]])
    emit("gameOver", ending, room = sessions[gameInfo[code][1]])



if __name__ == '__main__':
    socketio.run(app)

