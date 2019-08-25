# Episode Class


class Episode:
    """ Wikia Episode Object """

    def __init__(self, title, number, href, release_date, fork_ratings):
        self.title = title
        self.number = number
        self.href = href
        self.release_date = release_date
        self.fork_ratings = fork_ratings
        self.notes = None

    def __repr__(self):
        return self.title + "\nEpisode " + self.number + "\nReleased " + self.release_date + "\nFork Ratings: " + \
               str(self.fork_ratings)
