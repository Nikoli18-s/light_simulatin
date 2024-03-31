import PySimpleGUI as sg
import time


class GUI:
    def __init__(self):
        # system
        self.fps = 30
        self.buff_size = 20000

        # colors
        self.base_color = '#000000'

        # theme
        sg.theme('DarkGrey10')

        # screen elements
        self.graph_width = 1012
        self.graph_height = 675
        self.scale = 0.9
        self.graph = sg.Graph(key='GRAPH', background_color=self.base_color,
                              canvas_size=(int(self.graph_width*self.scale), int(self.graph_height*self.scale)),
                              graph_bottom_left=(0, 0), graph_top_right=(self.graph_width, self.graph_height),
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

            self.draw_field(field)
            field.update()
            time.sleep(1.0/self.fps)

            # end
        self.window.close()

    def get_cell_color(self, field, x, y):
        val = field.position[y][x]

        if abs(val) >= 1.0:
            color = "#ffffff"
        else:
            brightness = int(255*abs(val))
            if brightness >= 16:
                color = "#" + str(hex(brightness))[2:] + str(hex(brightness))[2:] + str(hex(brightness))[2:]
            else:
                color = "#0" + str(hex(brightness))[2:] + "0" + str(hex(brightness))[2:] + "0" + str(hex(brightness))[2:]

        return color

    def draw_cell(self, field, x, y, cell_width, cell_height):
        color = self.get_cell_color(field, x, y)
        x_px = x * cell_width
        y_px = y * cell_height

        if color != "#000000":
            ids = self.window['GRAPH'].draw_rectangle((x_px, y_px + cell_height), (x_px + cell_width, y_px),
                                            fill_color=color, line_color=color, line_width=0)

            if ids >= self.buff_size:
                del_ID = ids - self.buff_size
                self.window['GRAPH'].delete_figure(del_ID)

    def draw_field(self, field):
        nx = field.width
        ny = field.height

        cell_width = self.graph_width // nx
        cell_height = self.graph_height // ny

        for x in range(nx):
            for y in range(ny):
                self.draw_cell(field, x, y, cell_width, cell_height)
