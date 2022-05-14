'''
Very simple tetris implementation in pygame written in one sitting,
Controls are w,a,s,d to move and rotate blocks.
'''

import pygame 
import numpy as np
import time

class Figure:

    figures = [
        [np.array([-1,0], dtype=np.int8), np.array([0,1], dtype=np.int8), np.array([1,0], dtype=np.int8), np.array([0,0], dtype=np.int8)], # T
        [np.array([-1,0], dtype=np.int8), np.array([0,0], dtype=np.int8), np.array([1,0], dtype=np.int8), np.array([2,0], dtype=np.int8)], # |
        [np.array([-1,0], dtype=np.int8), np.array([0,0], dtype=np.int8), np.array([0,1], dtype=np.int8), np.array([-1,1], dtype=np.int8)], # square
        [np.array([-1,0], dtype=np.int8), np.array([0,0], dtype=np.int8), np.array([0,1], dtype=np.int8), np.array([1,1], dtype=np.int8)], # S 
        [np.array([-1,0], dtype=np.int8), np.array([-1,-1], dtype=np.int8), np.array([0,0], dtype=np.int8), np.array([1,0], dtype=np.int8)] # L
    ]

    rotate_matrix_right = np.array(
        [[0, -1],
         [1,  0]],
        dtype=np.int8
        )
    rotate_matrix_left = np.array(
        [[ 0, 1],
         [-1, 0]],
        dtype=np.int8
        )

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.elements = self.poll_figure()
        self.color = np.random.randint(2,9)


    def poll_figure(self):
        return self.figures[np.random.randint(len(self.figures)-1)]

    def move(self, x, y):
        # moves center of figure by [x, y] vector
        self.x = self.x + x
        self.y = self.y + y
    
    def rotate(self, direction):
        # roation = 0 - left
        # roation = 1 - right
        if direction == 0:
            for i in range(len(self.elements)):
                self.elements[i] = np.matmul(self.rotate_matrix_left, self.elements[i])
        else:
            for i in range(len(self.elements)):
                self.elements[i] = np.matmul(self.rotate_matrix_right, self.elements[i])


class Tetris:

    boundary_num = 1
    figure_num = 2
    moving_figure_num = 9

    def __init__(self, x, y):
        self.height = y
        self.width = x
        self.field = np.zeros((x,y), dtype=np.int8)
        self.figures = []
        self.current_figue = []
        self.moving_figure = None

    def empty_field(self):
        out = np.zeros((self.width+2,self.height+2), dtype=np.int8)
        out[0,:] = self.boundary_num
        out[-1,:] = self.boundary_num
        out[:,-1] = self.boundary_num
        return out

    def add_figure(self, x, y):
        self.moving_figure = Figure(x, y)

    def draw_figures(self):
        self.field = self.empty_field()
        for element in self.figures:
            self.field[element[0], element[1]] = element[2]
        for element in self.moving_figure.elements:
            self.field[element[0] + self.moving_figure.x, element[1] + self.moving_figure.y] = self.moving_figure.color

    def stick_figure(self, figure):
        # if a figure colided, make it stationary
        for element in figure.elements:
            self.figures.append(np.array([element[0]+figure.x, element[1]+figure.y, figure.color], dtype=np.int8))

    def check_collision(self):
        # returns  collision, does-it-need-sticking?

        for point_figure in self.moving_figure.elements:

            for point_stick in self.figures:
                # collision with other blocks
                if (point_figure[0]+self.moving_figure.x == point_stick[0]
                    and point_figure[1]+self.moving_figure.y == point_stick[1]):
                    return True, True

            # collision with walls
            if (point_figure[0]+self.moving_figure.x == 0
                or point_figure[0]+self.moving_figure.x == self.width + 1):
                return True, False
            # collision with ground
            if (point_figure[1]+self.moving_figure.y == self.height + 1):
                return True, True

        return False, False
    
    def check_line(self):
        # checks if there is a filled row
        for y in range(self.height + 1):
            sum = 0
            for block in self.figures:
                if block[1] == y:
                    sum = sum + 1
            if sum == self.width:
                self.score = self.score + 1
                self.figures = list(filter(lambda a: a[1] != y, self.figures))
                for i in range(len(self.figures)):
                    if self.figures[i][1] < y:
                        self.figures[i][1] = self.figures[i][1] + 1
                self.figures = list(filter(lambda a: a[1] != self.height + 1, self.figures))

    def move_figure(self, move):

        if move == 0:
            self.moving_figure.move(1, 0)
        elif move == 1:
            self.moving_figure.move(-1, 0)
        elif move == 2:
            self.moving_figure.rotate(0)
        elif move == 3:
            self.moving_figure.rotate(1)

        tmp, _ = self.check_collision()

        if tmp:
            if move == 0:
                self.moving_figure.move(-1, 0)
            elif move == 1:
                self.moving_figure.move(1, 0)
            elif move == 2:
                self.moving_figure.rotate(1)
            elif move == 3:
                self.moving_figure.rotate(0)

    def step(self):
        self.moving_figure.move(0, 1)
        collision, stick_collision = self.check_collision()
        if stick_collision:
            self.moving_figure.move(0, -1)
            self.stick_figure(self.moving_figure)
            self.add_figure(int(self.width/2)+1, 0)
            self.check_line()

    def start(self):
        self.field = self.empty_field()
        self.add_figure(int(self.width/2)+1, 0)
        self.score = 0

    def print_field(self):
        print(self.field)


class pygameTetris(Tetris):

    colors = [(255,255,255), # white for background
              (0,0,0),       # black for frame
              (255,0,0),     # block colors below
              (194, 8, 138),
              (245, 44, 215),
              (252, 151, 237),
              (204, 90, 143),
              (255, 28, 134),
              (194, 8, 95),
              (254,232,229)]

    square_size = 20
    offset = 100
    game_speed = 0.1 # step time in s

    def pygame_start(self):
        self.score = 0

    def print_field(self):
        print(self.field)


class pygameTetris(Tetris):

    colors = [(255,255,255), # white for background
              (0,0,0),       # black for frame
              (255,0,0),     # block colors below
              (194, 8, 138),
              (245, 44, 215),
              (252, 151, 237),
              (204, 90, 143),
              (255, 28, 134),
              (194, 8, 95),
              (254,232,229)]

    square_size = 20
    offset = 100
    game_speed = 0.1 # step time in s

    def pygame_start(self):

        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 30)

        self.gameDisplay = pygame.display.set_mode((800,600))
        pygame.display.set_caption('Tetris')

        self.start()

        timer = time.time()

        gameExit = False
        while not gameExit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameExit = True
                else:
                    self.handle_keys(event)

            #pygame.time.wait(self.game_speed)
            if time.time() > timer + self.game_speed:
                self.step()
                timer = timer + self.game_speed

            self.update_window()

    
    def handle_keys(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.move_figure(2)
                self.update_window()
            elif event.key == pygame.K_a:
                self.move_figure(1)
                self.update_window()
            elif event.key == pygame.K_s:
                self.move_figure(3)
                self.update_window()
            elif event.key == pygame.K_d:
                self.move_figure(0)
                self.update_window()
                
    def draw_window(self):
        self.gameDisplay.fill(self.colors[0])
        for i in range(self.width+2):
            for j in range(self.height+2):
                pygame.draw.rect(
                    self.gameDisplay,
                    self.colors[self.field[i,j]],
                    [self.offset + i*self.square_size, self.offset + j*self.square_size, self.square_size, self.square_size]
                )
        text_surface = self.font.render('Score: {}'.format(self.score), False, self.colors[5])
        self.gameDisplay.blit(text_surface, (2*self.offset + self.square_size*self.width,self.offset))
        pygame.display.update()
    
    def update_window(self):
        self.draw_figures() 
        self.draw_window()

if __name__ == '__main__':
    game = pygameTetris(10, 20)
    game.pygame_start()