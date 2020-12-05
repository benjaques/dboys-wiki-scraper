# Episode Class
from datetime import datetime


class PersonOrChain:
    """ Wikia Episode Object """

    def __init__(self, fork_ratings, episode_number):
        self.ratings = fork_ratings
        self.episodes = {"_" + str(episode_number): True}
