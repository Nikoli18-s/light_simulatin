import numpy as np
import numba as nb
from numba import uint8, uint32, float32
from numba.experimental import jitclass
import math

spec = [
    ('position', float32[:, :]),
    ('velocity', float32[:, :]),
    ('accumulated_light', float32[:, :]),
    ('n', float32[:, :]),
    ('width', uint32),
    ('height', uint32),
    ('wall_type', nb.types.string),
    ('step', uint32),
    ('sin_list_x', nb.types.List(uint32)),
    ('sin_list_y', nb.types.List(uint32)),
    ('sin_list_amp', nb.types.List(float32)),
    ('sin_list_freq', nb.types.List(float32)),
    ('sin_list_start_phase', nb.types.List(float32))
]

@jitclass(spec)
class Field(object):
    def __init__(self, width, height, wall_type):
        self.position = np.zeros((height, width), dtype=np.float32)
        self.velocity = np.zeros((height, width), dtype=np.float32)
        self.accumulated_light = np.zeros((height, width), dtype=np.float32)
        self.n = np.zeros((height, width), dtype=np.float32)
        self.width = width
        self.height = height
        self.wall_type = wall_type
        self.step = 1

        self.sin_list_x = [uint32(1)]
        self.sin_list_y = [uint32(1)]
        self.sin_list_amp = [float32(1)]
        self.sin_list_freq = [float32(1)]
        self.sin_list_start_phase = [float32(1)]

        self.sin_list_x.clear()
        self.sin_list_y.clear()
        self.sin_list_amp.clear()
        self.sin_list_freq.clear()
        self.sin_list_start_phase.clear()

        for y in range(self.height):
            for x in range(self.width):
                self.n[y][x] = 1

    def set_cell(self, x, y, position, velocity):
        self.position[y][x] = position
        self.velocity[y][x] = velocity

    def set_cell_n(self, x, y, n):
        self.n[y][x] = n

    def set_sin_cell(self, x, y, amp, freq, start_phase):
        self.sin_list_x.append(uint32(x))
        self.sin_list_y.append(uint32(y))
        self.sin_list_amp.append(float32(amp))
        self.sin_list_freq.append(float32(freq))
        self.sin_list_start_phase.append(float32(start_phase))

    def set_line_cells_n(self, x0, x1, y0, y1, n):
        for y in range(self.height):
            for x in range(self.width):
                if x0 <= x <= x1 and y0 <= y <= y1:
                    l = math.sqrt((x1 - x0)*(x1 - x0) + (y1 - y0)*(y1 - y0))

                    A = (y1 - y0)/l
                    B = -(x1 - x0)/l
                    C = -B*y0 - A*x0

                    d = abs(A*x + B*y + C)

                    if d <= 1:
                        self.set_cell_n(x, y, n)

    def set_rect_cells_n(self, x0, x1, y0, y1, n):
        for y in range(self.height):
            for x in range(self.width):
                # print(x, y)
                # print(f'{x0} <= {x} <= {x1}', x0 <= x <= x1)
                # print(f'{y0} <= {y} <= {y1}', y0 <= y <= y1)
                # print(self.height)
                # print(self.width)
                if x0 <= x <= x1 and y0 <= y <= y1:
                    self.set_cell_n(x, y, n)

    def set_rect_sin_cells(self, x0, x1, y0, y1, k, amp, freq):
        for y in range(self.height):
            for x in range(self.width):
                if x >= x0 and x <= x1 and y >= y0 and y <= y1:
                    self.set_sin_cell(x, y, amp, freq, k*x)

    def set_circle_cells_n(self, center_x, center_y, r, n):
        for y in range(self.height):
            for x in range(self.width):
                dist_sqr = (x - center_x) * (x - center_x) + (y - center_y) * (y - center_y)
                if dist_sqr <= r * r:
                    self.set_cell_n(x, y, n)

    def set_circle_sin_cells(self, center_x, center_y, r, direction_angle, k, amp, freq):
        for y in range(self.height):
            for x in range(self.width):
                dist_sqr = (x - center_x)*(x - center_x) + (y - center_y)*(y - center_y)

                if dist_sqr <= r*r:
                    alpha = math.pi*direction_angle/180
                    A = math.sin(alpha)
                    B = math.cos(alpha)
                    C = math.sin(alpha)*center_x + math.cos(alpha)*center_y

                    dr = A*x + B*y + C
                    self.set_sin_cell(x, y, amp, freq, k*dr)

    def mean_position_around(self, x, y):
        sum = 0

        sum += self.position[y][x + 1]
        sum += self.position[y][x - 1]
        sum += self.position[y - 1][x]
        sum += self.position[y + 1][x]

        return sum/4

    def update(self):
        self.step += 1

        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                add_velocity = (self.mean_position_around(x, y) - self.position[y][x])*self.n[y][x]
                self.velocity[y][x] += add_velocity

        if self.wall_type == "absorbing":
            for y in range(self.height):
                self.velocity[y][0] = -self.velocity[y][1]
                self.position[y][0] = (self.position[y][1] + self.position[y][2])/2
                self.velocity[y][self.width-1] = -self.velocity[y][self.width-2]
                self.position[y][self.width-1] = (self.position[y][self.width-2] + self.position[y][self.width-3])/2

            for x in range(1, self.width-1):
                self.velocity[0][x] = -self.velocity[1][x]
                self.position[0][x] = (self.position[1][x] + self.position[2][x])/2
                self.velocity[self.height-1][x] = -self.velocity[self.height-2][x]
                self.position[self.height-1][x] = (self.position[self.height-2][x] + self.position[self.height-3][x])/2
        elif self.wall_type == "reflecting":
            for y in range(self.height):
                self.velocity[y][0] = 0
                self.position[y][0] = 0
                self.velocity[y][self.width-1] = 0
                self.position[y][self.width-1] = 0

            for x in range(1, self.width-1):
                self.velocity[0][x] = 0
                self.position[0][x] = 0
                self.velocity[self.height-1][x] = 0
                self.position[self.height-1][x] = 0
        else:
            pass

        self.position += self.velocity

        for y in range(self.height):
            for x in range(self.width):
                self.accumulated_light[y][x] += abs(self.position[y][x])

        for i in range(len(self.sin_list_x)):
            x = self.sin_list_x[i]
            y = self.sin_list_y[i]
            amp = self.sin_list_amp[i]
            freq = self.sin_list_freq[i]
            start_phase = self.sin_list_start_phase[i]
            pos = amp*math.sin(freq*self.step/30 + start_phase)

            self.set_cell(x, y, pos, 0)


