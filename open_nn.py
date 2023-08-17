import random
import time
import tkinter as tk
import math
from copy import deepcopy as copy
from neuro import NeuralNetwork
import datetime
import matplotlib.pyplot as plt


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        new = Vector(self.x + other.x, self.y + other.y)
        return new

    def __mul__(self, other):
        new = Vector(self.x * other, self.y * other)
        return new

    def __sub__(self, other):
        new = Vector(self.x - other.x, self.y - other.y)
        return new

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def length(self):
        return (self.x**2 + self.y**2) ** 0.5


def calculate_edge_normal(point1, point2):
    point1 = (point1.x, point1.y)
    point2 = (point2.x, point2.y)
    edge_vector = [point2[0] - point1[0], point2[1] - point1[1]]
    edge_length = (edge_vector[0] ** 2 + edge_vector[1] ** 2) ** 0.5

    if edge_length == 0:
        raise ValueError("The edge has zero length.")

    normalized_edge_vector = [edge_vector[0] / edge_length, edge_vector[1] / edge_length]
    normal_vector = Vector(-normalized_edge_vector[1], normalized_edge_vector[0])
    return normal_vector


fuckingpoint = Vector(0,0)


def lines_intersect(line1, line2, is_fuckingpoint=False):
    global fuckingpoint
    x1, y1, x2, y2 = line1[0].x, line1[0].y, line1[1].x, line1[1].y
    x3, y3, x4, y4 = line2[0].x, line2[0].y, line2[1].x, line2[1].y

    # Calculate slopes
    slope1 = (y2 - y1) / (x2 - x1) if x2 - x1 != 0 else float('inf')
    slope2 = (y4 - y3) / (x4 - x3) if x4 - x3 != 0 else float('inf')

    # Check if lines are parallel
    if slope1 == slope2:
        return False

    if slope1 == float('inf'):  # Line 1 is vertical
        x = x1
        y = slope2 * (x - x3) + y3
    elif slope2 == float('inf'):  # Line 2 is vertical
        x = x3
        y = slope1 * (x - x1) + y1
    else:
        x = (slope1 * x1 - slope2 * x3 + y3 - y1) / (slope1 - slope2)
        y = slope1 * (x - x1) + y1

    if is_fuckingpoint:
        fuckingpoint = Vector(x, y)
    # Check if intersection point lies on both line segments
    if ((x1 <= x <= x2 or x2 <= x <= x1) and
        (x3 <= x <= x4 or x4 <= x <= x3)) and \
            ((y1 <= y <= y2 or y2 <= y <= y1) and
             (y3 <= y <= y4 or y4 <= y <= y3)):
        return True

    return False


G = Vector(0, .1)
LOSS = 1

class Ball:
    def __init__(self, x, y, radius):
        self.pos = Vector(x, y)
        self.radius = radius
        self.movement = Vector(0, 1)
        self.collide = False
        self.weight = 1

    def next_frame(self, edges, balls):

        collide = False
        for i, ball in enumerate(balls):
            line = [self.pos, ball.pos]
            length = math.sqrt((line[1].x - line[0].x)**2 + (line[1].y - line[0].y)**2)
            if length <= ball.radius + self.radius:
                line[0] = line[0]
                line[1] = line[1]
                v = line[1] - line[0]
                v *= 1/length
                self.movement = -v * self.movement.length()


        normals = []
        intersect = []

        for i, edge in enumerate(edges):
            normal = calculate_edge_normal(edge[0], edge[1])
            normals.append(normal)
            height = (self.pos, self.pos + (normal * self.radius))

            intersect.append(lines_intersect(edge, height, i == 0))

        if intersect[0] and intersect[1]:
            if (intersect[0] - self.pos).lenght() <= (intersect[1] - self.pos).lenght():
                self.movement = (normals[0] * self.movement.length()) * -LOSS * self.weight
                self.pos -= normals[0]
            else:
                self.movement = (normals[1] * self.movement.length()) * -LOSS * self.weight
                self.pos -= normals[1]

        elif intersect[0]:
            self.movement = (normals[0] * self.movement.length()) * -LOSS * self.weight
            self.pos -= normals[0]

        elif intersect[1]:
            self.movement = (normals[1] * self.movement.length()) * -LOSS * self.weight
            self.pos -= normals[1]

        if intersect[2] and intersect[3]:
            if (intersect[2] - self.pos).lenght() <= (intersect[3] - self.pos).lenght():
                self.movement = (normals[2] * self.movement.length()) * -LOSS * self.weight
                self.pos -= normals[2]
            else:
                self.movement = (normals[3] * self.movement.length()) * -LOSS * self.weight
                self.pos -= normals[3]

        elif intersect[2]:
            self.movement = (normals[2] * self.movement.length()) * -LOSS * self.weight
            self.pos -= normals[2]

        elif intersect[3]:
            self.movement = (normals[3] * self.movement.length()) * -LOSS * self.weight
            self.pos -= normals[3]

        self.collide = any(intersect)
        self.movement += G*self.weight
        self.pos += self.movement


pause = False

class Platform:
    def __init__(self, x, y, height, width, rotate):
        self.pos = Vector(x, y)
        self.height = height
        self.width = width
        self.rotate = rotate


class RotatingRectangleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rotate Rectangle")

        self.canvas = tk.Canvas(root, width=1280, height=1280)
        self.canvas.pack()

        self.rectangle = Platform(1280//2, 1280//2+300, 10, 800, 0)
        self.ball = Ball(1280//2 + random.randint(-200, 200), 1280//2, 25)
        self.ball1 = Ball(1280//2 + random.randint(-200, 200), 1280//2, 25)
        self.drawing_rectangle = self.canvas.create_rectangle(self.rectangle.pos.x, self.rectangle.pos.y, self.rectangle.width, self.rectangle.height, outline='red', fill='red', width=2)
        self.root.bind("<Right>", self.rotate_right)  # Bind right arrow key
        self.root.bind("<Left>", self.rotate_left)
        self.root.bind("<Up>", self.set_pause)
        self.root.bind("<B1-Motion>", self.set_pos_ball)
        self.root.bind("<B3-Motion>", self.set_pos_ball1)

    def set_pos_ball(self, event):
        self.ball.pos = Vector(event.x, event.y)
        self.ball.movement = Vector(0, 0)

    def set_pos_ball1(self, event):
        self.ball1.pos = Vector(event.x, event.y)
        self.ball.movement = Vector(0, 0)

    def rotate_right(self, event):
        self.rectangle.rotate = self.rectangle.rotate + 1

    def set_pause(self, event):
        global pause
        pause = not pause

    def rotate_left(self, event):
        self.rectangle.rotate = self.rectangle.rotate - 1  # Rotate by 15 degrees each time

    def draw_rectangle(self):
        center_x = self.rectangle.pos.x
        center_y = self.rectangle.pos.y

        angle_rad = math.radians(self.rectangle.rotate)

        corner_coords = [
            self.rotate_point(self.rectangle.pos.x - self.rectangle.width/2, self.rectangle.pos.y - self.rectangle.height/2, center_x, center_y, angle_rad),
            self.rotate_point(self.rectangle.pos.x + self.rectangle.width/2, self.rectangle.pos.y - self.rectangle.height/2, center_x, center_y, angle_rad),
            self.rotate_point(self.rectangle.pos.x + self.rectangle.width/2, self.rectangle.pos.y + self.rectangle.height/2, center_x, center_y, angle_rad),
            self.rotate_point(self.rectangle.pos.x - self.rectangle.width/2, self.rectangle.pos.y + self.rectangle.height/2, center_x, center_y, angle_rad)
        ]

        edges = [(Vector(corner_coords[i%4][0], corner_coords[i%4][1]), Vector(corner_coords[(i+1)%4][0], corner_coords[(i+1)%4][1])) for i in range(4)]

        self.drawing_rectangle = self.canvas.create_polygon(corner_coords, outline='red', fill='red', width=2)
        return edges

    def draw_ball(self):
        coords = [
            (self.ball.pos.x - self.ball.radius, self.ball.pos.y - self.ball.radius),
            (self.ball.pos.x + self.ball.radius, self.ball.pos.y + self.ball.radius),
        ]

        self.canvas.create_oval(coords, outline='black', fill='', width=2)

        coords = [
            (self.ball1.pos.x - self.ball1.radius, self.ball1.pos.y - self.ball1.radius),
            (self.ball1.pos.x + self.ball1.radius, self.ball1.pos.y + self.ball1.radius),
        ]

        self.canvas.create_oval(coords, outline='black', fill='', width=2)

    def rotate_point(self, x, y, cx, cy, angle_rad):
        new_x = cx + (x - cx) * math.cos(angle_rad) - (y - cy) * math.sin(angle_rad)
        new_y = cy + (x - cx) * math.sin(angle_rad) + (y - cy) * math.cos(angle_rad)
        return new_x, new_y

    def clear_canvas(self):
        self.canvas.delete("all")

nn = NeuralNetwork.open(input('file name:'))
print(nn.weights)
while True:
    root = tk.Tk()
    app = RotatingRectangleApp(root)
    start_time = datetime.datetime.now()
    frames_count = -1
    while 0 <= app.ball.pos.x <= 1280 and 0 <= app.ball.pos.y <= 1280 and 0 <= app.ball1.pos.x <= 1280 and 0 <= app.ball1.pos.y <= 1280:
        frames_count += 1
        #app.rectangle.rotate = math.cos(app.rectangle.rotate)*360
        edges = app.draw_rectangle()
        app.ball.next_frame(edges, [app.ball1])
        app.ball1.next_frame(edges, [app.ball])
        app.canvas.create_oval(fuckingpoint.x - 10, fuckingpoint.y - 10, fuckingpoint.x+10, fuckingpoint.y+10, fill='blue', width=2)
        input = [app.rectangle.rotate/360, app.rectangle.pos.x/1280, app.rectangle.pos.y/1280, app.ball.pos.x/1280, app.ball.pos.y/1280, app.ball.movement.x, app.ball.movement.y, app.ball1.pos.x/1280, app.ball1.pos.y/1280, app.ball1.movement.x, app.ball1.movement.y]
        formatted_input = [math.tanh(el) for el in input]
        out = nn.out(formatted_input)[-1]
        app.rectangle.rotate = (app.rectangle.rotate + out[0]) % 360
        app.rectangle.pos += Vector(out[1], out[2])
        app.draw_ball()
        root.update()
        time.sleep(0.01)
        app.clear_canvas()
    root.destroy()
    all_time = frames_count

root.mainloop()
