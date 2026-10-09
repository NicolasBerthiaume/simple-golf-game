import tkinter as tk
from tkinter import ttk, simpledialog # anyway to combine these two lines?

from grid import Grid
from tile import TileType

MAIN_FRAME_XYPADDING = 20

BOARD_WIDTH = 20
BOARD_HEIGHT = 25

BOARD_TILE_SIZE = 30
TILE_COLORS = {
    TileType.ROUGH: "#2e7d32",
    TileType.GREEN: "#4caf50",
    TileType.WATER: "#2196f3",
    TileType.SAND: "#f4e1a1",
    TileType.TEE: "#8bc34a",
    TileType.HOLE: "#000000",
}

TARGET_RADIUS = BOARD_TILE_SIZE * 0.2

CONTROLS_EL_PADY = (10, 0)
CONTROLS_EL_FONT = ("Helvetica", 12)

class Window:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Golf")
        self.root.resizable(False, False)

        self.main_frame = tk.Frame(self.root, padx=MAIN_FRAME_XYPADDING, pady=MAIN_FRAME_XYPADDING)
        self.main_frame.pack()

        self.board_frame = tk.Frame(self.main_frame)
        self.board_frame.pack(fill="x")

        self.controls_frame = tk.Frame(self.main_frame)
        self.controls_frame.pack(fill="x")

    def prompt_user(self, dialog_box_title, prompt):
        return simpledialog.askstring(dialog_box_title, prompt, parent=self.root)

    def run(self):
        self.root.mainloop()

class Board():
    def __init__(self, frame):
        self.tile_size = BOARD_TILE_SIZE
        self.canvas = tk.Canvas(
            frame,
            width = BOARD_WIDTH * self.tile_size,
            height = BOARD_HEIGHT * self.tile_size,
        )
        self.canvas.pack()
        self.grid = Grid(BOARD_WIDTH, BOARD_HEIGHT)
        self.targets = {}

    def prepare_board(self, is_new):
        if is_new:
            self.grid.generate_course_data()
        self.draw_course()
        self.initialize_targets()
        self.draw_tee()

    def draw_course(self):
        self.canvas.delete("all")

        for t in self.grid.tile_map.values():
            left = (t.x - 1) * self.tile_size
            top = (t.y - 1) * self.tile_size

            self.canvas.create_rectangle(
                left, top, left + self.tile_size, top + self.tile_size,
                fill=TILE_COLORS[t.type],
                outline=""
            )

    def initialize_targets(self):
        for item in self.targets.values():
            self.canvas.delete(item)
        self.targets = {}

        for _, t in self.grid.tile_map.items():
            if t.type == TileType.WATER:
                continue

            cx, cy = self.get_pixel_at_tile_center(t)

            self.targets[(t.x, t.y)] = self.canvas.create_oval(
                cx - TARGET_RADIUS, cy - TARGET_RADIUS, cx + TARGET_RADIUS, cy + TARGET_RADIUS, outline="white", width=3, fill="", state="hidden",
            )

    def show_targets(self, targets_to_show):
        for target in targets_to_show:
            self.canvas.itemconfig(self.targets[(target.x, target.y)], state="normal")

    def hide_targets(self, targets_to_hide):
        for target in targets_to_hide:
            self.canvas.itemconfig(self.targets[(target.x, target.y)], state="hidden")

    def show_current_tee_pos(self, tee_pos):
        self.canvas.itemconfig(self.targets[(tee_pos.x, tee_pos.y)], fill="white", state="normal")

    def hide_previous_tee_pos(self, tee_pos):
        self.canvas.itemconfig(self.targets[(tee_pos.x, tee_pos.y)], fill="", state="hidden")

    def draw_tee(self):
        self.canvas.itemconfig(self.targets[(self.grid.tee.x, self.grid.tee.y)], fill="white", state="normal")

    def draw_hole(self):
        self.canvas.itemconfig(self.targets[(self.grid.hole.x, self.grid.hole.y)], outline="white", fill="gray", state="normal")

    def draw_trajectory(self, shots, visited):
        for start, end in shots:
            x1, y1 = self.get_pixel_at_tile_center(start)
            x2, y2 = self.get_pixel_at_tile_center(end)
            self.canvas.create_line(x1, y1, x2, y2, fill="white", width=3, tags="trajectory")

        # this whole thing is just because the player might visit one tile more than once
        # so we need to deal with that to indicate the order in which they shot their shots at the end
        # if they visited the same tile at shot #2 and #6
        # the tile will indicate 2/6
        shots_order_indicators = {}
        indicator = 1
        i = 1
        for x, y in visited:
            if i == 1:
                i += 1
                continue
            shots_order_indicators.setdefault((x, y), []).append(indicator)
            self.canvas.itemconfig(self.targets[(x, y)], fill="white", state="normal", tags="trajectory")
            indicator += 1

        for (x, y), indicators in shots_order_indicators.items():
            tile = self.grid.tile_map[(x, y)]
            cx, cy = self.get_pixel_at_tile_center(tile)
            self.canvas.create_text(
                cx, cy,
                text="/".join(map(str, indicators)),
                font=("Helvetica", 6, "bold"),
                tags="trajectory",
            )

    def erase_trajectory(self):
        self.canvas.delete("trajectory")

    def get_pixel_at_tile_center(self, tile):
        cx = (tile.x - 1) * BOARD_TILE_SIZE + BOARD_TILE_SIZE / 2
        cy = (tile.y - 1) * BOARD_TILE_SIZE + BOARD_TILE_SIZE / 2
        return cx, cy

    def get_tile_from_pixel_coordinates(self, x, y):
        x = int(x // self.tile_size) + 1
        y = int(y // self.tile_size) + 1
        return self.grid.tile_map.get((x, y))

class ControlsPanel():
    def __init__(self, frame):
        # row 1 is the current roll indicator and mulligan left indicator
        self.roll_label = tk.Label(frame, text="ROLL: (0)", font=CONTROLS_EL_FONT)
        self.roll_label.grid(row=0, column=0, sticky="w", pady=CONTROLS_EL_PADY)

        self.mulligan_label = tk.Label(frame, text="MULLIGANS: ( )", font=CONTROLS_EL_FONT)
        self.mulligan_label.grid(row=0, column=1, sticky="e", pady=CONTROLS_EL_PADY)

        # row 2 is the roll dice button and retry button
        self.roll_button = tk.Button(frame, text="ROLL DICE", font=CONTROLS_EL_FONT)
        self.roll_button.grid(row=1, column=0, sticky="w", pady=CONTROLS_EL_PADY)

        self.retry_button = tk.Button(frame, text="RETRY", font=CONTROLS_EL_FONT)
        self.retry_button.grid(row=1, column=1, sticky="e", pady=CONTROLS_EL_PADY)

        # row 3 is save course, new course buttons
        self.save_button = tk.Button(frame, text="SAVE", font=CONTROLS_EL_FONT)
        self.save_button.grid(row=2, column=0, sticky="w", pady=CONTROLS_EL_PADY)

        self.new_button = tk.Button(frame, text="NEW", font=CONTROLS_EL_FONT)
        self.new_button.grid(row=2, column=1, sticky="e", pady=CONTROLS_EL_PADY)

        # row 4 is course dropdown and load course button
        self.load_dropdown = ttk.Combobox(frame, state="readonly", width=25)
        self.load_dropdown.set("SELECT COURSE")
        self.load_dropdown.grid(row=3, column=0, sticky="w", pady=CONTROLS_EL_PADY)

        self.load_button = tk.Button(frame, text="LOAD", font=CONTROLS_EL_FONT)
        self.load_button.grid(row=3, column=1, stick="e", pady=CONTROLS_EL_PADY)

        # this code distributes the size of the label columns in the grid 
        # so they fill in the width of the window evenly
        columns, _ = frame.grid_size()
        for col in range(columns):
            frame.columnconfigure(col, weight=1, uniform="controls")

    def reinitialize_label_values(self, mulligans):
        self.roll_label.config(text="ROLL: (0)")
        self.mulligan_label.config(text=f"MULLIGANS: ({mulligans})")

    def update_roll_label(self, value, is_over):
        if not is_over:
            self.roll_label.config(text=f"ROLL: ({value})")
        else:
            self.roll_label.config(text=f"HOLE IN ({value})") # at the end of the game we use the roll label to print par how many

    def update_mulligan_label(self, mulligans):
        self.mulligan_label.config(text=f"MULLIGANS: ({mulligans})")

    def update_roll_button(self, is_shooting_phase):
        if is_shooting_phase:
            self.roll_button.config(text="USE MULLIGAN")
        else:
            self.roll_button.config(text="ROLL DICE")

    def refresh_saved_courses_list(self, course_names):
        self.load_dropdown["values"] = course_names