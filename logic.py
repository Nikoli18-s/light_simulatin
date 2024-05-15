import numpy as np
import numba as nb
from numba import uint8, uint32, float32
from numba.experimental import jitclass
import math

spec = [
    ('position', float32[:, :, :]),
    ('velocity', float32[:, :, :]),
    ('accumulated_light', float32[:, :, :]),
    ('n', float32[:, :]),
    ('width', uint32),
    ('height', uint32),
    ('wall_type', nb.types.string),
    ('step', uint32),
    ('disperse', nb.types.List(float32)),
    ('sin_list_x', nb.types.List(uint32)),
    ('sin_list_y', nb.types.List(uint32)),
    ('sin_list_c', nb.types.List(uint32)),
    ('sin_list_amp', nb.types.List(float32)),
    ('sin_list_freq', nb.types.List(float32)),
    ('sin_list_start_phase', nb.types.List(float32))
]


@jitclass(spec)
class Field(object):
    def __init__(self, width, height, wall_type):
        self.position = np.zeros((height, width, 3), dtype=np.float32)
        self.velocity = np.zeros((height, width, 3), dtype=np.float32)
        self.accumulated_light = np.zeros((height, width, 3), dtype=np.float32)
        self.n = np.zeros((height, width), dtype=np.float32)
        self.width = width
        self.height = height
        self.wall_type = wall_type
        self.step = 1

        self.disperse = [float32(0.02), float32(0.0), float32(-0.04)]

        self.sin_list_x = [uint32(1)]
        self.sin_list_y = [uint32(1)]
        self.sin_list_c = [uint32(1)]
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

    def _set_cell(self, x, y, c, position, velocity):
        self.position[y][x][c] = position
        self.velocity[y][x][c] = velocity

    def _set_cell_n(self, x, y, n):
        self.n[y][x] = n

    def _set_sin_cell(self, x, y, c, amp, freq, start_phase):
        self.sin_list_x.append(uint32(x))
        self.sin_list_y.append(uint32(y))
        self.sin_list_c.append(uint32(c))
        self.sin_list_amp.append(float32(amp))
        self.sin_list_freq.append(float32(freq))
        self.sin_list_start_phase.append(float32(start_phase))

    def set_line_cells_n(self, x0, x1, y0, y1, n):
        for y in range(self.height):
            for x in range(self.width):
                if x0 <= x <= x1 and y0 <= y <= y1:
                    l = math.sqrt((x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0))

                    A = (y1 - y0) / l
                    B = -(x1 - x0) / l
                    C = -B * y0 - A * x0

                    d = abs(A * x + B * y + C)

                    if d <= 1:
                        self._set_cell_n(x, y, n)

    def set_rect_cells_n(self, x0, x1, y0, y1, n):
        for y in range(self.height):
            for x in range(self.width):
                if x0 <= x <= x1 and y0 <= y <= y1:
                    self._set_cell_n(x, y, n)

    def set_rect_sin_cells(self, x0, x1, y0, y1, k, amp, freq):
        for y in range(self.height):
            for x in range(self.width):
                for c in range(3):
                    if x0 <= x <= x1 and y0 <= y <= y1:
                        self._set_sin_cell(x, y, c, amp, freq, k * x)

    def set_circle_cells_n(self, center_x, center_y, r, n):
        for y in range(self.height):
            for x in range(self.width):
                dist_sqr = (x - center_x) * (x - center_x) + (y - center_y) * (y - center_y)
                if dist_sqr <= r * r:
                    self._set_cell_n(x, y, n)

    def set_linse(self, x_flat, y_flat, r, thin):
        n = 0.5
        center_x = x_flat + thin - r
        center_y = y_flat
        for y in range(self.height):
            for x in range(self.width):
                dist_sqr = (x - center_x) * (x - center_x) + (y - center_y) * (y - center_y)
                if dist_sqr <= r * r:
                    if x >= x_flat:
                        self._set_cell_n(x, y, n)

    def set_circle_sin_cells(self, center_x, center_y, r, direction_angle, k, amp, freq):
        for y in range(self.height):
            for x in range(self.width):
                for c in range(3):
                    dist_sqr = (x - center_x) * (x - center_x) + (y - center_y) * (y - center_y)

                    if dist_sqr <= r * r:
                        alpha = math.pi * direction_angle / 180
                        A = math.sin(alpha)
                        B = math.cos(alpha)
                        C = math.sin(alpha) * center_x + math.cos(alpha) * center_y

                        dr = A * x + B * y + C
                        self.set_sin_cell(x, y, c, amp, freq, k * dr)

    def mean_position_around(self, x, y, c):
        sum = 0

        sum += self.position[y][x + 1][c]
        sum += self.position[y][x - 1][c]
        sum += self.position[y - 1][x][c]
        sum += self.position[y + 1][x][c]

        return sum / 4

    def update(self):
        self.step += 1

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                for c in range(3):
                    add_velocity = (self.mean_position_around(x, y, c) - self.position[y][x][c]) * (self.n[y][x] + self.disperse[c])
                    self.velocity[y][x][c] += add_velocity

        for c in range(3):
            if self.wall_type == "absorbing":
                for y in range(self.height):
                    self.velocity[y][0][c] = -self.velocity[y][1][c]
                    self.position[y][0][c] = (self.position[y][1][c] + self.position[y][2][c]) / 2
                    self.velocity[y][self.width - 1][c] = -self.velocity[y][self.width - 2][c]
                    self.position[y][self.width - 1][c] = (self.position[y][self.width - 2][c] +
                                                           self.position[y][self.width - 3][c]) / 2

                for x in range(1, self.width - 1):
                    self.velocity[0][x][c] = -self.velocity[1][x][c]
                    self.position[0][x][c] = (self.position[1][x][c] + self.position[2][x][c]) / 2
                    self.velocity[self.height - 1][x][c] = -self.velocity[self.height - 2][x][c]
                    self.position[self.height - 1][x][c] = (self.position[self.height - 2][x][c] +
                                                            self.position[self.height - 3][x][c]) / 2
            elif self.wall_type == "reflecting":
                for y in range(self.height):
                    self.velocity[y][0][c] = 0
                    self.position[y][0][c] = 0
                    self.velocity[y][self.width - 1][c] = 0
                    self.position[y][self.width - 1][c] = 0

                for x in range(1, self.width - 1):
                    self.velocity[0][x][c] = 0
                    self.position[0][x][c] = 0
                    self.velocity[self.height - 1][x][c] = 0
                    self.position[self.height - 1][x][c] = 0
            else:
                pass

        self.position += self.velocity

        for y in range(self.height):
            for x in range(self.width):
                for c in range(3):
                    self.accumulated_light[y][x][c] += self.position[y][x][c] * self.position[y][x][c]

        for i in range(len(self.sin_list_x)):
            x = self.sin_list_x[i]
            y = self.sin_list_y[i]
            c = self.sin_list_c[i]
            amp = self.sin_list_amp[i]
            freq = self.sin_list_freq[i]
            start_phase = self.sin_list_start_phase[i]
            pos = amp * math.sin(freq * self.step / 30 + start_phase)

            self._set_cell(x, y, c, pos, 0)
