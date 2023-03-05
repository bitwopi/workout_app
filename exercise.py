class Exercise:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.brk = kwargs['brk']
        self.time = kwargs['time']
        self.reps = kwargs['reps']

    def __str__(self):
        if self.reps is not None:
            return f"{self.name}({self.reps} reps)"
        else:
            return f"{self.name}({self.time}s)"

    def __eq__(self, other):
        if not isinstance(other, Exercise):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.name == other.name \
            and self.brk == other.brk \
            and self.time == other.time \
            and self.reps == self.reps
