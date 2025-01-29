import tkinter as tk
from tkinter import Listbox, Button
from windows import CopyTextWindow

class GridCanvas:
    def __init__(self, root, cell_size=20):
        self.root = root
        self.cell_size = cell_size
        self.canvas = tk.Canvas(root, width=600, height=600, bg="white")
        self.canvas.pack(side=tk.RIGHT) 

        # Frame for the line and point list
        self.sidebar = tk.Frame(root, width=200, bg="lightgray")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.line_listbox = Listbox(self.sidebar, height=20)
        self.line_listbox.pack(pady=10, padx=10, fill=tk.X)

        self.point_listbox = Listbox(self.sidebar, height=10)
        self.point_listbox.pack(pady=10, padx=10, fill=tk.X)

        self.export_button = Button(self.sidebar, text="Export", command=self.export)
        self.export_button.pack(pady=10, padx=10, fill=tk.X)
        
        self.draw_grid()

        self.lines = []  # Store all lines (as list of points)
        self.current_line = []  # Points in the current line being drawn
        self.selected_line_index = None
        self.selected_point_index = None
        self.moving_point = False

        # Event bindings
        self.canvas.bind("<Motion>", self.preview_line)
        self.canvas.bind("<Button-1>", self.start_line)
        self.root.bind("<Escape>", self.finish_line)
        self.root.bind("d", self.delete_selected_point)
        self.root.bind("m", self.toggle_move_point)
        self.line_listbox.bind("<<ListboxSelect>>", self.select_line)
        self.point_listbox.bind("<<ListboxSelect>>", self.select_point)

        # Store the current highlighted oval and preview line
        self.highlighted_oval = None
        self.preview_line_id = None

    def draw_grid(self):
        """Draw the grid on the canvas."""
        width = int(self.canvas['width'])
        height = int(self.canvas['height'])

        for x in range(0, width, self.cell_size):
            self.canvas.create_line(x, 0, x, height, fill="lightgray")
        for y in range(0, height, self.cell_size):
            self.canvas.create_line(0, y, width, y, fill="lightgray")

    def get_snapped_coordinates(self, event):
        """Get the coordinates snapped to the nearest grid point."""
        x = round(event.x / self.cell_size) * self.cell_size
        y = round(event.y / self.cell_size) * self.cell_size
        return x, y

    def preview_line(self, event):
        """Preview the line to the nearest intersection."""
        x, y = self.get_snapped_coordinates(event)

        # If moving a point, update its position
        if self.moving_point and self.selected_line_index is not None and self.selected_point_index is not None:
            self.lines[self.selected_line_index][self.selected_point_index] = (x, y)
            self.redraw_lines()
            self.update_point_list()

        # Remove the previously highlighted oval
        if self.highlighted_oval:
            self.canvas.delete(self.highlighted_oval)

        # Draw a new oval to highlight the intersection
        self.highlighted_oval = self.canvas.create_oval(
            x - 5, y - 5, x + 5, y + 5, fill="red"
        )

        # Preview the line from the last point to the current cursor location
        if self.current_line:
            last_x, last_y = self.current_line[-1]

            # Remove the old preview line
            if self.preview_line_id:
                self.canvas.delete(self.preview_line_id)

            # Draw the new preview line
            self.preview_line_id = self.canvas.create_line(
                last_x, last_y, x, y, fill="blue", dash=(4, 2)
            )

    def start_line(self, event):
        """Start or extend a line when left mouse button is clicked."""
        x, y = self.get_snapped_coordinates(event)
        
        if not self.moving_point:
            if not self.current_line:
                # Start a new line
                self.current_line.append((x, y))
            else:
                # Extend the line
                last_x, last_y = self.current_line[-1]
                self.canvas.create_line(last_x, last_y, x, y, fill="blue", width=2)
                self.current_line.append((x, y))
        else:
            self.moving_point = False

        self.update_point_list()

    def finish_line(self, event):
        """Finish the current line when Escape key is pressed."""
        if self.current_line:
            self.lines.append(self.current_line)
            self.update_line_list()

        if self.preview_line_id:
            self.canvas.delete(self.preview_line_id)
            self.preview_line_id = None

        if self.highlighted_oval:
            self.canvas.delete(self.highlighted_oval)
            self.highlighted_oval = None
        
        if self.moving_point:
            self.moving_point = False

        print("Line finished:", self.current_line)
        self.current_line = []

    def update_line_list(self):
        """Update the list of lines in the sidebar."""
        self.line_listbox.delete(0, tk.END)
        for i, line in enumerate(self.lines):
            self.line_listbox.insert(tk.END, f"Line {i+1}: {len(line)} points")

    def update_point_list(self):
        """Update the list of points for the selected line or current line."""
        self.point_listbox.delete(0, tk.END)
        for x, y in self.current_line:
            self.point_listbox.insert(tk.END, f"({x}, {y})")

    def select_line(self, event):
        """Select a line from the list and display its points."""
        selection = self.line_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_line_index = index
            self.current_line = self.lines[index]
            self.update_point_list()

    def select_point(self, event):
        """Select a point in the selected line."""
        selection = self.point_listbox.curselection()
        if selection and self.selected_line_index is not None:
            self.selected_point_index = selection[0]
            print(f"Selected Point: {self.lines[self.selected_line_index][self.selected_point_index]}")

    def delete_selected_point(self, event):
        """Delete the selected point from the line."""
        if self.selected_line_index is not None and self.selected_point_index is not None:
            del self.lines[self.selected_line_index][self.selected_point_index]
            self.selected_point_index = None
            self.redraw_lines()
            self.update_point_list()
            print("Point deleted.")

    def toggle_move_point(self, event):
        """Toggle the movement mode for the selected point."""
        if self.moving_point:
            self.moving_point = False
            print("Stopped moving the point.")
        elif self.selected_line_index is not None and self.selected_point_index is not None:
            self.moving_point = True
            print("Started moving the point.")
        else:
            print("oh no moving", self.selected_line_index, self.selected_point_index)

    def export(self):
        end_point = [0, 0]
        modificator = None
        commands = []
        block_lines = []
        for line in self.lines:
            new_line = []
            for dot in line:
                if not modificator:
                    modificator = [end_point[0] - dot[0] / self.cell_size, end_point[1] - dot[1] / self.cell_size]
                new_line.append([(dot[0] / self.cell_size + modificator[0])*-1, dot[1] / self.cell_size + modificator[1]])
            block_lines.append(new_line)
        
        line_started = False
        for line in block_lines:
            for dot in line:
                commands.append(f"сместиться на вектор ({end_point[0] - dot[0]}, {end_point[1] - dot[1]})")
                if not line_started:
                    commands.append("опустить перо")
                    line_started = True
                end_point = dot
            line_started = False
            commands.append("поднять перо")
        text = "\n".join(commands)
        twindow = CopyTextWindow(self.root, text)
    
    def redraw_lines(self):
        """Redraw all lines on the canvas."""
        self.canvas.delete("all")
        self.draw_grid()
        for line in self.lines:
            if len(line) > 1:
                for i in range(len(line) - 1):
                    x1, y1 = line[i]
                    x2, y2 = line[i + 1]
                    self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
        

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Grid Canvas with Intersections and Lines")
    app = GridCanvas(root)
    root.mainloop()
