class Exercise:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.brk = kwargs['brk']
        if 'time' in kwargs:
            self.time = kwargs['time']
            self.reps = None
        else:
            self.reps = kwargs['pers']
            self.time = None

    def __str__(self):
        if self.reps is not None:
            return
        else:
            return f"{self.name}({self.time}s)"
