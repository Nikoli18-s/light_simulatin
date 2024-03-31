import numpy as np
import numba as nb
from numba import uint8, float32
from numba.experimental import jitclass
import typing as pt
import math

spec = [
    ('position', float32[:, :]),
    ('velocity', float32[:, :]),
    ('width', uint8),
    ('height', uint8),
    ('wall_type', nb.types.string),
    ('step', uint8),
    ('sin_list_x', nb.types.List(uint8)),
    ('sin_list_y', nb.types.List(uint8)),
    ('sin_list_amp', nb.types.List(float32)),
    ('sin_list_freq', nb.types.List(float32)),
    ('sin_list_start_phase', nb.types.List(float32))
]

@jitclass(spec)
class Field(object):
    def __init__(self, width, height, wall_type):
        self.position = np.zeros((height, width), dtype=np.float32)
        self.velocity = np.zeros((height, width), dtype=np.float32)
        self.width = width
        self.height = height
        self.wall_type = wall_type
        self.step = 0

        self.sin_list_x = [uint8(1)]
        self.sin_list_y = [uint8(1)]
        self.sin_list_amp = [float32(1)]
        self.sin_list_freq = [float32(1)]
        self.sin_list_start_phase = [float32(1)]

        self.sin_list_x.clear()
        self.sin_list_y.clear()
        self.sin_list_amp.clear()
        self.sin_list_freq.clear()
        self.sin_list_start_phase.clear()

    def set_cell(self, x, y, position, velocity):
        self.position[y][x] = position
        self.velocity[y][x] = velocity

    def set_sin_cell(self, x, y, amp, freq, start_phase):
        self.sin_list_x.append(uint8(x))
        self.sin_list_y.append(uint8(y))
        self.sin_list_amp.append(float32(amp))
        self.sin_list_freq.append(float32(freq))
        self.sin_list_start_phase.append(float32(start_phase))

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

        if self.wall_type == "absorbing":
            if x == 0:
                sum += -self.position[y][x + 1]
                sum += self.position[y][x + 1]
            elif x == self.width-1:
                sum += -self.position[y][x - 1]
                sum += self.position[y][x - 1]
            else:
                sum += self.position[y][x + 1]
                sum += self.position[y][x - 1]

            if y == 0:
                sum += -self.position[y+1][x]
                sum += self.position[y+1][x]
            elif y == self.height-1:
                sum += -self.position[y - 1][x]
                sum += self.position[y - 1][x]
            else:
                sum += self.position[y - 1][x]
                sum += self.position[y + 1][x]

        return sum/4

    def update(self):
        self.step += 1

        for y in range(self.height):
            for x in range(self.width):
                add_velocity = (self.mean_position_around(x, y) - self.position[y][x])/1.0
                self.velocity[y][x] += add_velocity

        self.position += self.velocity

        for i in range(len(self.sin_list_x)):
            x = self.sin_list_x[i]
            y = self.sin_list_y[i]
            amp = self.sin_list_amp[i]
            freq = self.sin_list_freq[i]
            start_phase = self.sin_list_start_phase[i]
            pos = amp*math.sin(freq*self.step/30 + start_phase)

            self.set_cell(x, y, pos, 0)


