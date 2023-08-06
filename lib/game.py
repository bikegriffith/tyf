from lib.byes import is_bye as _is_bye


class Game:
    """ Represents a game between two teams in a given week.  If
        the game was the result of a forced condition, the forced
        flag is set.  If the game is a bye, the is_bye flag is set.
    """

    def __init__(self, home, away, week, forced=False, is_bye=False):
        self.home = home
        self.away = away
        self.week = week
        self.forced = forced
        self.is_bye = is_bye or _is_bye(home, away)

        if self.home.abbrev == 'PRM':
            self.swap()

    def swap(self):
        """ Swap home and away teams """
        if self.away.abbrev == 'PRM':
            return
        tmp = self.away
        self.away = self.home
        self.home = tmp

    def __repr__(self):
        return "Week %s - %s vs %s " % (self.week, self.home, self.away)
