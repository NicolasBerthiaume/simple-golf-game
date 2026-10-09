import json
from pathlib import Path

SAVE_DIR = Path.home() / ".golf"
SAVE_DIR.mkdir(exist_ok=True)
SAVE_FILE = SAVE_DIR / "courses.json"

class SaveSystem:
    # Courses are randomly generated...
    # This system allows the user to save the courses they like
    
    def __init__(self, window, board, controls, game):
        self.window = window
        self.board = board
        self.controls = controls
        self.game = game

    def save_current_course(self):
        course_name = self.window.prompt_user("Save course", "Course name:")
        if not course_name:
            return

        self.write_course_to_file(course_name)
        self.controls.refresh_saved_courses_list(self.get_all_course_names())

    def load_selected_course(self):
        course_index = self.controls.load_dropdown.current()
        if course_index == -1:
            return

        course_data = self.load_all()[course_index]
        self.board.grid.convert_from_dict(course_data)
        self.game.reset_game(True)

    def write_course_to_file(self, course_name):
        courses = self.load_all()
        courses.append(self.current_course_to_dict(course_name))
        self.save_all(courses)

    def load_all(self):
        if not SAVE_FILE.exists():
            return []
        with open(SAVE_FILE) as f:
            return json.load(f)

    def save_all(self, courses):
        data = json.dumps(courses, indent=2) # fail guard in case of corrupted/non-serializable save data
        with open(SAVE_FILE, "w") as f:
            f.write(data)

    def current_course_to_dict(self, course_name):
        course = self.board.grid.convert_to_dict()
        course["course_name"] = course_name
        return course

    def get_all_course_names(self):
        return [c["course_name"] for c in self.load_all()]

    def load_course(self, course_data):
        self.board.grid.convert_from_dict(course_data)