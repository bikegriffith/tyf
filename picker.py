import random
from errors import NoAvailableOpponnentError

def pick_random_away_game_for_team(schedule, abbrev, sort_key=None):
    games = []
    for g in schedule.games:
        if g.is_bye:
            continue
        if g.away.abbrev == abbrev:
            games.append(g)
    try:
        if sort_key is None:
            random.shuffle(games)
        else:
            random.shuffle(games)
            # XXX: too smart doesn't work
            #games = sorted(games, key=sort_key)
        return games.pop()
    except IndexError:
        return None

def pick_random_home_game_for_team(schedule, abbrev, sort_key=None):
    games = []
    for g in schedule.games:
        if g.is_bye:
            continue
        if g.home.abbrev == abbrev:
            games.append(g)
    try:
        if sort_key is None:
            random.shuffle(games)
        else:
            random.shuffle(games)
            # XXX: too smart doesn't work
            #games = sorted(games, key=sort_key)
        return games.pop()
    except IndexError:
        return None

class Counter:
    def __init__(self):
        self.value = 0

pick_random_opponent_counter = Counter()

def pick_random_opponent(team, eligible_teams, schedule, avoid_teams=None):
    """ Pick a random opponent for the given team that has not yet
        been played against in the given schedule.
    """
    # global pick_random_opponent_counter
    pick_random_opponent_counter.value = pick_random_opponent_counter.value + 1

    teams = list(eligible_teams.values())
    random.shuffle(teams)
    for t in teams:
        if team.abbrev == t.abbrev:
            continue
        if avoid_teams and t.abbrev in avoid_teams:
            continue
        if schedule.already_played(team, t):
            continue
        # HACK: XXX: checking for double bye...
        if t.is_pseudo_team_bye() and schedule.has_bye(team.abbrev):
            continue
        return t
    raise NoAvailableOpponnentError
