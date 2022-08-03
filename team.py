
class Team:
    """ Represents a team """

    def __init__(self, abbrev, division):
        self.abbrev = abbrev
        self.division = division 

    def is_pseudo_team_bye(self):
        return self.abbrev.startswith('BY') #BYE

    def __repr__(self):
        return self.abbrev