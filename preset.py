from exercise import Exercise


class Preset:
    def __init__(self, name: str, exercises: list):
        self.exercises = exercises
        self.name = name

    def __str__(self):
        return self.name

    def add_exercise(self, exercise):
        if exercise.isinstance(Exercise):
            self.exercises.append(exercise)

    def remove_exercise(self, exercise):
        if exercise.isinstance(Exercise):
            self.exercises.remove(exercise)

    def clear_preset(self):
        self.exercises.clear()
