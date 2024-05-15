from GUI import GUI
from logic import Field
import math

field = Field(200, 200, "absorbing")

field.set_sin_cell(10, 110, 1.0, 10.0, 0.0)
field.set_sin_cell(10, 90, 1.0, 10.0, 0.0)
field.set_rect_cells_n(70, 100, 100, 199, 0.5)
# field.set_sin_cell(10, 69, 2.0, 10.0, 0.0)
# field.set_sin_cell(15, 69, 2.0, 10.0, math.pi)
# field.set_sin_cell(10, 73, 2.0, 10.0, math.pi)
# field.set_sin_cell(15, 73, 2.0, 10.0, 0.0)
# field.set_rect_sin_cells(20, 20, 0, 141, 0.5, 1.0, 10.0)

# field.set_line_cells_n(40, 40, 0, 51, 0.01)
# field.set_line_cells_n(40, 40, 61, 81, 0.01)
# field.set_line_cells_n(40, 40, 91, 141, 0.01)

# field.set_circle_sin_cells(20, 71, 5, 90, 10, 1, 10)
# field.set_circle_sin_cells(101, 71, 5, 90, 10, -1, 10)

gui = GUI(field)
gui.run(field)




