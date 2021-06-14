from piece import Piece
from board import Board



def generatepieces():
    pieces = []
    for i in range(1,9):
        pieces.append(Piece("P", str(i)+"2","White"))
        pieces.append(Piece("P",str(9-i)+"7","Black"))
    pieces.append(Piece("R",))


pieces = []
x = Board(pieces)

x.generateBoard()




