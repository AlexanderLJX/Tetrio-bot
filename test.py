import keyboard
import mouse
import time
import numpy as np
import math
from PIL import ImageGrab
from TetrisBoard import TetrisBoard
import pyautogui

# set x1, y1, x2, y2
x1, y1 = 1566, 439
x2, y2 = 1564, 488

x1_board, y1_board = 1342, 396 # top left of board
x2_board, y2_board = 1512, 733 # bottom right of board

# keybinds
rotate_clockwise = 'x'
rotate_180 = 'a'
rotate_counterclockwise = 'z'
# constants - ARR 0ms - DAS 40ms
calculation_accuracy = 10 # higher number means more accurate but slower
multiplayer = True # multiplayer mode has the pieces spawning from the bottom

# Each piece is represented by a 2D array, and rotations are stored as a list of 2D arrays
# 4x4 pieces are padded with 0s to make them 4x4
tetris_pieces = {
    'I': [
        np.array([[1, 1, 1, 1]]),
        np.array([[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]])
    ],
    'O': [
        np.array([[0, 1, 1, 0], [0, 1, 1, 0]])
    ],
    'T': [
        np.array([[1, 1, 1, 0], [0, 1, 0, 0]]),
        np.array([[0, 1, 0, 0], [0, 1, 1, 0], [0, 1, 0, 0]]),
        np.array([[0, 1, 0, 0], [1, 1, 1, 0]]),
        np.array([[0, 1, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0]]),
    ],
    'L': [
        np.array([[1, 1, 1, 0], [0, 0, 1, 0]]),
        np.array([[0, 1, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0]]),
        np.array([[1, 0, 0, 0], [1, 1, 1, 0]]),
        np.array([[0, 1, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0]]),
    ],
    'L2': [
        np.array([[1, 1, 1, 0], [1, 0, 0, 0]]),
        np.array([[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0]]),
        np.array([[0, 0, 1, 0], [1, 1, 1, 0]]),
        np.array([[1, 0, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0]]),
    ],
    'Z': [
        np.array([[0, 1, 1, 0], [1, 1, 0, 0]]),
        np.array([[0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0]])
    ],
    'Z2': [
        np.array([[1, 1, 0, 0], [0, 1, 1, 0]]),
        np.array([[0, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 0]])
    ]
}


def evaluate_board(board):
    # Implement your heuristic function here
    # The height of the tallest column - find highest row with a 1
    highest_block_row = 20
    for row in range(board.shape[0]):
        if not np.any(board[row] == 1):
            highest_block_row = row
            break
    # The sum of max height block in each column - the bottom of the board is index 0
    sum_of_heights = 0
    for col in range(board.shape[1]):
        for row in reversed(range(board.shape[0])):
            if board[row][col] == 1:
                sum_of_heights += row + 1
                break
    num_cleared_rows = np.sum(np.all(board == 1, axis=1))
    # The number of holes - find number of 0s with 1s above
    holes = np.sum((board == 0) & (np.cumsum(board, axis=0) < np.sum(board, axis=0)))
    # print("holes: ", holes)
    # The number of blockades - find number of 1s with 0s above
    blockades = np.sum((board == 1) & (np.cumsum(board, axis=0) > 0))
    # assign higher weights to higher blocks
    weighted_heights = 0
    for col in range(board.shape[1]):
        for row in reversed(range(board.shape[0])):
            # find highest block in each column
            if board[row][col] == 1:
                weighted_heights += (row + 1) * (row + 1)
                break

    A, B, C, D, E = -1, 10, -20, -1, -1
    score = A * weighted_heights + B * num_cleared_rows + C * holes + D * blockades + E * highest_block_row
    return score

def get_positions(board, rotated_block):
    # Return a list of all possible positions for the given block and rotation
    possible_positions = []
    # remove padded 0s from rotated block
    rotated_block = rotated_block[~np.all(rotated_block == 0, axis=1)]
    rotated_block = rotated_block[:, ~np.all(rotated_block == 0, axis=0)]
    # drop block from top for each column - bottom is index 0
    for x in range(board.shape[1] - rotated_block.shape[1] + 1):
        y = board.shape[0] - rotated_block.shape[0] - 1
        while y >= 0:
            if np.any(np.logical_and(rotated_block, board[y:y + rotated_block.shape[0], x:x + rotated_block.shape[1]])):
                if y == board.shape[0] - rotated_block.shape[0] - 1:
                    print("You lose!")
                    # exit()
                possible_positions.append((y + 1, x))
                break
            if y == 0:
                possible_positions.append((y, x))
            y -= 1

    return possible_positions

def clear_full_rows(board):
    while True:
        for y, row in enumerate(board):
            if all(cell == 1 for cell in row):
                board = np.delete(board, y, axis=0)
                # insert new row at last index which is the top of the board
                board = np.insert(board, board.shape[0], 0, axis=0)
                break
            if y == board.shape[0] - 1:
                return board

def find_least_holes(board):
    return np.sum((board == 0) & (np.cumsum(board, axis=0) < np.sum(board, axis=0)))

def find_best_position(board, block_array):
    best_position = None
    best_rotation = None
    board = board.copy()
    boards = []
    score_array = []
    position_rotation_array = []
    for rotation in range(len(block_array[0])):
        positions = get_positions(board, block_array[0][rotation])
        for position in positions:
            new_board = place_block(board, block_array[0][rotation], position)
            new_board = clear_full_rows(new_board)
            # evaluate board score and add to list
            score = evaluate_board(new_board)
            score_array.append(score)
            boards.append(new_board)
            position_rotation_array.append([position, rotation])

    # get top calculation_accuracy boards and position rotations using their scores
    top_boards = [x for _, x in sorted(zip(score_array, boards), key=lambda pair: pair[0], reverse=True)][:calculation_accuracy]
    top_position_rotations = [x for _, x in sorted(zip(score_array, position_rotation_array), key=lambda pair: pair[0], reverse=True)][:calculation_accuracy]
    boards2 = []
    score_array2 = []
    position_rotation_array2 = []
    for index, top_board in enumerate(top_boards):
        for rotation2 in range(len(block_array[1])):
            positions2 = get_positions(top_board, block_array[1][rotation2])
            for position2 in positions2:
                new_board2 = place_block(top_board, block_array[1][rotation2], position2)
                new_board2 = clear_full_rows(new_board2)
                # evaluate board score and add to list
                score = evaluate_board(new_board2)
                score_array2.append(score)
                boards2.append(new_board2)
                position_rotation_array2.append(top_position_rotations[index])

    # get top calculation_accuracy boards and position rotations using their scores
    top_boards2 = [x for _, x in sorted(zip(score_array2, boards2), key=lambda pair: pair[0], reverse=True)][:calculation_accuracy]
    top_position_rotations2 = [x for _, x in sorted(zip(score_array2, position_rotation_array2), key=lambda pair: pair[0], reverse=True)][:calculation_accuracy]
    # boards3 = []
    score_array3 = []
    position_rotation_array3 = []
    for index, top_board2 in enumerate(top_boards2):
        for rotation3 in range(len(block_array[2])):
            positions3 = get_positions(top_board2, block_array[2][rotation3])
            for position3 in positions3:
                new_board3 = place_block(top_board2, block_array[2][rotation3], position3)
                # new_board3 = clear_full_rows(new_board3) # either way is the same since the evaluation function takes into account full rows
                score = evaluate_board(new_board3)
                score_array3.append(score)
                # boards3.append(new_board3)
                position_rotation_array3.append(top_position_rotations2[index])
                # if score > best_score:
                #     best_position = position
                #     best_rotation = rotation
                #     best_score = score
    # get top 1 boards using their scores
    # top_board3s = [x for _, x in sorted(zip(score_array3, boards3), key=lambda pair: pair[0], reverse=True)][:1]
    top_position_rotations3 = [x for _, x in sorted(zip(score_array3, position_rotation_array3), key=lambda pair: pair[0], reverse=True)][:1]
    best_position, best_rotation = top_position_rotations3[0]

    return best_position, best_rotation

def place_block(board, rotated_block, position):
    new_board = board.copy()
    # remove padded 0s from rotated block
    rotated_block = rotated_block[~np.all(rotated_block == 0, axis=1)]
    rotated_block = rotated_block[:, ~np.all(rotated_block == 0, axis=0)]
    new_board[position[0]:position[0] + rotated_block.shape[0], position[1]:position[1] + rotated_block.shape[1]] += rotated_block
    return new_board

def euclidean_distance(color1, color2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(color1, color2)))

def closest_color_in_area(colors, x, y):
    min_diff = float('inf')
    closest_color = (0, 0, 0)
    while min_diff > 20:
        # break if esc
        if keyboard.is_pressed('esc'):
            break
        # get pixel colors in a 10 by 10 around x and y
        target_colors = []
        # Grab a portion of the screen
        image = ImageGrab.grab(bbox=(x - 5, y - 5, x + 5, y + 5))
        # Loop through the pixels in the grabbed image
        for i in range(10):
            for j in range(10):
                target_colors.append(image.getpixel((i, j)))

        # find the closest color in target_colors that is in colors
        closest_color = (0, 0, 0)
        min_diff = float('inf')
        for target_color in target_colors:
            for color in colors:
                diff = euclidean_distance(color, target_color)
                if diff < min_diff:
                    min_diff = diff
                    closest_color = color
                if min_diff < 20:
                    break
    return tuple(closest_color)

def get_piece_based_on_color(matched_color, colors):
    piece = None
    if matched_color == colors[0]:
        # print('Red - Z')
        piece = tetris_pieces['Z']
    elif matched_color == colors[1]:
        # print('Lime - Z2')
        piece = tetris_pieces['Z2']
    elif matched_color == colors[2]:
        # print('Dark blue - L2')
        piece = tetris_pieces['L2']
    elif matched_color == colors[3]:
        # print('Yellow - O')
        piece = tetris_pieces['O']
    elif matched_color == colors[4]:
        # print('Turquoise - I')
        piece = tetris_pieces['I']
    elif matched_color == colors[5]:
        # print('Orange - L')
        piece = tetris_pieces['L']
    elif matched_color == colors[6]:
        # print('Purple - T')
        piece = tetris_pieces['T']
    if piece is None:
        print('No piece found')
    return piece

# Define your 7 colors
colors = [
    (194, 64, 70),  # red 
    (142, 191, 61),  # lime
    (93, 76, 176), # dark blue
    (192, 168, 64),  # yellow
    (62, 191, 144),  # turquoise
    (194, 115, 68), # orange
    (176, 75, 166), # purple
]


# Create a new board
tetrisboard = TetrisBoard()
board_initialized = False
piece_array = []

def key_press(best_position, best_rotation):
    # key presses time
    start_time4 = time.time()
    # rotate
    if best_rotation == 1:
        keyboard.press(rotate_clockwise)
        keyboard.release(rotate_clockwise)
    elif best_rotation == 2:
        keyboard.press(rotate_180)
        keyboard.release(rotate_180)
    elif best_rotation == 3:
        keyboard.press(rotate_counterclockwise)
        keyboard.release(rotate_counterclockwise)
    # press left arrow or right arrow to move to position
    if best_position[1] < 3:
        for i in range(3 - best_position[1]):
            keyboard.press('left')
            keyboard.release('left')
    elif best_position[1] > 3:
        for i in range(best_position[1] - 3):
            keyboard.press('right')
            keyboard.release('right')
    # press space to drop piece
    keyboard.press('space')
    keyboard.release('space')
    time.sleep(0.15) # this is needed for some reason, probably can find a better way
    print("time for key presses: ", time.time() - start_time4)


def get_tetris_board_from_screen(top_left_x, top_left_y, bottom_right_x, bottom_right_y):
    board_coords = (top_left_x, top_left_y, bottom_right_x, bottom_right_y)
    board_image = ImageGrab.grab(board_coords)
    board_image = board_image.convert('L')
    board = np.zeros((20, 10), dtype=int)
    block_width = board_image.width // 10
    block_height = board_image.height // 20

    for row in reversed(range(20)):
        empty_row = True
        for col in range(10):
            x = col * block_width + block_width // 2
            y = row * block_height + block_height // 2
            # near black
            print(board_image.getpixel((x, y)))
            if board_image.getpixel((x, y)) < 20:
                board[20 - row - 1][col] = 0
            else:
                empty_row = False
                board[20 - row - 1][col] = 1
        if empty_row:
            break
    return board



# start program
while True:
    if keyboard.is_pressed('['):
        x1, y1 = mouse.get_position()
        time.sleep(0.2)

    if keyboard.is_pressed(']'):
        x2, y2 = mouse.get_position()
        time.sleep(0.2)
    
    if keyboard.is_pressed('-'):
        x1_board, y1_board = mouse.get_position()
        time.sleep(0.2)

    if keyboard.is_pressed('='):
        x2_board, y2_board = mouse.get_position()
        time.sleep(0.2)

    if x1 != 0 and x2 != 0 and not board_initialized and keyboard.is_pressed('space'):
        print('Board initialized')
        board_initialized = True
        closest_color1 = closest_color_in_area(colors, x1, y1)
        closest_color2 = closest_color_in_area(colors, x2, y2)
        print(f'Closest color: {closest_color1}')
        print(f'Closest color: {closest_color2}')
        piece_array.append(get_piece_based_on_color(closest_color1, colors))
        piece_array.append(get_piece_based_on_color(closest_color2, colors))
        first_move = True
        while True:
            # set break key
            if keyboard.is_pressed('esc'):
                break
            # if coord at x1, y1 change color, add piece to piece_ar ray
            if first_move:
                closest_color1_0 = closest_color_in_area(colors, x1, y1)
                closest_color2_0 = closest_color_in_area(colors, x2, y2)
                if closest_color2 != closest_color2_0 or closest_color1 != closest_color1_0:
                    first_move = False
                    closest_color1 = closest_color1_0
                    closest_color2 = closest_color2_0
                else:
                    continue
            closest_color2 = closest_color_in_area(colors, x2, y2)
            # total time
            start_time = time.time()
            # time to get color
            start_time3 = time.time()
            
            piece_array.append(get_piece_based_on_color(closest_color2, colors))
            print("time for get color: ", time.time() - start_time)
            # time to get board
            start_time2 = time.time()
            # get board from screen
            tetrisboard.board = get_tetris_board_from_screen(x1_board, y1_board, x2_board, y2_board)
            print("time for get board: ", time.time() - start_time2)
            # print board
            for row in reversed(tetrisboard.board):
                print(row)
            # time how long find_best_position takes
            start_time2 = time.time()
            best_position, best_rotation = find_best_position(tetrisboard.board, piece_array)
            print("time for find_best_position: ", time.time() - start_time2)
            best_piece_pos_rot = piece_array[0][best_rotation]
            # remove first piece from piece_array
            piece_array.pop(0)
            # add offset depending on padded zeros on the left side of axis 1 only
            offset = 0
            for i in range(best_piece_pos_rot.shape[1]):
                if not any(best_piece_pos_rot[:, i]):
                    offset += 1
                else:
                    break
            best_position2 = (best_position[0], best_position[1] - offset)
            key_press(best_position2, best_rotation)
            # remove 0s padding
            best_piece_pos_rot = best_piece_pos_rot[~np.all(best_piece_pos_rot == 0, axis=1)]
            best_piece_pos_rot = best_piece_pos_rot[:, ~np.all(best_piece_pos_rot == 0, axis=0)]
            tetrisboard.add_piece(best_piece_pos_rot, best_position)
            # clear full rows
            tetrisboard.clear_full_rows()
            print("total time: ", time.time() - start_time)
                
    # Exit the loop with the "ESC" key
    if keyboard.is_pressed('esc'):
        break