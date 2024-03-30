import PySimpleGUI as sg


class GUI:
    def __init__(self):
        # theme
        sg.theme('DarkGrey10')

        layout = [[sg.Text('Test')]]

        self.window = sg.Window('Light simulation', layout, size=(1280, 720))

    def run(self):
        while True:
            event, values = self.window.read(timeout=200)

            # print(event, values)

            # process events
            if event == sg.WIN_CLOSED:
                break
        # end
        self.window.close()

    def enable_cell(self, cell_px, x, y, shift_x, shift_y):
        pass

    def disable_cell(self, cell_px, x, y, shift_x, shift_y):
        pass

    def draw_field(self):
        pass