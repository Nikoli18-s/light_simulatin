import PySimpleGUI as sg
import numpy as np
import time
from io import BytesIO
from PIL import Image


class GUI:
    def __init__(self, field):
        # system
        self.fps = 30
        self.prev_id = -1

        # colors
        self.base_color = '#000000'

        # theme
        sg.theme('DarkGrey10')

        # screen elements
        self.graph_width = 675
        self.graph_height = 675
        self.graph = sg.Graph(key='GRAPH', background_color=self.base_color,
                              canvas_size=(self.graph_width, self.graph_height),
                              graph_bottom_left=(0, 0), graph_top_right=(field.width, field.height),
                              pad=(10, 10), enable_events=True, drag_submits=True, visible=True)

        layout = [[sg.Text('Test')],
                  [self.graph]]

        self.window = sg.Window('Light simulation', layout, size=(1280, 720))

    def run(self, field):
        while True:
            event, values = self.window.read(timeout=0)

            # print(event, values)

            # process events
            if event == sg.WIN_CLOSED:
                break

            self._draw_accumulated_field(field)
            field.update()
            time.sleep(1.0/self.fps)

            # end
        self.window.close()

    def _get_cell_color(self, field, x, y):
        val_r = field.position[y][x][0]
        val_g = field.position[y][x][1]
        val_b = field.position[y][x][2]

        if abs(val_r) >= 1.0:
            R = 255
        else:
            brightness = int(255 * abs(val_r))
            R = brightness

        if abs(val_g) >= 1.0:
            G = 255
        else:
            brightness = int(255 * abs(val_g))
            G = brightness

        if abs(val_r) >= 1.0:
            B = 255
        else:
            brightness = int(255 * abs(val_b))
            B = brightness

        return R, G, B

    def _get_accumulated_cell_color(self, field, x, y):
        val_r = field.accumulated_light[y][x][0] / 200
        val_g = field.accumulated_light[y][x][1] / 200
        val_b = field.accumulated_light[y][x][2] / 200

        if abs(val_r) >= 1.0:
            R = 255
        else:
            brightness = int(255 * abs(val_r))
            R = brightness

        if abs(val_g) >= 1.0:
            G = 255
        else:
            brightness = int(255 * abs(val_g))
            G = brightness

        if abs(val_r) >= 1.0:
            B = 255
        else:
            brightness = int(255 * abs(val_b))
            B = brightness

        return R, G, B

    def _get_n_cell_color(self, field, x, y):
        val = field.n[y][x]

        if val == 1.0:
            # color = "#ffffff"
            R = 0
            G = 0
            B = 0
        else:
            R = 50
            G = 60
            B = 70

        return R, G, B

    def _draw_field(self, field):
        nx = field.width
        ny = field.height

        data = np.zeros((ny, nx, 3), dtype=np.uint8)

        for x in range(nx):
            for y in range(ny):

                R, G, B = self._get_cell_color(field, x, y)
                R_n, G_n, B_n = self._get_n_cell_color(field, x, y)

                if R + R_n <= 255:
                    data[y][x][0] = R + R_n
                else:
                    data[y][x][0] = 255

                if G + G_n <= 255:
                    data[y][x][1] = G + G_n
                else:
                    data[y][x][1] = 255

                if B + B_n <= 255:
                    data[y][x][2] = B + B_n
                else:
                    data[y][x][2] = 255

        img = Image.fromarray(data, 'RGB')
        img = img.resize((self.graph_width, self.graph_height))

        with BytesIO() as output:
            img.save(output, format="PNG")
            img_bytes = output.getvalue()

        id = self.window['GRAPH'].draw_image(data=img_bytes, location=(0, ny))

        if self.prev_id >= 0:
            self.window['GRAPH'].delete_figure(self.prev_id)
            self.prev_id = id
        else:
            self.prev_id = id

    def _draw_accumulated_field(self, field):
        if field.step % 5 == 1:
            nx = field.width
            ny = field.height

            data = np.zeros((ny, nx, 3), dtype=np.uint8)

            for x in range(nx):
                for y in range(ny):

                    R, G, B = self._get_accumulated_cell_color(field, x, y)
                    R_n, G_n, B_n = self._get_n_cell_color(field, x, y)

                    if R + R_n <= 255:
                        data[y][x][0] = R + R_n
                    else:
                        data[y][x][0] = 255

                    if G + G_n <= 255:
                        data[y][x][1] = G + G_n
                    else:
                        data[y][x][1] = 255

                    if B + B_n <= 255:
                        data[y][x][2] = B + B_n
                    else:
                        data[y][x][2] = 255

            img = Image.fromarray(data, 'RGB')
            img = img.resize((self.graph_width, self.graph_height))

            with BytesIO() as output:
                img.save(output, format="PNG")
                img_bytes = output.getvalue()

            id = self.window['GRAPH'].draw_image(data=img_bytes, location=(0, ny))

            if self.prev_id >= 0:
                self.window['GRAPH'].delete_figure(self.prev_id)
                self.prev_id = id
            else:
                self.prev_id = id
