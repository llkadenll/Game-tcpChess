import pygame
import chess
import sys
import threading

import socket
TCP_IP = sys.argv[1]
TCP_PORT = 4321
BUFFER_SIZE = 1024

windowSize = 800
squareSize = 100
Squares = []
squareColors = ((228, 205, 180), (115, 77, 38)) # bright, dark
squareColorsClicked = ((188, 165, 140), (155, 117, 78))
possibleMoveColors = ((218, 255, 170), 	(158, 225, 110))
squareLetters = ['h','g','f','e','d','c','b','a']
paintedSquares = []

chessboard = (
    ('a8','b8','c8','d8','e8','f8','g8','h8'),
    ('a7','b7','c7','d7','e7','f7','g7','h7'),
    ('a6','b6','c6','d6','e6','f6','g6','h6'),
    ('a5','b5','c5','d5','e5','f5','g5','h5'),
    ('a4','b4','c4','d4','e4','f4','g4','h4'),
    ('a3','b3','c3','d3','e3','f3','g3','h3'),
    ('a2','b2','c2','d2','e2','f2','g2','h2'),
    ('a1','b1','c1','d1','e1','f1','g1','h1')
)

class Square:
    size = squareSize

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def click(self):
        if (self.color == squareColors[0]):     #if the square is white
            self.color = squareColorsClicked[0]
        elif (self.color == squareColors[1]):       #if the square is black
            self.color = squareColorsClicked[1]

    def unclick(self):
        if (self.color == squareColorsClicked[0]):      #if the square is white
            self.color = squareColors[0]
        elif (self.color == squareColorsClicked[1]):    #if the square is black
            self.color = squareColors[1]
        
    def paint(self):
        if self.color == squareColors[0]:   #if the square is white
            self.color = possibleMoveColors[0]
        elif self.color == squareColors[1]:      #if the square is black
            self.color = possibleMoveColors[1]
    
    def unpaint(self):
        if self.color == possibleMoveColors[0]:    #if the square is white
            self.color = squareColors[0]
        elif self.color == possibleMoveColors[1]:    #if the square is black
            self.color = squareColors[1]

def connectToServer():
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    my_color = s.recv(BUFFER_SIZE).decode()
    return my_color

def receiveDataFromServer():
    while(run):
        try:
            opponentMove = s.recv(BUFFER_SIZE).decode()
            #print('odebralem ', opponentMove)
            movePiece(int(opponentMove[0]), int(opponentMove[1]), int(opponentMove[2]), int(opponentMove[3]))
            drawChessboard()
        except:
            print('Connection closed')
            break

def sendDataToServer(data):
    #print('wysylam ',data)
    s.send(data.encode())

def createSquares():
    for i in range(8):
        Squares.append([])
        for j in range(8):
            color = squareColors[(i+j+1) % 2] # +1 so there's a white square in the right-bottom corner
            Squares[i].append(Square(i*100,j*100,color))

def drawChessboard():
    for i in range(8):
        for j in range(8):
            pygame.draw.rect(screen, Squares[i][j].color, pygame.Rect(Squares[i][j].x,Squares[i][j].y,Squares[i][j].size,Squares[i][j].size))
    putImages()
    pygame.display.flip()

def putImages():
    for i in range(8):
        for j in range(8):
            square_index = chessboard[i][j]
            square = board.piece_at(chess.parse_square(square_index))
            if square != None:
                putImage(i,j)

def putImage(i,j):
    square_index = chessboard[i][j]
    square = str(board.piece_at(chess.parse_square(square_index)))
    if square == square.upper():    # then it means the piece is white
        image = pygame.image.load('img/white/'+ square +'.png')
    else:       # when piece is black
        image = pygame.image.load('img/black/'+ square +'.png')
    screen.blit(image, (j*squareSize+20, i*squareSize+20))

def handleClick(firstSquare):
    i = pygame.mouse.get_pos()[0] // squareSize
    j = pygame.mouse.get_pos()[1] // squareSize
    square_index = chessboard[j][i]
    square = board.piece_at(chess.parse_square(square_index))
    if (firstSquare == None and board.color_at(chess.parse_square(square_index)) == board.turn):
        Squares[i][j].click()                                # if no square is selected, select clicked square
        firstSquare = [i, j]
        paintLegalMoves(chessboard[j][i])
    elif (firstSquare == [i, j]):                          # if clicked square is already selected
        Squares[firstSquare[0]][firstSquare[1]].unclick()  # unselect it
        unpaintLegalMoves()
        firstSquare = None
    elif firstSquare != None:                                           # if clicked square is not the selected one
        if square == None and movePossible(firstSquare[0], firstSquare[1], i, j):   # check if the clicked square is not occupied
            movePiece(firstSquare[0], firstSquare[1], i, j)             # and move the piece to the clicked square
            Squares[firstSquare[0]][firstSquare[1]].unclick() 
            unpaintLegalMoves()
            sendDataToServer(str(firstSquare[0])+str(firstSquare[1])+str(i)+str(j))
            firstSquare = None
    
        elif board.color_at(chess.parse_square(square_index)) == board.turn:    # if clicked field is occupied
            Squares[firstSquare[0]][firstSquare[1]].unclick()               # by a piece of the same color
            unpaintLegalMoves()
            firstSquare = [i, j]
            Squares[firstSquare[0]][firstSquare[1]].click()
            paintLegalMoves(chessboard[j][i])

        elif board.color_at(chess.parse_square(square_index)) != board.turn and movePossible(firstSquare[0], firstSquare[1], i, j):     # if clicked field is occupied
            movePiece(firstSquare[0], firstSquare[1], i, j)                                                                             # by a piece of opposite color
            Squares[firstSquare[0]][firstSquare[1]].unclick()       
            unpaintLegalMoves()
            sendDataToServer(str(firstSquare[0])+str(firstSquare[1])+str(i)+str(j))
            firstSquare = [-1, -1]
    return firstSquare

def checkPawnPromotion(from_square, to_square):
    if str(board.piece_at(chess.parse_square(from_square))) != 'P':
        return False
    try:
        move_pawn_queen = str(board.find_move(chess.parse_square(from_square),chess.parse_square(to_square)))
    except(ValueError):
        move_pawn_queen = 0
    if str(from_square) + str(to_square) + 'q' == move_pawn_queen:
        return True
    else:
        return False

def paintLegalMoves(square):
    for i in range(8):
        for j in range(8):
            if chessboard[j][i] == square:
                continue
            if checkPawnPromotion(square, chessboard[j][i]):
                Squares[i][j].paint()
                paintedSquares.append([i,j])
            else:
                possible_move = chess.Move.from_uci(square + chessboard[j][i])
                if possible_move in board.legal_moves:
                    Squares[i][j].paint()
                    paintedSquares.append([i,j])

def unpaintLegalMoves():
    while paintedSquares != []:
        square = paintedSquares.pop()
        Squares[square[0]][square[1]].unpaint()

def movePossible(from_i, from_j, to_i, to_j):
    moveFrom = str(chessboard[from_j][from_i])
    moveTo = str(chessboard[to_j][to_i])
    move = chess.Move.from_uci(moveFrom + moveTo)
    if move in board.legal_moves or checkPawnPromotion(moveFrom,moveTo):
        return 1
    else:
        return 0

def movePiece(from_i, from_j, to_i, to_j):
    moveFrom = str(chessboard[from_j][from_i])
    moveTo = str(chessboard[to_j][to_i])
    move = chess.Move.from_uci(moveFrom + moveTo)
    if checkPawnPromotion(moveFrom,moveTo):
        board.remove_piece_at(chess.parse_square(moveFrom))
        board.set_piece_at(chess.parse_square(moveTo),chess.Piece(chess.QUEEN,board.turn), True)
        board.turn = not board.turn
        return
    if move in board.legal_moves:
        piece = chess.Square(chess.parse_square(moveTo))
        if piece != None:
            board.remove_piece_at(piece)
        board.push(move)

def displayResult(result):
    if result == 'Window closed':
        print(result)
        return
    if str(result.termination) == 'Termination.CHECKMATE':
        if result.winner == True:
            print('White wins!')
        elif result.winner == False:
            print('Black wins!')
    elif str(result.termination) == 'Termination.STALEMATE':
        print('Stalemate!')

def mainLoop(my_color, run):
    firstSquare = None

    while run:
        drawChessboard()
        
        event = pygame.event.wait()
        while (event.type != pygame.QUIT and event.type != pygame.MOUSEBUTTONDOWN):
            event = pygame.event.wait()
        if event.type == pygame.QUIT:  
            run = False
            return 'Window closed'
        if event.type == pygame.MOUSEBUTTONDOWN and ((my_color == "white\0" and board.turn == True) or (my_color == 'black\0' and board.turn == False)):
            firstSquare = handleClick(firstSquare)  

        if board.is_checkmate() or board.is_stalemate():
            return board.outcome()

def main():
    my_color = connectToServer()
    print(my_color,'\n')
    pygame.init()
    pygame.display.set_caption('tcpChess') # window title
    global board, screen
    board = chess.Board()
    screen = pygame.display.set_mode((windowSize, windowSize))
    createSquares()
    global run
    run = True
    receiveData = threading.Thread(target=receiveDataFromServer)
    receiveData.start()
    result = mainLoop(my_color, run)
    displayResult(result)
    sendDataToServer('end!')
    pygame.quit()

if __name__ == '__main__':
    main()