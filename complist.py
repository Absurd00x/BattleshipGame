class CompressedList(list):
    def __init__(self, capacity=100):
        """
        Contains means of added values as their number exceed 'power'.
        Last added values are stored in 'buff'
        It is resized every time its size exceeds 'capacity'
        """
        super(CompressedList, self).__init__()
        self.buff = []
        self.power = 1
        self.capacity = capacity

    def append(self, new):
        self.buff.append(new)

        if len(self.buff) == self.power:
            super(CompressedList, self).append((sum(self.buff) / self.power))
            self.buff.clear()
            if self.__len__() == self.capacity:
                # Resizing
                # Every 10 values are replaced by their mean
                for i in range(10):
                    self.__setitem__(slice(i, i+10), (sum(self.__getitem__(slice(i, i+10))) / 10 for _ in range(1)))
                self.power *= 10
