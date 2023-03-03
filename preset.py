from exercise import Exercise


class Preset:
    def __init__(self, name: str, exercises: list):
        self.exercises = exercises
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Preset):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.name == other.name and all([ex1 == ex2 for ex1, ex2 in zip(self.exercises, other.exercises)])

    def add_exercise(self, exercise):
        if exercise.isinstance(Exercise):
            self.exercises.append(exercise)

    def remove_exercise(self, exercise):
        if exercise.isinstance(Exercise):
            self.exercises.remove(exercise)

    def clear_preset(self):
        self.exercises.clear()
