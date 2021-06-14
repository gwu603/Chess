class Board:

    def __init__(self, pieces):
        self.pieces = pieces
        self.board = [[]]


    
    
    #def resetBoard(self):
        
        #self.board = [["X" for i in range(8)] for j in range(8)]

        #for val in self.pieces:
            #if val.name == "R" and val.color == "White":

    def generateBoard():
        pass

    def printBoard(self): #visually prints board
        visualboard = []
        for row in self.board:
            x = []
            for col in self.board[i]:
                if 
                x.append(col.name)
            visualboard.append(x)
        for i in reversed(range(8)):
            print(visualboard[i])
        


    def generateMoves(self):
        pass
