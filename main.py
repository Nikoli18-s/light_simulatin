from GUI import GUI
from logic import Field

field = Field(151, 101, "absorbing")
field.set_sin_cell(76, 51, 1.0, 10.0, 0.0)
# field.set_circle_sin_cells(76+10, 51, 5, 90, 10, 1, 10)
# field.set_circle_sin_cells(76-10, 51, 5, 90, 10, -1, 10)

gui = GUI()
gui.run(field)




