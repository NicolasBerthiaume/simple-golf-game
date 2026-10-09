from gui import Window, Board, ControlsPanel
from game import Game
from save import SaveSystem

def golf():
    window = Window()
    board = Board(window.board_frame)
    controls = ControlsPanel(window.controls_frame)
    
    game = Game(board, controls)
    save = SaveSystem(window, board, controls, game)

    # binding controls
    board.canvas.bind("<Button-1>", game.shoot)
    controls.roll_button.config(command=game.roll_dice)
    controls.new_button.config(command=game.new_game)
    controls.retry_button.config(command=lambda: game.reset_game(True)) # need to use a lambda here because reset_game takes a bool
    controls.save_button.config(command=save.save_current_course)
    controls.load_button.config(command=save.load_selected_course)

    game.new_game()
    controls.refresh_saved_courses_list(save.get_all_course_names())
    window.run()

if __name__ == "__main__":
    golf()