import pygame
import traceback
import os
import math
import random
import time
from tetrominot import *

pygame.init()

block_images = {
    "S": pygame.image.load("Packs/default/S.png"),
    "Z": pygame.image.load("Packs/default/Z.png"),
    "I": pygame.image.load("Packs/default/I.png"),
    "O": pygame.image.load("Packs/default/O.png"),
    "J": pygame.image.load("Packs/default/J.png"),
    "L": pygame.image.load("Packs/default/L.png"),
    "T": pygame.image.load("Packs/default/T.png"),
}

class startbtn:
    def __init__(self,pos):
        self.image = pygame.Surface((100, 100))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=pos)

class Tetromino:
    def __init__(self, x, y, shape, image, shape_key):
        self.x = x
        self.y = y
        self.shape = shape
        self.rotation = 0
        self.image = image
        self.shape_key = shape_key
    def get_current_shape(self):
        return self.shape[self.rotation]
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)
    def get_positions(self):
        positions = []
        shape = self.get_current_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == '0':
                    positions.append((self.x + j, self.y + i))
        return positions 
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
    def check_collision(piece, grid):
        for (x, y) in piece.get_positions():
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return True
            if y >= 0 and grid[y][x] != 0:
                return True
        return False

    
def get_ghost_piece(piece, grid):
    ghost = Tetromino(piece.x, piece.y, piece.shape, piece.image, piece.shape_key)
    ghost.rotation = piece.rotation
    while not Tetromino.check_collision(ghost, grid):
        ghost.move(0, 1)
    ghost.move(0, -1)
    return ghost

def generate_bag():
    bag = ["S", "Z", "I", "O", "J", "L", "T"]
    random.shuffle(bag)
    return bag

bag = generate_bag()
next_queue = []

while len(next_queue) < 4:
    if not bag:
        bag = generate_bag()
    next_queue.append(bag.pop())

hold_piece = None
hold_used = False

def draw_ghost_piece(win, ghost):
    ghost_image = ghost.image.copy()
    ghost_image.set_alpha(80)
    for (x, y) in ghost.get_positions():
        win.blit(ghost_image, (x * BLOCK_SIZE, y * BLOCK_SIZE))
def draw_piece(win, piece):
    for (x, y) in piece.get_positions():
        win.blit(piece.image, (x * BLOCK_SIZE, y * BLOCK_SIZE))

def draw_grid(win, grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] != 0:
                win.blit(block_images[grid[y][x]], (x * BLOCK_SIZE, y * BLOCK_SIZE))

def clear_lines(grid):
    new_grid = []
    lines_cleared = 0
    for row in grid:
        if all(cell != 0 for cell in row):
            lines_cleared += 1
        else:
            new_grid.append(row)
    while len(new_grid) < GRID_HEIGHT:
        new_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
    return new_grid, lines_cleared

def flash_lines(grid, full_lines, surface):
    for _ in range(3):
        for y in full_lines:
            for x in range(GRID_WIDTH):
                pygame.draw.rect(surface, (255, 255, 255), (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        pygame.display.flip()
        pygame.time.delay(100)
        draw_grid(surface, grid)
        pygame.display.flip()
        pygame.time.delay(100)

def get_full_lines(grid):
    return [i for i, row in enumerate(grid) if all(cell != 0 for cell in row)]
    
def get_available_packs():
    base = "Packs"
    return [
        name for name in os.listdir(base)
        if os.path.isdir(os.path.join(base, name))
    ]

def load_pack(pack_name):
    folder = os.path.join("Packs", pack_name)
    images = {}
    for key in ["S", "Z", "I", "O", "J", "L", "T"]:
        path = os.path.join(folder, f"{key}.png")
        images[key] = pygame.image.load(path).convert_alpha()
    return images

class Button:
    def __init__(self, text, pos):
        self.font = pygame.font.SysFont("Arial", 32)
        self.text = text
        self.image = self.font.render(text, True, (0, 0, 0))
        self.original_y = pos[1]
        self.rect = pygame.Rect(pos[0], pos[1], 240, 50)
        
    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        screen.blit(self.image, (self.rect.x + 10, self.rect.y + 10))
        
def draw_hold(screen, hold_piece):
    font = pygame.font.SysFont("Arial", 20)
    text = font.render("Hold:", True, (0, 0, 0))
    screen.blit(text, (340, 320))

    if hold_piece:
        draw_mini_piece(screen, hold_piece, 360, 360)


def draw_preview(screen, next_queue):
    font = pygame.font.SysFont("Arial", 20)
    text = font.render("Next:", True, (0, 0, 0))
    screen.blit(text, (340, 20))

    y = 60
    for key in next_queue[:3]:
        draw_mini_piece(screen, key, 360, y)
        y += 80  

def draw_mini_piece(screen, shape_key, x, y, scale=16):
    index = ["S","Z","I","O","J","L","T"].index(shape_key)
    shape = tetrominos[index][0]

    img = block_images[shape_key]
    img = pygame.transform.scale(img, (scale, scale))

    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell == '0':
                screen.blit(img, (x + j * scale, y + i * scale))

def start_game():
    global GRID_WIDTH, GRID_HEIGHT, BLOCK_SIZE
    global bag, next_queue, hold_piece, hold_used, block_images
    
    FPS = 60

    BLOCK_SIZE = 32

    WIDTH, HEIGHT = 320, 640
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    GRID_WIDTH = WIDTH // BLOCK_SIZE
    GRID_HEIGHT = HEIGHT // BLOCK_SIZE

    name = "Tetris"

    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    clock = pygame.time.Clock()

    hold_piece = None
    hold_used = False

    fall_time = 0
    fall_speed = 0.5
    soft_drop_speed = 0.15

    shape_key = next_queue.pop(0)

    bag = generate_bag()
    next_queue = []
    while len(next_queue) < 4:
        if not bag:
            bag = generate_bag()
        next_queue.append(bag.pop())


    shape_index = ["S","Z","I","O","J","L","T"].index(shape_key)

    piece = Tetromino(3, -2, tetrominos[shape_index], block_images[shape_key], shape_key)

    aloitus = True
    game_over = False

    start_button = startbtn((WIDTH // 8, 512))

    pack_button = startbtn((WIDTH - 130 , 512))

    pack_selector = False

    packs = get_available_packs()
    pack_buttons = []

    y = 200
    for pack in packs:
        pack_buttons.append(Button(pack, (40, y)))
        y += 70

    scroll_offset = 0
    scroll_speed = 30 

    max_scroll = max(0, len(pack_buttons) * 70 - HEIGHT + 200)
    scroll_offset = max(0, min(scroll_offset, max_scroll))

    while aloitus:
        max_scroll = max(0, len(pack_buttons) * 70 - HEIGHT + 200)
        scroll_offset = max(0, min(scroll_offset, max_scroll))

        for btn in pack_buttons:
            btn.rect.y = btn.original_y - scroll_offset

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if not pack_selector:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.rect.collidepoint(event.pos):
                        aloitus = False
                        started = True
                    if pack_button.rect.collidepoint(event.pos):
                        pack_selector = True
                    if event.type == pygame.MOUSEWHEEL:
                        print("wheel:", event.y)

            else:
                if event.type == pygame.MOUSEWHEEL:
                    scroll_offset -= event.y * scroll_speed

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn in pack_buttons:
                        if btn.rect.collidepoint(event.pos):
                            selected_pack = btn.text
                            block_images = load_pack(selected_pack)
                            pack_selector = False

        screen.fill((255, 255, 255))

        if pack_selector:
            font = pygame.font.SysFont("Arial", 24)
            text3 = font.render("Valitse resurssi paketti", True, (0, 0, 0))
            screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2,
                                HEIGHT // 2 - 256 - text3.get_height() // 2))

            for btn in pack_buttons:
                btn.draw(screen)

        else:
            font = pygame.font.SysFont("Arial", 48)
            text2 = font.render(name, True, (0, 0, 0))
            screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2,
                                HEIGHT // 2 - 64 - text2.get_height() // 2))

            screen.blit(start_button.image, start_button.rect)
            screen.blit(pack_button.image, pack_button.rect)

        pygame.display.flip()
        clock.tick(FPS)



    piece = Tetromino(3, -2, tetrominos[shape_index], block_images[shape_key], shape_key)
    piece_locked = False
    flashing = False
    running = True

    print(aloitus)
    while running and not aloitus:
        if started:
            WIDTH, HEIGHT = 480, 640
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            started = False
        
        dt = clock.tick(FPS) / 1000.0
        fall_time += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    piece.move(1, 0)
                    if Tetromino.check_collision(piece, grid):
                        piece.move(-1, 0)
                elif event.key == pygame.K_LEFT:
                    piece.move(-1, 0)
                    if Tetromino.check_collision(piece, grid):
                        piece.move(1, 0)
                elif event.key == pygame.K_UP:
                    prev_rotation = piece.rotation
                    piece.rotate()
                    if Tetromino.check_collision(piece, grid):
                        piece.rotation = prev_rotation
                elif event.key == pygame.K_SPACE:
                    while not Tetromino.check_collision(piece, grid):
                        piece.move(0, 1)
                    piece.move(0, -1)
                    
                    for (x, y) in piece.get_positions():
                        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                            grid[y][x] = piece.shape_key

                    piece_locked = True
                    full_lines = get_full_lines(grid)
                    if full_lines:
                        flashing = True
                        flash_lines(grid, full_lines, screen)
                        for y in full_lines:
                            del grid[y]
                            grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                        flashing = False

                    shape_key = next_queue.pop(0)
                    
                    bag = generate_bag()
                    next_queue = []
                    while len(next_queue) < 4:
                        if not bag:
                            bag = generate_bag()
                        next_queue.append(bag.pop())

                    shape_index = ["S","Z","I","O","J","L","T"].index(shape_key)

                    piece = Tetromino(3, -2, tetrominos[shape_index], block_images[shape_key], shape_key)

                    hold_piece = None

                    hold_used = False

                    if Tetromino.check_collision(piece, grid):
                        running = False
                        game_over = True
                    piece_locked = False
                    fall_time = 0
                elif event.key == pygame.K_c: 
                    if not hold_used:
                        if hold_piece is None:
                            hold_piece = piece.shape_key
                            shape_key = next_queue.pop(0)
                            while len(next_queue) < 4:
                                if not bag:
                                    bag = generate_bag()
                                next_queue.append(bag.pop())
                        else:
                            temp = hold_piece
                            hold_piece = piece.shape_key
                            shape_key = temp

                        shape_index = ["S","Z","I","O","J","L","T"].index(shape_key)
                        piece = Tetromino(3, -2, tetrominos[shape_index], block_images[shape_key], shape_key)
                        hold_used = True



        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            if fall_time >= soft_drop_speed:
                piece.move(0, 1)
                if Tetromino.check_collision(piece, grid): 
                    piece.move(0, -1)



        
        

        if fall_time >= fall_speed:
            piece.move(0, 1)
            if Tetromino.check_collision(piece, grid): 
                piece.move(0, -1)
                for (x, y) in piece.get_positions():
                    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                        grid[y][x] = piece.shape_key
                        
                piece_locked = True
                full_lines = get_full_lines(grid)
                if full_lines:
                    flashing = True
                    flash_lines(grid, full_lines, screen)
                    for y in full_lines:
                        del grid[y]
                        grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                    flashing = False
                        
                shape_key = next_queue.pop(0)

                while len(next_queue) < 4:
                    if not bag:
                        bag = generate_bag()
                    next_queue.append(bag.pop())
                    
                shape_index = ["S","Z","I","O","J","L","T"].index(shape_key)

                piece = Tetromino(3, -2, tetrominos[shape_index], block_images[shape_key], shape_key)

                hold_used = False
                    
                if Tetromino.check_collision(piece, grid):
                    running = False
                    game_over = True
                piece_locked = False
            fall_time = 0

        grid, lines_cleared = clear_lines(grid)
        
        screen.fill((255, 255, 255))
        if not flashing:
            ghost = get_ghost_piece(piece, grid)
            draw_ghost_piece(screen, ghost)
        if not piece_locked:
            draw_piece(screen, piece)
        draw_grid(screen, grid)

        draw_preview(screen, next_queue)
        draw_hold(screen, hold_piece)
        
        pygame.display.flip()
        clock.tick(FPS)


    if game_over:
        font = pygame.font.SysFont("Arial", 48)
        text = font.render("GAME OVER", True, (0, 0, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

        pygame.display.flip()
        pygame.time.wait(1000)
        start_game()

start_game()


pygame.quit()
