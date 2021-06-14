class Board:

    def __init__(self, pieces):
        self.pieces = pieces
        self.board = [["X" for i in range(8)] for j in range(8)]

    
    
    #def resetBoard(self):
        
        #self.board = [["X" for i in range(8)] for j in range(8)]

        #for val in self.pieces:
            #if val.name == "R" and val.color == "White":



    def generateBoard(self):
        for i in reversed(range(8)):
            print(self.board[i])

    def generateMoves(self):
        pass
