from piece import Piece

class Board:

    def __init__(self, pieces):
        self.pieces = pieces
        self.board = [[]]


    def resetBoard(self): #places all pieces on their respective square at the start
        
        self.board = [[Piece(".","Null","Null") for i in range(8)] for j in range(8)]

        for val in self.pieces:
            row = int(val.pos[1])-1
            col = int(val.pos[0])-1
            self.board[row][col] = val

    def printBoardtest(self,board): #visually prints board in terminal
        visualboard = []
        for i in range(8):
            x = []
            for j in range(8):
                x.append(board[i][j].name)
            visualboard.append(x)
        for i in reversed(range(8)):
            print(visualboard[i])

    
    def printBoard(self): #visually prints board in terminal
        visualboard = []
        for i in range(8):
            x = []
            for j in range(8):
                x.append(self.board[i][j].name)
            visualboard.append(x)
        for i in reversed(range(8)):
            print(visualboard[i])

    
    def makeMove(self, color, move): #makes a move directly on the instantiated board

        x = self.screenPosMoves(self.generateMoves(color, self.board), color, False)
        y = self.checkCastling(color, self.board)
        z = self.screenPosMoves(self.checkEn_passant(color), color, True)


        if move in x:
            self.board[int(move[2])-1][int(move[1])-1].pos = move[-2] + move[-1]
            self.board[int(move[2])-1][int(move[1])-1].hasMoved = True
            self.board[int(move[-1])-1][int(move[-2])-1] = self.board[int(move[2])-1][int(move[1])-1]
            self.board[int(move[2])-1][int(move[1])-1] = Piece(".","Null","Null")
            if move[0] == "P" and abs(int(move[2])-int(move[-1])) == 2:
                self.board[int(move[-1])-1][int(move[-2])-1].movedDouble = True
            if move[0] == "P" and move[-1] == 8 and color == "White":
                return "promote"
            if move[0] == "P" and move[-1] == 0 and color == "Black":
                return "promote"
        elif move in y:
            if move[-2] == "7":
                self.board[int(move[2])-1][7].pos = "6" + move[-1]
                self.board[int(move[-1])-1][5] = self.board[int(move[2])-1][7]
                self.board[int(move[2])-1][7] = Piece(".","Null","Null")
            else:
                self.board[int(move[2])-1][0].pos = "4" + move[-1]
                self.board[int(move[-1])-1][3] = self.board[int(move[2])-1][0]
                self.board[int(move[2])-1][0] = Piece(".","Null","Null")
        elif move in z:
            self.board[int(move[2])-1][int(move[1])-1].pos = move[-2] + move[-1]
            self.board[int(move[2])-1][int(move[1])-1].hasMoved = True
            self.board[int(move[-1])-1][int(move[-2])-1] = board[int(move[2])-1][int(move[1])-1]
            self.board[int(move[2])-1][int(move[1])-1] = Piece(".","Null","Null")
            if color == "White":
                self.board[int(move[-1])-2][int(move[-2])-1] = Piece(".","Null","Null")
            else:
                self.board[int(move[-1])][int(move[-2])-1] = Piece(".","Null","Null")
        else:
            print("invalid move")
            return "invalid move"
        if color == "White":
            color = "Black"
        else:
            color = "White"
        
        #x = self.screenPosMoves(self.generateMoves(color, self.board), color, False)
        #y = self.screenPosMoves(self.checkEn_passant(color, self.board), color, True)
        # if len(x) == 0 and self.isCheck(color):
        #     print("Checkmate")
    def makePromotion(self, square, piece):
        self.board[int(piece.pos[1])-1][int(piece.pos[0])-1] = Piece(piece.name, piece.pos, piece.color)
    
    def generateMoves(self, color, board): #generates all possible moves (not considering checks/checkmates)
        moves = []
        for i in range(8):
            for j in range(8):
                piece = board[i][j]
                if piece.color == color:
                    name = piece.name
                    if name == "Q" or name == "B" or name == "R":
                        if name == "R":
                            directions = [(-1,0), (1,0), (0,1), (0,-1)]
                        elif name == "B":
                            directions = [(1,1), (-1,-1), (-1,1), (1,-1)]
                        else:
                            directions = [(-1,0), (1,0), (0,1), (0,-1), (1,1), (-1,-1), (-1,1), (1,-1)]
                        for direction in directions:
                            col, row = int(piece.pos[0]), int(piece.pos[1])
                            isAdding = True
                            while isAdding:
                                col += direction[0]
                                row += direction[1]
                                move = name+str(piece.pos[0])+str(piece.pos[1])+str(col)+str(row)
                                if not (row < 1 or row > 8 or col < 1 or col > 8):
                                    if board[row-1][col-1].name == ".":
                                            moves.append(move)
                                    else:
                                        if board[row-1][col-1].color != piece.color:
                                            moves.append(move[:-2]+"x"+move[-2:])
                                        isAdding = False
                                else:
                                    isAdding = False
                    if name == "N" or name == "K":
                        if name == "N":
                            possibleMoves = [(1,2),(-1,2),(1,-2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]
                        if name == "K":
                            possibleMoves = [(-1,-1),(1,1),(1,0),(0,1),(-1,1),(1,-1),(-1,0),(0,-1)]
                        for direction in possibleMoves:
                            col, row = int(piece.pos[0]), int(piece.pos[1])
                            col += direction[0]
                            row += direction[1]
                            move = name+str(piece.pos[0])+str(piece.pos[1])+str(col)+str(row)
                            if not (row < 1 or row > 8 or col < 1 or col > 8):
                                if board[row-1][col-1].pos == str(col) + str(row):
                                    if board[row-1][col-1].color != piece.color:
                                        moves.append(move)
                                else:
                                    moves.append(move)

                    if name == "P":
                        col, row = int(piece.pos[0]), int(piece.pos[1])
                        if color == "White":
                            direction, take, lineChecker = 1, [(1,1),(-1,1)], 2
                        else:
                            direction, take, lineChecker = -1, [(1,-1),(-1,-1)], 7
                        if board[row-1 + direction][col-1].name == ".":
                            moves.append(name+str(col)+str(row)+str(col)+str(row+direction))
                            if board[row-1 + 2*direction][col-1].name == "." and row == lineChecker:
                                moves.append(name+str(col)+str(row)+str(col)+str(row+2*direction))
                        if col < 8:
                            if board[row-1+take[0][1]][col-1+take[0][0]].name != "." and board[row-1+take[0][1]][col-1+take[0][0]].color != color:
                                moves.append(name+str(piece.pos[0])+str(piece.pos[1])+"x"+str(col+take[0][0])+str(row+take[0][1]))
                        if col > 1:
                            if board[row-1+take[1][1]][col-1+take[1][0]].name != "." and board[row-1+take[1][1]][col-1+take[1][0]].color != color:
                                moves.append(name+str(piece.pos[0])+str(piece.pos[1])+"x"+str(col+take[1][0])+str(row+take[1][1]))
        return moves

    def checkEn_passant(self, color):
        move = []
        if color == "White":
            direction = 1
        else:
            direction = -1
        for i in range(8):
            for j in range(8):
                if self.board[i][j].color == color:
                    if self.board[i][j].name == "P" and j < 7:
                        if self.board[i][j+1].name == "P" and self.board[i][j+1].movedDouble:
                            move.append("P"+ str(self.board[i][j].pos) + "x" + str(int(self.board[i][j].pos[0])+1) + str(int(self.board[i][j].pos[1])+direction))
                    if self.board[i][j].name == "P" and j > 1:
                        if self.board[i][j-1].name == "P" and self.board[i][j-1].movedDouble:
                            move.append("P"+self.board[i][j].pos + "x" + str(int(self.board[i][j].pos[0])-1) + str(int(self.board[i][j].pos[1]+direction)))
        #print(move)
        return move
    
    def checkCastling(self, color, board):
        move = []
        if color == "White":
            row = 1
        else:
            row = 8
        if not self.isCheck(color, "K5"+str(row)+"5"+str(row), False):
            if board[row-1][4].name == "K" and board[row-1][4].hasMoved == False and board[row-1][0].hasMoved == False:
                if board[row-1][3].name == "." and board[row-1][2].name == "." and board[row-1][1].name == ".":
                    if not self.isCheck(color, "K5"+str(row)+"4"+str(row), False) and not self.isCheck(color, "K5"+str(row)+"3"+str(row), False):
                        move.append("K5"+str(row) + "3"+ str(row))
            if board[row-1][4].name == "K" and board[row-1][4].hasMoved == False and board[row-1][7].hasMoved == False:
                if board[row-1][5].name == "." and board[row-1][6].name == ".":
                    if not self.isCheck(color, "K5"+str(row)+"6"+str(row), False) and not self.isCheck(color, "K5"+str(row)+"7"+str(row), False):
                        move.append("K5"+str(row) + "7"+ str(row))
        return move    


    
    def screenPosMoves(self, moves, color, en_pass): #screens all naive moves to for checks/checkmates
        actualmoves = []
        for move in moves:
            if not self.isCheck(color, move, en_pass):
                actualmoves.append(move)
        return actualmoves

    def isCheck(self, color, move, en_pass): #checks whether or not a naive move is a legal move
        board = [[Piece(".","Null","Null") for i in range(8)] for j in range(8)]
        pieces = []
        for i in range(8):
            for j in range(8):
                newp = Piece(self.board[i][j].name,self.board[i][j].pos,self.board[i][j].color)
                board[i][j] = newp

        if en_pass:
            board[int(move[2])-1][int(move[1])-1].pos = move[-2] + move[-1]
            board[int(move[2])-1][int(move[1])-1].hasMoved = True
            board[int(move[-1])-1][int(move[-2])-1] = board[int(move[2])-1][int(move[1])-1]
            board[int(move[2])-1][int(move[1])-1] = Piece(".","Null","Null")
            if color == "White":
                board[int(move[-1])-2][int(move[-2])-1] = Piece(".","Null","Null")
            else:
                board[int(move[-1])][int(move[-2])-1] = Piece(".","Null","Null")
            #self.printBoardtest(board)
            
        # elif castle:
        #     if move[-2] == "7":
        #         board[int(move[2])-1][7].pos = "6" + move[-1]
        #         board[int(move[-1])-1][5] = board[int(move[2])-1][7]
        #         board[int(move[2])-1][7] = Piece(".","Null","Null")
        #     else:
        #         board[int(move[2])-1][0].pos = "4" + move[-1]
        #         board[int(move[-1])-1][3] = board[int(move[2])-1][0]
        #         board[int(move[2])-1][0] = Piece(".","Null","Null")
            
        else:
            board[int(move[2])-1][int(move[1])-1].pos = move[-2] + move[-1]
            board[int(move[2])-1][int(move[1])-1].hasMoved = True
            board[int(move[-1])-1][int(move[-2])-1] = board[int(move[2])-1][int(move[1])-1]
            board[int(move[2])-1][int(move[1])-1] = Piece(".","Null","Null")



        if color == "White":
            color = "Black"
        else:
            color = "White"

        x = self.generateMoves(color, board)

        for val in x:
            if board[int(val[-1])-1][int(val[-2])-1].name == "K":
                return True
        return False



    def getSquare(self, square): #returns the piece of a given square on the board
        return self.board[square[1]][square[0]]
