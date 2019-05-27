class CompressedList:
    def __init__(self, power=1, max_size=100):
        """
        Contains means of added values as their number exceed 'power'.
        Means are stored in 'stored' variable.
        Last added values are stored in 'buff'
        'stored' is resized when it's length exceeds 'max_size'
        """
        self.stored = []
        self.buff = []
        self.power = power
        self.max_size = max_size

    def add(self, new):
        self.buff.append(new)
        if len(self.buff) == self.power:
            # Adding to 'stored'
            self.stored.append((sum(self.buff) / self.power))
            self.buff.clear()
            if len(self.stored) == self.max_size:
                # Resizing 'stored'
                # Every 10 values are compressed in 1
                self.stored = [sum(self[i:i+10]) / 10 for i in range(0, len(self.stored), 10)]
                self.power *= 10
