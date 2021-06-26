import chess
import time

board = chess.Board()

ticks = time.time()

board.push_san("d4")
print(board.legal_moves)  
board.push_san("e5")
print(board.legal_moves)  
board.push_san("dxe5")
print(board.legal_moves)  
board.push_san("Bb4")
print(board.legal_moves)  
  

#print(board)

print(time.time()-ticks)


ticks = time.time()

for i in range(1000000):
    a=5

print(time.time()-ticks)