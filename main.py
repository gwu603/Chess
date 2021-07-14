from piece import Piece
from board import Board




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



board.makeMove("White", "P4244")
board.makeMove("White", "P4445")
board.makeMove("Black", "P5755")
# board.makeMove("Black", "P4745")
print(board.allMoves("White"))
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










