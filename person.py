# Episode Class
from datetime import datetime


class Episode:
    """ Wikia Episode Object """

    def __init__(self, title, number, release_date, duration, fork_ratings, photo, nextRatingNum, synopsis):
        self.avgScore = self.find_average(fork_ratings)
        self.awards = self.determine_awards(fork_ratings)
        self.date = release_date
        self.duration = duration
        self.epoch = self.epoch_time(release_date)
        self.negativeEpoch = -self.epoch
        self.negativeAvgScore = -self.avgScore
        self.negativeDuration = -self.duration
        self.number = number
        self.people = dict.fromkeys(fork_ratings, True)
        self.photo = photo
        self.ratings = {}
        for key in fork_ratings.keys():
            self.ratings["_" + str(nextRatingNum)] = True
            nextRatingNum = nextRatingNum + 1

        self.title = title
        self.restaurant = self.parse_restaurant()
        self.synopsis = synopsis


    def __repr__(self):
        return self.title + "\nEpisode " + self.number + "\nReleased " + self.release_date + "\nFork Ratings: " + \
               str(self.fork_ratings)

    def epoch_time(self, date):
        utc_time = datetime.strptime(date, "%B %d, %Y")
        epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()
        return int(epoch_time)

    def find_average(self, fork_ratings):
        total = 0
        for key in fork_ratings.values():
            total += float(key)

        self.avgScore = round(total / len(fork_ratings), 2)
        return self.avgScore

    def determine_awards(self, fork_ratings):
        if self.isPlatinum(fork_ratings):
            self.awards = "platinum"
        elif self.isGold(fork_ratings):
            self.awards = "gold"
        else:
            self.awards = "none"

        return self.awards

    def isPlatinum(self, fork_ratings):
        for key in fork_ratings.values():
            if float(key) != float(5):
                return False

        return True

    def isGold(self, fork_ratings):
        for key in fork_ratings.values():
            if float(key) < float(4):
                return False

        return True

    def parse_restaurant(self):
        first_part = self.title.split("with")[0]
        return ' '.join(first_part.split())

