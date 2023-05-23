import keyboard
import mouse
import pyautogui
import time
import numpy as np
import math
from PIL import ImageGrab
from TetrisBoard import TetrisBoard

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
    # print("weighted heights: ", weighted_heights)
    
    # print board given bottom is index 0
    # for row in reversed(board):
    #     print(row)

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
                    break
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
    best_score = float('-inf')
    board = board.copy()
    least_holes = float('inf')
    for rotation in range(len(block_array[0])):
        positions = get_positions(board, block_array[0][rotation])
        for position in positions:
            new_board = place_block(board, block_array[0][rotation], position)
            new_board = clear_full_rows(new_board)
            # break if have more holes than any before
            if find_least_holes(new_board) > least_holes:
                continue
            least_holes = find_least_holes(new_board)
            least_holes2 = float('inf')
            for rotation2 in range(len(block_array[1])):
                positions2 = get_positions(new_board, block_array[1][rotation2])
                for position2 in positions2:
                    new_board2 = place_block(new_board, block_array[1][rotation2], position2)
                    new_board2 = clear_full_rows(new_board2)
                    # break if have more holes than any before
                    if find_least_holes(new_board2) > least_holes2:
                        continue
                    least_holes2 = find_least_holes(new_board2)
                    for rotation3 in range(len(block_array[2])):
                        positions3 = get_positions(new_board2, block_array[2][rotation3])
                        for position3 in positions3:
                            new_board3 = place_block(new_board2, block_array[2][rotation3], position3)

                            score = evaluate_board(new_board3)
                            if score > best_score:
                                best_position = position
                                best_rotation = rotation
                                best_score = score

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
    while min_diff > 10:
        # break if esc
        if keyboard.is_pressed('esc'):
            break
        # get pixel colors in a 10 by 10 around x and y
        target_colors = []
        # Grab a portion of the screen
        image = ImageGrab.grab(bbox=(x - 3, y - 3, x + 3, y + 3))
        # Loop through the pixels in the grabbed image
        for i in range(6):
            for j in range(6):
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
                    closest_target_color = target_color
                if min_diff == 0:
                    break
        print("closest color: ", closest_color)
        print("closest target color: ", closest_target_color)
        print("min diff: ", min_diff)
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

x1, y1 = 0, 0
x2, y2 = 0, 0
# Create a new board
tetrisboard = TetrisBoard()
board_initialized = False
piece_array = []

while True:
    if keyboard.is_pressed('['):
        x1, y1 = mouse.get_position()
        time.sleep(0.2)

    if keyboard.is_pressed(']'):
        x2, y2 = mouse.get_position()
        time.sleep(0.2)

    if x1 != 0 and x2 != 0 and not board_initialized:
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
                    # print("currentpiece: ")
                    # for row in reversed(piece_array[0][0]):
                    #     print(row)
                    # time.sleep(0.3)
                    piece_array.append(get_piece_based_on_color(closest_color2, colors))
                    # place down the piece in the first array
                    best_position, best_rotation = find_best_position(tetrisboard.board, piece_array)
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
                    # if coord at x2, y2 change color, add piece to piece_array
                    # press up arrow to rotate for rotation
                    for i in range(best_rotation):
                        pyautogui.press('up')
                    # press left arrow or right arrow to move to position
                    if best_position2[1] < 3:
                        for i in range(3 - best_position2[1]):
                            pyautogui.press('left')
                    elif best_position2[1] > 3:
                        for i in range(best_position2[1] - 3):
                            pyautogui.press('right')
                    # press space to drop piece
                    pyautogui.press('space')
                    # remove 0s padding
                    best_piece_pos_rot = best_piece_pos_rot[~np.all(best_piece_pos_rot == 0, axis=1)]
                    best_piece_pos_rot = best_piece_pos_rot[:, ~np.all(best_piece_pos_rot == 0, axis=0)]
                    tetrisboard.add_piece(best_piece_pos_rot, best_position)
                    # clear full rows
                    tetrisboard.clear_full_rows()
                    # print the board
                    for row in reversed(tetrisboard.board):
                        print(row)
                    print("")
            else:
                closest_color2 = closest_color_in_area(colors, x2, y2)
                piece_array.append(get_piece_based_on_color(closest_color2, colors))
                # place down the piece in the first array
                # time how long find_best_position takes
                start_time = time.time()
                best_position, best_rotation = find_best_position(tetrisboard.board, piece_array)
                print("time: ", time.time() - start_time)
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
                # if coord at x2, y2 change color, add piece to piece_array
                # press up arrow to rotate for rotation
                for i in range(best_rotation):
                    pyautogui.press('up')
                # press left arrow or right arrow to move to position
                if best_position2[1] < 3:
                    for i in range(3 - best_position2[1]):
                        pyautogui.press('left')
                elif best_position2[1] > 3:
                    for i in range(best_position2[1] - 3):
                        pyautogui.press('right')
                # press space to drop piece
                pyautogui.press('space')
                # remove 0s padding
                best_piece_pos_rot = best_piece_pos_rot[~np.all(best_piece_pos_rot == 0, axis=1)]
                best_piece_pos_rot = best_piece_pos_rot[:, ~np.all(best_piece_pos_rot == 0, axis=0)]
                tetrisboard.add_piece(best_piece_pos_rot, best_position)
                # clear full rows
                tetrisboard.clear_full_rows()
                # print the board
                for row in reversed(tetrisboard.board):
                    print(row)
                print("")


                
    # Exit the loop with the "ESC" key
    if keyboard.is_pressed('esc'):
        break