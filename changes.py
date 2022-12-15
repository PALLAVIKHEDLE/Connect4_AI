import numpy as np
import random
import pygame
import sys
import math


BLACK = (0,0,0)
TAN=(210,180,140)
GREEN=(0,128,0)
YELLOW = (255,255,0)

HORIZONTAL_COUNT = 6
VERTICAL_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_BLOCK = 1
AI_BLOCK = 2

WINDOW_LENGTH = 4

def create_panel():
	board = np.zeros((HORIZONTAL_COUNT,VERTICAL_COUNT))
	return board

def drop_block(board, row, col, piece):
	board[row][col] = piece

def is_valid_position(board, col):
	return board[HORIZONTAL_COUNT-1][col] == 0

def get_next_available_row(board, col):
	for r in range(HORIZONTAL_COUNT):
		if board[r][col] == 0:
			return r

def print_panel(board):
	print(np.flip(board, 0))

def winning_move(board, piece):
	# Check horizontal locations for win
	for c in range(VERTICAL_COUNT-3):
		for r in range(HORIZONTAL_COUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(VERTICAL_COUNT):
		for r in range(HORIZONTAL_COUNT-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diaganols
	for c in range(VERTICAL_COUNT-3):
		for r in range(HORIZONTAL_COUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols
	for c in range(VERTICAL_COUNT-3):
		for r in range(3, HORIZONTAL_COUNT):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

def evaluate_window(window, piece):
	score = 0
	opp_piece = PLAYER_BLOCK
	if piece == PLAYER_BLOCK:
		opp_piece = AI_BLOCK

	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4

	return score

def score_position(board, piece):
	score = 0

	## Score center column
	center_array = [int(i) for i in list(board[:, VERTICAL_COUNT//2])]
	center_count = center_array.count(piece)
	score += center_count * 3

	## Score Horizontal
	for r in range(HORIZONTAL_COUNT):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(VERTICAL_COUNT-3):
			window = row_array[c:c+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score Vertical
	for c in range(VERTICAL_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(HORIZONTAL_COUNT-3):
			window = col_array[r:r+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score posiive sloped diagonal
	for r in range(HORIZONTAL_COUNT-3):
		for c in range(VERTICAL_COUNT-3):
			window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	for r in range(HORIZONTAL_COUNT-3):
		for c in range(VERTICAL_COUNT-3):
			window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	return score

def is_terminal_node(board):
	return winning_move(board, PLAYER_BLOCK) or winning_move(board, AI_BLOCK) or len(get_valid_positions(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
	valid_locations = get_valid_positions(board)
	is_terminal = is_terminal_node(board)
	if depth == 0 or is_terminal:
		if is_terminal:
			if winning_move(board, AI_BLOCK):
				return (None, 100000000000000)
			elif winning_move(board, PLAYER_BLOCK):
				return (None, -10000000000000)
			else: # Game is over, no more valid moves
				return (None, 0)
		else: # Depth is zero
			return (None, score_position(board, AI_BLOCK))
	if maximizingPlayer:
		value = -math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_available_row(board, col)
			b_copy = board.copy()
			drop_block(b_copy, row, col, AI_BLOCK)
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing player
		value = math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_available_row(board, col)
			b_copy = board.copy()
			drop_block(b_copy, row, col, PLAYER_BLOCK)
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

def get_valid_positions(board):
	valid_locations = []
	for col in range(VERTICAL_COUNT):
		if is_valid_position(board, col):
			valid_locations.append(col)
	return valid_locations

def pick_best_move(board, piece):

	valid_locations = get_valid_positions(board)
	best_score = -10000
	best_col = random.choice(valid_locations)
	for col in valid_locations:
		row = get_next_available_row(board, col)
		temp_board = board.copy()
		drop_block(temp_board, row, col, piece)
		score = score_position(temp_board, piece)
		if score > best_score:
			best_score = score
			best_col = col

	return best_col

def draw_panel(board):
	for c in range(VERTICAL_COUNT):
		for r in range(HORIZONTAL_COUNT):
			pygame.draw.rect(screen, YELLOW, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(VERTICAL_COUNT):
		for r in range(HORIZONTAL_COUNT):		
			if board[r][c] == PLAYER_BLOCK:
				pygame.draw.circle(screen, GREEN, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI_BLOCK: 
				pygame.draw.circle(screen, TAN, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()

board = create_panel()
print_panel(board)
game_over = False

pygame.init()

SQUARESIZE = 100

width = VERTICAL_COUNT * SQUARESIZE
height = (HORIZONTAL_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
draw_panel(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(PLAYER, AI)

while not game_over:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION:
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			posx = event.pos[0]
			if turn == PLAYER:
				pygame.draw.circle(screen, GREEN, (posx, int(SQUARESIZE/2)), RADIUS)

		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			#print(event.pos)
			# Ask for Player 1 Input
			if turn == PLAYER:
				posx = event.pos[0]
				col = int(math.floor(posx/SQUARESIZE))

				if is_valid_position(board, col):
					row = get_next_available_row(board, col)
					drop_block(board, row, col, PLAYER_BLOCK)

					if winning_move(board, PLAYER_BLOCK):
						label = myfont.render("Player 1 wins!!", 1, GREEN)
						screen.blit(label, (40,10))
						game_over = True

					turn += 1
					turn = turn % 2

					print_panel(board)
					draw_panel(board)


	# # Ask for Player 2 Input
	if turn == AI and not game_over:				

		#col = random.randint(0, VERTICAL_COUNT-1)
		#col = pick_best_move(board, AI_BLOCK)
		col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

		if is_valid_position(board, col):
			#pygame.time.wait(500)
			row = get_next_available_row(board, col)
			drop_block(board, row, col, AI_BLOCK)

			if winning_move(board, AI_BLOCK):
				label = myfont.render("Player 2 wins!!", 1, YELLOW)
				screen.blit(label, (40,10))
				game_over = True

			print_panel(board)
			draw_panel(board)

			turn += 1
			turn = turn % 2

	if game_over:
		pygame.time.wait(3000)