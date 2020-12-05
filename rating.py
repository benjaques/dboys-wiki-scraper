# Episode Class
from datetime import datetime


class Rating:
    """ Wikia Rating Object """

    def __init__(self, number, date, epoch, person, restaurant, score):
        self.episode = "_" + str(number)
        self.date = date
        self.epoch = epoch
        self.person = person
        self.restaurant = restaurant
        self.score = float(score)


