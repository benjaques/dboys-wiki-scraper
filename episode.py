# Episode Class


class Episode:
    """ Wikia Episode Object """

    def __init__(self, title, number):
        self.title = title
        self.number = number
        self.release_date = None
        self.href = None
        self.notes = None
