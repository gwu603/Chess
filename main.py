from piece import Piece
from board import Board
from stockfish import Stockfish



def generatepieces():
    pieces = []
    pieces.append(Piece("R","11","White"))
    for i in range(1,9):
        pieces.append(Piece("P", str(i)+"2","White"))
        pieces.append(Piece("P",str(9-i)+"7","Black"))
    pieces.append(Piece("R","81","White"))
    pieces.append(Piece("R","18","Black"))
    pieces.append(Piece("R","88","Black"))
    pieces.append(Piece("N","21","White"))
    pieces.append(Piece("N","71","White"))
    pieces.append(Piece("N","28","Black"))
    pieces.append(Piece("N","78","Black"))
    pieces.append(Piece("B","31","White"))
    pieces.append(Piece("B","61","White"))
    pieces.append(Piece("B","38","Black"))
    pieces.append(Piece("B","68","Black"))
    pieces.append(Piece("Q","41","White"))
    pieces.append(Piece("Q","48","Black"))
    pieces.append(Piece("K","51","White"))
    pieces.append(Piece("K","58","Black"))
    return pieces
    
pieces = generatepieces()
board = Board(pieces)
board.resetBoard()
#board.printBoard()

fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR White KQkq - 0 1"

# stockfish = Stockfish("/Users/zhelyabuzhsky/Work/stockfish/stockfish-9-64")

stockfish = Stockfish(r"C:\Users\yiqin\Desktop\stockfish_14_win_x64_avx2\stockfish_14_win_x64_avx2\stockfish_14_x64_avx2.exe")
# stockfish = Stockfish(parameters={"Threads": 2, "Minimum Thinking Time": 30})

stockfish.set_fen_position("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")

print(stockfish.get_best_move())


# board.makeMove("White", "P4244")
# board.makeMove("White", "P4445")
# board.makeMove("Black", "P5755")
# # board.makeMove("Black", "P4745")
print(board.allMoves("White", fen))
allMoves = board.allMoves("White", fen)
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
        x = "T"

    newfen = holderfen[0] + " " + color + " " + holderfen[2] + " " + holderfen[3]
    movedict[move] = newfen

print(movedict)
#print(board.checkEn_passant("White"))


# board.board, color = board.loadFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR White)
print(board)
# print(board.allMoves("White"))

#x = board.generateMoves("White")

#print(x)



while False:
    if color:
        white = input("White's move:")
        if white == "stop":
            exit()
        x = board.makeMove("White", white)
        if x == "invalid move":
            color = True
        elif x == "promote":
            name = input("Promotion piece:")
            piece = Piece(name, white[-2]+white[-1], "White")
            board.makePromotion(piece)
            color = False
        else:
            color = False
    else:
        black = input("Black's move:")
        if black == "stop":
            exit()
        x = board.makeMove("Black", black)
        if x == "invalid move":
            color = False
        elif x == "promote":
            name = input("Promotion piece:")
            piece = Piece(name, white[-2]+white[-1], "Black")
            board.makePromotion(piece)
            color = False
        else:
            color = True

    print(board)










