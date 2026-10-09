import random

from enum import Enum, auto

STARTING_NUMBER_OF_MULLIGANS = 3

class GamePhase(Enum):
    ROLL = auto()
    SHOOT = auto()
    OVER = auto()

class Game:
    def __init__(self, board, controls):
        self.board = board
        self.controls = controls

        self.current_pos = None
        self.visited = [] # visited is just coordinates for a tile we've been on
        self.hole_pos = None
        self.shots = [] # shots include tuples of 2 tiles, start tile and end tile
        self.mulligans = STARTING_NUMBER_OF_MULLIGANS
        self.valid_targets = []
        self.phase = GamePhase.ROLL
        self.roll = None

    def new_game(self):
        # get new board data
        self.board.prepare_board(True)
        # reinitialize with new values
        self.reset_game(False) # don't need to prepare the board twice
        
    def reset_game(self, board_needs_preparing):
        self.board.erase_trajectory()
        if board_needs_preparing: self.board.prepare_board(False) # the bool is for is_new, so False here
        self.hole_pos = self.board.grid.hole

        # we need this check because player might be resetting in the middle of shooting
        # with visible targets on board
        if self.valid_targets != []:
            self.board.hide_targets(self.valid_targets)
            self.valid_targets = []

        self.current_pos = self.board.grid.tee
        self.visited = [(self.board.grid.tee.x, self.board.grid.tee.y)]
        self.shots = []
        self.mulligans = STARTING_NUMBER_OF_MULLIGANS
        self.phase = GamePhase.ROLL
        self.roll = None
        self.controls.reinitialize_label_values(self.mulligans)
        self.controls.update_roll_button(False)

    def roll_dice(self):
        if not self.can_roll():
            return

        # in case we're using a mulligan
        # hide any previously valid targets first
        self.board.hide_targets(self.valid_targets)

        self.roll = random.randint(1, 6)
        self.valid_targets = self.get_valid_targets()
        self.phase = GamePhase.SHOOT

        # update GUI
        self.controls.update_roll_label(self.roll, False)
        self.controls.update_roll_button(True)
        self.board.show_targets(self.valid_targets)

    def shoot(self, event):
        # event = mouse left click
        if self.phase != GamePhase.SHOOT:
            return

        # check which tile we just clicked on and if that's currently a valid target
        target = self.board.get_tile_from_pixel_coordinates(event.x, event.y)
        if target not in self.valid_targets:
            return

        # hide previous valid targets
        # and previous tee position
        self.board.hide_targets(self.valid_targets)
        self.board.hide_previous_tee_pos(self.current_pos)

        # update everything
        self.visited.append((target.x, target.y))
        self.shots.append((self.current_pos, target))
        self.valid_targets.remove(target)
        self.current_pos = target

        # draw the tee at the current position
        self.board.show_current_tee_pos(self.current_pos)

        # do we roll or did we put in the hole
        if self.current_pos == self.board.grid.hole:
            self.phase = GamePhase.OVER
            self.board.draw_trajectory(self.shots, self.visited)
            self.controls.update_roll_label(len(self.shots), True)
        else:
            self.phase = GamePhase.ROLL
            self.controls.update_roll_label(0, False)
        
        self.controls.update_roll_button(False)

    def can_roll(self):
        if self.phase == GamePhase.OVER:
            return False
        elif self.phase == GamePhase.SHOOT:
            if self.mulligans == 0:
                return False
            else:
                self.mulligans -= 1
                self.controls.update_mulligan_label(self.mulligans)
                return True
        else:
            return True

    def get_valid_targets(self):
        return [
            target for target in self.board.grid.tile_map.values() if (target.x, target.y) in self.board.targets and self.is_valid_target(target)
        ]

    def is_valid_target(self, target):
        dx = target.x - self.current_pos.x
        dy = target.y - self.current_pos.y

        if dx == 0 and dy == 0:
            return False

        # rule for now: player can only shoot up, down, diagonally
        straight_or_diagonal = dx == 0 or dy == 0 or abs(dx) == abs(dy)
        if not straight_or_diagonal:
            return False

        # this gives us the distance to the target
        # as shown above, if straight, either dx or dy is 0, so distance gives the value of the non-zero variable
        # if diagonal, both values are the same, so it doesn't matter which of them we get for distance
        distance = max(abs(dx), abs(dy))

        # rule for now: players can shoot their balls exactly the distance of the roll they got
        # OR one below that, so if you roll 5, you can roll 5 or 4 tiles away
        return self.roll - 1 <= distance <= self.roll