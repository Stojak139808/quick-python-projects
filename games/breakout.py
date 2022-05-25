'''
Quick and barebone implementation on a breakout game,
it was more about using qt rather than making a game
'''


import sys
import numpy as np

from random import(
    randint,
    random
)

from PyQt5.QtCore import (
    Qt,
    QTimer
)
from PyQt5.QtGui import (
    QBrush,
    QPainter,
    QColor,
    QKeySequence,
    QPixmap
)
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QShortcut,
    QMainWindow
)

class PID:

    def __init__(self, P, I, D, dt):
        self.kp = P
        self.ki = I
        self.kd = D
        self.integral = 0
        self.dt = dt
        self.previous_e = 0

    def step(self, measurement, desiret_value):

        e = desiret_value - measurement
        # P
        out = e*self.kp
        # I
        self.integral += e*self.dt
        out += self.integral*self.ki
        # D
        out += self.kd*(e - self.previous_e)/self.dt
        self.previous_e = e
        
        return out


class Block(QGraphicsRectItem):
    
    id = 0

    def __init__(self, x, y, width, height):
        super().__init__(0, 0, width, height)
        self.width = width
        self.height = height
        self.setPos(x, y)
        
        self.end = 0
        self.id = Block.id
        Block.id += 1

    def setColor(self):
        brush = QBrush(self.color)
        self.setBrush(brush)
        self.update()

    def step(self):
        pass

    def __str__(self):
        return "0"

class StandardBlock(Block):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.color = QColor(0, 0, 255)
        self.setColor()

        self.type = 1

    def hit(self, side):
        # pop block
        return self.id, 1

    def __str__(self):
        return super().__str__()

class StaticBlock(Block):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.color = QColor(0, 0, 0)
        self.setColor()

        self.type = 2

    def hit(self, side):
        return self.id, 0
    
    def __str__(self):
        return super().__str__()

class PowerupBlock(Block):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.color = QColor(0, 0, 0)
        self.setColor()
        self.i = 0

        self.type = 3

    def hit(self, side):
        return self.id, 2
    
    def step(self):
        #change colors here
        self.i += 1
        if self.i == 5:
            self.color = QColor(randint(0,255), randint(0,255), randint(0,255))
            self.setColor()
            self.i = 0
        
    def __str__(self):
        return super().__str__()

class OneSidedBlock(Block):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.color = QColor(125, 125, 255)
        self.setColor()

        self.side = randint(1,4)  # side which has to be hit to destroy the block

        self.type = 4

    def hit(self, side):
        if side == self.side:
            return self.id, 1

        return self.id, 0

    def __str__(self):
        return super().__str__()

class SpeedBlock(Block):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        # true - speedup, false - slowdown
        self.speed = [True, False][randint(0,1)]
        if self.speed == True:
            self.color = QColor(125, 60, 0)
        else:
            self.color = QColor(0, 200, 125)
        self.setColor()

        self.type = 5
    
    def hit(self, side):
        if self.speed:
            return self.id, 3
        return self.id, 4

    def __str__(self):
        return super().__str__()

class ExplodingBlock(Block):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.color = QColor(255, 255, 0)
        self.setColor()

        self.type = 6

    def hit(self, side):
        return self.id, 5

    def __str__(self):
        return super().__str__()

class Ball(QGraphicsEllipseItem):

    def __init__(self, radius, dt):
        self.radius = radius
        self.dt = dt
        self.velocity_vector = np.zeros(2)
        self.max_speed = radius/dt

        super().__init__(0,
                         0,
                         self.radius*2,
                         self.radius*2)

        color = QColor(0, 255, 0)
        brush = QBrush(color)
        self.setBrush(brush)
        

    def move_ball(self, x, y):
        self.setX(x)
        self.setY(y)

    def change_velocity(self, vector):
        self.velocity_vector = np.array(vector)

    def speed_up(self):
        self.velocity_vector[0] = self.velocity_vector[0] * 1.5
        self.velocity_vector[1] = self.velocity_vector[1] * 1.5
    
    def slow_down(self):
        self.velocity_vector[0] = self.velocity_vector[0] * 0.5
        self.velocity_vector[1] = self.velocity_vector[1] * 0.5

    def cap_speed(self):
        speed = np.sqrt(self.velocity_vector[0]**2 + self.velocity_vector[1]**2)
        if speed > self.max_speed:
            ratio = self.max_speed/speed
            self.velocity_vector *= ratio
        
    def step(self):

        self.cap_speed()

        center_x = self.x() + self.velocity_vector[0]*self.dt
        center_y = self.y() + self.velocity_vector[1]*self.dt
        self.move_ball(center_x, center_y)

    def __str__(self):
        return "2"

class Powerup(Block):

    colors = [QColor(255, 0, 0),
              QColor(0, 255, 0),
              QColor(0, 0, 255),
              QColor(255, 255, 0),
              QColor(0, 255, 255)]

    def __init__(self, x, y, width, height):
        super().__init__(0, 0, width, height)
        self.power = randint(0,4)
        self.color = Powerup.colors[self.power]
        self.setColor()
        self.setPos(x, y)

    def hit(self):
        return self.id, self.power

    def step(self):
        self.setPos(self.x(), self.y() + 5)

    def __str__(self):
        return "1"

class Platform(QGraphicsRectItem):
    
    '''
    |x'|   | 0  1    |   | 0   |
    |v'| = | 0  -u/m | + | 1/m | * f(t)

    y = |1  0| * |x| + 0
                 |v|
    where m is mass and u is air friction coefficient
    f(t) is the acting force
    '''

    modes = [[5, 0, 3],
             [1, 0, 0],
             [2, 0, 0.5],
             [1, 0, 2],
             [1, 0, 1]]

    def __init__(self, platform_width, field_width, field_height, dt):
        self.height = 15
        self.center_x = 0
        self.velocity = 0
        self.mass = 0.1
        self.friction = 0.1
        self.platform_radius = platform_width/2
        self.field_width = field_width
        self.field_height = field_height
        self.dt = dt

        self.mode = 2  # 6 speed modes = 6 PIDs
        self.controller = PID(self.modes[2][0], self.modes[2][1], self.modes[2][2], dt)

        self.A = np.array([[0,                        1],
                           [0, -self.friction/self.mass]])
        self.B = np.array([[0],
                           [1/self.mass]])
        self.C = np.array([1, 0])

        self.X = np.array([[0],
                           [0]])

        super().__init__(0, 0, platform_width, self.height)
        self.setPos(-self.center_x, self.field_height - self.height)
        color = QColor(255, 0, 0)
        brush = QBrush(color)
        self.setBrush(brush)

    def move(self, u):

        Xprim = np.add(np.matmul(self.A, self.X),self.B*u)
        self.X = np.add(self.X, Xprim*self.dt)
        
        # platform wall collision here

        if self.X[0] + self.platform_radius > self.field_width:
            self.X[0] = self.field_width - self.platform_radius
            self.X[1] = 0  # hitting a wall stops you
        elif self.X[0] - self.platform_radius < 0:
            self.X[0] = self.platform_radius
            self.X[1] = 0  # hitting left wall also stops you

        self.center_x = np.matmul(self.C, self.X)
        self.setPos(self.center_x - self.platform_radius, self.field_height - self.height)

    def speedup(self):

        if self.mode < 4:
            self.mode += 1

        self.controller.integral = 0

        self.controller.kp = self.modes[self.mode][0]
        self.controller.ki = self.modes[self.mode][1]
        self.controller.kd = self.modes[self.mode][2]
    
    def slowdown(self):
        if self.mode > 0:
            self.mode -= 1

        self.controller.integral = 0
        
        self.controller.kp = self.modes[self.mode][0]
        self.controller.ki = self.modes[self.mode][1]
        self.controller.kd = self.modes[self.mode][2]

    def resize(self, radius_change: float):
        self.platform_radius += radius_change
        self.setRect(0, 0, self.platform_radius*2, self.height)
        self.setPos(self.center_x - self.platform_radius, self.field_height - self.height)

    def step(self, desired_position):

        f = self.controller.step(self.center_x ,desired_position)
        self.move(f)

        x = self.center_x + self.velocity*self.dt

        if(    x + self.platform_radius > self.field_width 
            or x - self.platform_radius < 0):
            # if wall was hit
           self.velocity = 0

        else:
            self.center_x = x
        #self.action = 0
        self.setPos(self.center_x - self.platform_radius, self.field_height - self.height)

class Breakout(QWidget):

    def __init__(self):
        super().__init__()
        self.game_width = 1000
        self.game_height = 400
        self.time_stamp = 1/30
        self.block_size = 25
        self.desired_position = 0
        self.on = False

        self.init_qt()

        #plot background
        '''
        background = QGraphicsRectItem(0, 0, self.game_width, self.game_height)
        brush = QBrush(QColor(255,255,255))
        background.setBrush(brush)
        self.scene.addItem(background)
        '''
        background = QPixmap("triangles-g8a61c3fa0_1280.rc")
        self.scene.addPixmap(background)


    def init_objects(self):
        self.elements = []
        self.elements = self.generate_grid()
        self.powerups = []
        
        self.platform = Platform(150, self.game_width, self.game_height, self.time_stamp)
        self.platform.center_x = self.game_width/2
        self.platform.X[0] = self.platform.center_x

        self.desired_position = self.platform.center_x

        self.indicator = QGraphicsRectItem(0, 0, 5, 5)
        self.indicator.setBrush(Qt.yellow)
        self.indicator.setPos(self.desired_position, self.game_height - 5)
        self.indicator.setZValue(5)
        self.scene.addItem(self.indicator)

        self.scene.addItem(self.platform)

        self.balls = []
        self.balls.append(Ball(10, self.time_stamp))
        self.balls[0].move_ball(int(self.game_width/2), int(self.game_height*0.8))
        self.balls[0].change_velocity((self.balls[0].max_speed*0.5, self.balls[0].max_speed*0.5))

        self.scene.addItem(self.balls[-1])
        
    
    def init_qt(self):
        
        self.scene = QGraphicsScene(0, 0, self.game_width, self.game_height)

        # Define our layout.
        vbox = QVBoxLayout()

        up = QPushButton("left")
        up.clicked.connect(self.left)
        vbox.addWidget(up)

        down = QPushButton("right")
        down.clicked.connect(self.right)
        vbox.addWidget(down)

        down = QPushButton("start")
        down.clicked.connect(self.start)
        vbox.addWidget(down)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)

        hbox = QHBoxLayout(self)
        hbox.addLayout(vbox)
        hbox.addWidget(self.view)
        self.setLayout(hbox)

        self.timer = QTimer()
        self.timer.timeout.connect(self.step)

        self.keyboard_init()

    def mousePressEvent(self, QMouseEvent):
        x = QMouseEvent.x() - 100
        y = QMouseEvent.y() - 14
        print(self.pos())
        print("Clicked At: (x, y) -> ({}, {})".format(x, y))
        if self.on == True: # if the game is running
            # change blocks here on click
            ob = self.view.itemAt(x, y)
            if ob.__str__() == '0':
                if ob.type == 1:
                    new_block = StaticBlock(ob.x(), ob.y(), ob.width, ob. height)
                elif ob.type == 2:
                    new_block = PowerupBlock(ob.x(), ob.y(), ob.width, ob. height)
                elif ob.type == 3:
                    new_block = OneSidedBlock(ob.x(), ob.y(), ob.width, ob. height)
                elif ob.type == 4:
                    new_block = SpeedBlock(ob.x(), ob.y(), ob.width, ob. height)
                elif ob.type == 5:
                    new_block = ExplodingBlock(ob.x(), ob.y(), ob.width, ob. height)
                elif ob.type == 6:
                    new_block = StandardBlock(ob.x(), ob.y(), ob.width, ob. height)

                self.block_hit_handle(ob.id, 1)
                self.scene.removeItem(ob)
                self.elements.append(new_block)
                self.scene.addItem(new_block)



    def keyboard_init(self):
        self.left_key = QShortcut(QKeySequence('a'), self)
        self.left_key.activated.connect(self.left_keyboard)

        self.right_key = QShortcut(QKeySequence('d'), self)
        self.right_key.activated.connect(self.right_keyboard)

    def left_keyboard(self):
        self.desired_position -= 10
        self.indicator.setPos(self.desired_position, self.game_height - 5)

    def right_keyboard(self):
        self.desired_position += 10
        self.indicator.setPos(self.desired_position, self.game_height - 5)

    def left(self):
        self.desired_position -= 50
        self.indicator.setPos(self.desired_position, self.game_height - 5)
        
    def right(self):
        self.desired_position += 50
        self.indicator.setPos(self.desired_position, self.game_height - 5)


    def start(self):
        self.init_objects()
        self.on = True
        self.timer.start(int(self.time_stamp*1000))
    
    def generate_grid(self):

        # method for generating breakable tiles
        grid = []

        gap = 0

        y = 0
        while y < self.game_height*0.25:
            x = 0
            while x < self.game_width:
                #grid.append(PowerupBlock(x + gap, y - gap, self.block_size - gap, self.block_size - gap))
                
                s = random()
                if s < 0.2 and x + self.block_size < self.game_width:
                    grid.append(StandardBlock(x + gap, y - gap, (self.block_size - gap)*2, self.block_size - gap))
                    x += 25
                elif s < 0.5:
                    grid.append(StandardBlock(x + gap, y - gap, self.block_size - gap, self.block_size - gap))
                elif s < 0.7:
                    grid.append(StaticBlock(x + gap, y - gap, self.block_size - gap, self.block_size - gap))
                elif s < 0.8:
                    grid.append(PowerupBlock(x + gap, y - gap, self.block_size - gap, self.block_size - gap))
                elif s < 0.9:
                    grid.append(SpeedBlock(x + gap, y - gap, self.block_size - gap, self.block_size - gap))
                elif s < 0.95:
                    grid.append(OneSidedBlock(x + gap, y - gap, self.block_size - gap, self.block_size - gap))
                else:
                    grid.append(ExplodingBlock(x + gap, y - gap, self.block_size - gap, self.block_size - gap))
                
                x += self.block_size
                self.scene.addItem(grid[-1])
            y += self.block_size

        return grid

    def ball_block_collision_check(self, rsq, x, y, width, height):

        # 0 - no
        # 1 - bottom
        # 2 - top
        # 3 - left
        # 4 - right

        yhsq = (y + height)**2
        xsq = x**2
        ysq = y**2
        xwsq = (x + width)**2

        #print("X: {} Y: {} W: {} H: {}".format(x, y, width, height))
        #print("RSQ: {} XSQ: {} YSQ {} YHSQ: {} XWSQ {}".format(rsq,xsq,ysq,yhsq,xwsq) )
        
        # assume ball is at (0;0)
        if x < 0 and x + width > 0:
            # bottom wall
            if ysq < rsq:
                return 1
        
            # top wall
            if yhsq < rsq:
                return 2

        if y < 0 and y > -height:
            # left wall
            if xsq < rsq:
                return 3

            # right wall
            if xwsq < rsq:
                return 4

        # add corner collision here
        if( xsq + ysq < rsq 
            or xsq + yhsq < rsq
            or xwsq + ysq < rsq
            or xwsq + yhsq < rsq):
            return 5

        # no collision
        return 0

    def ball_platform_collision(self, ball_x, ball_y, ball):
        
        if (ball_y + ball.radius > self. game_height - self.platform.height
            and abs(ball_x - self.platform.center_x) < self.platform.platform_radius):
            # platform was hit from above
            ball.velocity_vector[1] = -ball.velocity_vector[1]
            # simple ball spin
            #ball.velocity_vector[0] += self.platform.X[1]*0.5

        # add side platform collision here

    def block_hit_handle(self, id, action):
        
        # find id for block in a list
        lid = 0
        for i in range(len(self.elements)):
            if self.elements[i].id == id:
                lid = i
                break
        
        if action == 1:     # standard block / delete
            self.elements.pop(lid)
        elif action == 2:   # powerup block
            out = self.elements.pop(lid)
            power = Powerup(out.x(), out.y(), out.width, out.height)
            self.powerups.append(power)
            self.scene.addItem(power)
        elif action == 3 or action == 4:    # speed up/down block
            self.elements.pop(lid)
        elif action == 5:   # explode
            explosion_radius = self.block_size*2
            ersq = explosion_radius**2
            a = self.elements[lid].width / 2

            rm = []
            for i, x in enumerate(self.elements):
                if (( ((x.x() + x.width/2) - (self.elements[lid].x() + a))**2
                      + ((x.y() - x.height/2) - (self.elements[lid].y() - a))**2)
                      < ersq):
                    rm.append(i)
                    ob = self.view.itemAt(int(x.x() + self.block_size/2), int(x.y() + self.block_size/2))
                    if ob.__str__() == "0":
                        self.scene.removeItem(ob)

            for id in reversed(rm):
                self.elements.pop(id)


    def ball_collision_check(self, ball):
        
        rsq = ball.radius**2

        # next ball position if no collision
        x = ball.x() + ball.velocity_vector[0]*self.time_stamp + ball.radius
        y = ball.y() + ball.velocity_vector[1]*self.time_stamp + ball.radius
        
        
        for block in self.elements:
            col = self.ball_block_collision_check(rsq, block.x() - x, block.y() - y, block.width, block.height)
            if col != 0:
                if col == 5: # corner
                    ball.velocity_vector[0] = -ball.velocity_vector[0]
                    ball.velocity_vector[1] = -ball.velocity_vector[1]
                elif col == 1 or col == 2:
                    ball.velocity_vector[1] = -ball.velocity_vector[1]
                else:
                    ball.velocity_vector[0] = -ball.velocity_vector[0]
                id, action = block.hit(col)
                
                if action != 0:
                    # delete block from scene if needed
                    ob = self.view.itemAt(int(block.x() + self.block_size/2), int(block.y() + self.block_size/2))
                    print(ob)
                    if ob.__str__() == "0":
                        self.scene.removeItem(ob)

                self.block_hit_handle(id, action)

                if action == 3:
                    ball.speed_up()
                elif action == 4:
                    ball.slow_down()
        
        # walls 
        if self.game_width < x + ball.radius or 0 > x - ball.radius:
            # hit right or left wall
            ball.velocity_vector[0] = -ball.velocity_vector[0]

        if 0 > y - ball.radius: 
            # hit ground or celling
            ball.velocity_vector[1] = -ball.velocity_vector[1]

        # platform
        self.ball_platform_collision(x, y, ball)

    def use_powerup(self, which):
        if which == 0:
            # make platform bigger
            self.platform.resize(15)            

        elif which == 1:
            # make platform smaller
            self.platform.resize(-15)

        elif which == 2:
            # add balls
            self.balls.append(Ball(self.balls[-1].radius, self.time_stamp))
            self.balls[-1].move_ball(self.balls[-2].x(), self.balls[-2].y())
            self.balls[-1].velocity_vector = -self.balls[-2].velocity_vector
            self.scene.addItem(self.balls[-1])

            self.balls.append(Ball(self.balls[-1].radius, self.time_stamp))
            self.balls[-1].move_ball(self.balls[-2].x(), self.balls[-2].y())
            self.balls[-1].velocity_vector = -self.balls[-2].velocity_vector
            self.balls[-1].velocity_vector[0] = -self.balls[-1].velocity_vector[0]
            self.scene.addItem(self.balls[-1])

        elif which == 3:
            # make platform faster
            self.platform.speedup()

        elif which == 4:
            # make platform slower
            self.platform.slowdown()

    def powerup_collision_check(self, powerup):
        if (    powerup.y() + powerup.height > self.game_height - self.platform.height
            and powerup.y() + powerup.height < self.game_height
            and powerup.x() < self.platform.center_x + self.platform.platform_radius
            and powerup.x() + powerup.width > self.platform.center_x - self.platform.platform_radius):
            # pickup the powerup
            self.use_powerup(powerup.power)
            return True
        if powerup.y() + powerup.height > self.game_height:
            return True
        
        return False

    def end(self):

        if len(self.balls) == 0:
            self.on = False
        sum = 0
        for block in self.elements:
            sum += block.end
        
        if sum == len(self.elements):
            self.on = False

    def step(self):
        
        self.end()

        # here the game calculates next game state
        for block in self.elements:
            block.step()

        for object in self.balls:
            object.step()

        i = 0
        while i < len(self.powerups):
            self.powerups[i].step()
            if self.powerup_collision_check(self.powerups[i]):
                ob = self.view.itemAt(int(self.powerups[i].x() + self.block_size/2), int(self.powerups[i].y() + self.block_size/2))
                if ob.__str__() == "1":
                    self.scene.removeItem(ob)
                self.powerups.pop(i)
            i += 1
        
        for ball in self.balls:
            self.ball_collision_check(ball)

        rm = []
        for i, ball in enumerate(self.balls):
            if ball.y() > self.game_height:
                rm.append(i)
                ob = self.view.itemAt(int(ball.x() + ball.radius), int(ball.y() + ball.radius))
                if ob.__str__() == "2":
                    self.scene.removeItem(ob)
        for i in reversed(rm):
            self.balls.pop(i)

        self.platform.step(self.desired_position)


class Main_window(QMainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.form_widget = Breakout() 
        self.setCentralWidget(self.form_widget) 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Main_window()
    w.show()
    app.exec()