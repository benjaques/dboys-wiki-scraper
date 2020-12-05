# Episode Class
from datetime import datetime


class Episode:
    """ Wikia Episode Object """

    def __init__(self, title, number, href, release_date, fork_ratings):
        self.title = title
        self.number = number
        self.href = href
        self.release_date = release_date
        self.fork_ratings = fork_ratings
        self.notes = None
        self.avgScore = None
        self.awards = None

    def __repr__(self):
        return self.title + "\nEpisode " + self.number + "\nReleased " + self.release_date + "\nFork Ratings: " + \
               str(self.fork_ratings)

    def epoch_time(self):
        utc_time = datetime.strptime(self.release_date, "%B %d, %Y")
        epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()
        return int(epoch_time)

    def find_average(self):
        total = 0
        for key in self.fork_ratings.values():
            total += float(key)

        self.avgScore = round(total / len(self.fork_ratings), 2)
        return self.avgScore

    def determine_awards(self):
        if self.isPlatinum():
            self.awards = "platinum"
        elif self.isGold():
            self.awards = "gold"
        else:
            self.awards = "none"

        return self.awards

    def isPlatinum(self):
        for key in self.fork_ratings.values():
            if float(key) != float(5):
                return False

        return True

    def isGold(self):
        for key in self.fork_ratings.values():
            if float(key) < float(4):
                return False

        return True
