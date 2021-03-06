# vim:filetype=python:fileencoding=utf-8
"""
Usage

    python schedule.py

Generates a randomized schedule for the Buckeye Youth Football Conference
satisfying all rules and constraints.  When done, a matrix of the schedule
is printed to standard output.

Will attempt several million iterations using simplified genetic
mutation solving techniques.  If no schedule can be generated, an
error is logged and the current best attempt will be printed.
"""

from __future__ import print_function
import random, sys

global debug
debug = False

class Field:
    """ Represents a playing field """

    def __init__(self, abbrev):
        self.abbrev = abbrev

class Team:
    """ Represents a team """

    def __init__(self, abbrev, home_field):
        self.abbrev = abbrev
        self.home_field = home_field

    def __repr__(self):
        return self.abbrev

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
        self.is_bye = is_bye

    def swap(self):
        """ Swap home and away teams """
        tmp = self.away
        self.away = self.home
        self.home = tmp

    def __repr__(self):
        return "Week %s - %s vs %s " % (self.week, self.home, self.away)

class LeagueSchedule:
    """ Used to build a schedule for the entire league for a given
        division and season.
    """

    def __init__(self, teams, num_weeks):
        self.teams = teams
        self.games = []
        self.num_weeks = num_weeks

    def print_schedule(self):
        teams = self.teams.values()
        teams.sort(key=lambda t: t.abbrev)
        for team in teams:
            ta = team.abbrev
            if ta == 'BYE':
                continue
            opponents = [self.opponent_in_week(ta, i+1) for i in range(self.num_weeks)]
            unplayed = list(set(t for t in self.teams.keys() if t != ta) - set(o.lstrip('@') for o in opponents))
            line = "%s:\t" % ta
            for opponent in opponents:
                if opponent == 'BYE':
                    opponent = '*BYE*'
                line += "%s\t" % opponent
            line += "<" + ",".join(unplayed) + ">"
            print(line)

    def add(self, game):
        if debug:
            print(game)
        self.games.append(game)

    def already_played(self, a, b):
        for g in self.games:
            if g.home == a and g.away == b:
                return True
            if g.home == b and g.away == a:
                return True
        return False

    def game_for_team_in_week(self, abbrev, week):
        for g in self.games:
            if (g.away.abbrev == abbrev or g.home.abbrev == abbrev) and g.week == week:
                return g
        return None

    def games_for_team(self, abbrev):
        games = []
        for g in self.games:
            if g.away.abbrev == abbrev or g.home.abbrev == abbrev:
                games.append(g)
        games.sort(key=lambda g: g.week)
        return games

    def opponent_in_week(self, abbrev, week):
        for g in self.games:
            if week != g.week:
                continue
            if g.away is not None and g.away.abbrev == abbrev:
                if g.is_bye:
                    return '*BYE*'
                return '@' + g.home.abbrev
            if g.home is not None and g.home.abbrev == abbrev:
                if g.is_bye:
                    return '*BYE*'
                return g.away.abbrev
        return None

    def contains_matchup(self, abbrev1, abbrev2):
        for g in self.games:
            if g.away.abbrev == abbrev1 and g.home.abbrev == abbrev2:
                return True
            if g.away.abbrev == abbrev2 and g.home.abbrev == abbrev1:
                return True
        return False

    def max_consecutive_home_or_away_games(self, abbrev):
        max_consecutive = 0
        consecutive_home = 0
        consecutive_away = 0
        games = self.games_for_team(abbrev)
        for g in games:
            if g.is_bye:
                continue
            elif g.home.abbrev == abbrev:
                consecutive_home += 1
                consecutive_away = 0
                max_consecutive = max(max_consecutive, consecutive_home)
            elif g.away.abbrev == abbrev:
                consecutive_away += 1
                consecutive_home = 0
                max_consecutive = max(max_consecutive, consecutive_away)
        return max_consecutive

    def home_game_count_for_team(self, abbrev):
        count = 0
        for g in self.games:
            if g.is_bye:
                continue
            if g.home.abbrev == abbrev:
               count = count + 1
        return count

    def is_away_in_week(self, abbrev, week):
        for g in self.games:
            if g.week != week:
                continue
            if g.is_bye:
                continue
            if g.away.abbrev == abbrev:
                return True
        return False

    def is_home_in_week(self, abbrev, week):
        for g in self.games:
            if g.week != week:
                continue
            if g.is_bye:
                continue
            if g.home.abbrev == abbrev:
                return True
        return False

    def pick_random_away_game_for_team(self, abbrev):
        games = []
        for g in self.games:
            if g.is_bye:
                continue
            if g.away.abbrev == abbrev:
                games.append(g)
        try:
            random.shuffle(games)
            return games.pop()
        except IndexError:
            return None

    def pick_random_home_game_for_team(self, abbrev):
        games = []
        for g in self.games:
            if g.is_bye:
                continue
            if g.home.abbrev == abbrev:
                games.append(g)
        try:
            random.shuffle(games)
            return games.pop()
        except IndexError:
            return None

    def rebalance_home_away(self, max_iterations):
        any_team_unbalanced = False
        for i in range(max_iterations):
            if i % 1000 == 0:
                print(".", end="")
                sys.stdout.flush()

            any_team_unbalanced = False
            for team in teams:
                count = self.home_game_count_for_team(team)

                # Equal number of home/away ... now check more complex requirements
                if count == 4:
                    # Cannot not have more than 3 consecutive home/away
                    max_consecutive = self.max_consecutive_home_or_away_games(team)
                    if max_consecutive > 3:
                        any_team_unbalanced = True
                        g1 = self.pick_random_home_game_for_team(team)
                        g2 = self.pick_random_away_game_for_team(team)
                        if not g1.forced and not g2.forced:
                            g1.swap()
                            g2.swap()

                    # TAG/TAB cannot be both Home in same week (shared field)
                    if team == "TAG" or team == "TAB":
                        g_home_weeks = map(lambda g: g.week,
                                filter(lambda g: g.home.abbrev == 'TAG', self.games_for_team('TAG')))
                        b_home_weeks = map(lambda g: g.week,
                                filter(lambda g: g.home.abbrev == 'TAB', self.games_for_team('TAB')))
                        shared_weeks = list(set(g_home_weeks) & set(b_home_weeks))
                        if len(shared_weeks) > 0:
                            # print("Fixing TAG/TAB sharing home in weeks %s" % shared_weeks)
                            any_team_unbalanced = True
                            rand_teams = ['TAG', 'TAB']
                            random.shuffle(rand_teams)
                            random.shuffle(shared_weeks)
                            g = self.game_for_team_in_week(rand_teams[0], shared_weeks[0])
                            if not g.forced:
                                g.swap()
                    continue

                # More or less than 4 home games ... try to rebalance
                any_team_unbalanced = True
                if count > 4:
                    for i in range(count - 4):
                        g = self.pick_random_home_game_for_team(team)
                        if not g.forced:
                            g.swap()
                if count < 4:
                    for i in range(count):
                        g = self.pick_random_away_game_for_team(team)
                        if not g.forced:
                            g.swap()

            if not any_team_unbalanced:
                return True

        return False

    def __repr__(self):
        return "%s" % self.games


###
### League and Season Configuration
###

fields = {
    1: Field('Ellet'),
    2: Field('Tallmadge'),
    3: Field('Tallmadge HS'),
    4: Field('NW'),
    5: Field('Manchester'),
    6: Field('Springfield'),
    7: Field('Norton'),
    8: Field('Norton HS'),
    9: Field('Barberton'),
    10: Field('Barberton HS'),
    11: Field('Chipp'),
    12: Field('Chipp HS'),
    13: Field('Coventry'),
    14: Field('Coventry HS'),
    15: Field('Rittman'),
    16: Field('Tuslaw'),
}

teams_byfc_2019 = dict(
    BAR=Team('BAR', fields[9]),
    CHI=Team('CHI', fields[11]),
    COV=Team('COV', fields[13]),
    ELL=Team('ELL', fields[1]),
    MAN=Team('MAN', fields[5]),
    NRW=Team('NRW', fields[4]),
    NRT=Team('NRT', fields[7]),
    RIT=Team('RIT', fields[15]),
    SPR=Team('SPR', fields[6]),
    TAB=Team('TAB', fields[2]),
    TAG=Team('TAG', fields[2]),
    TUS=Team('TUS', fields[16]),
)


# 2019 Season Weeks		
# 1	8/17	
# 2	8/24	Barberton Home, Norton Away
# 3	8/31	
# 4	9/7	Norton Home (if possible, Tallmadge Blue Bye this week)
# 5	9/14	
# 6	9/21	Coventry Home
# 7	9/28	Barberton Home
# 8	10/5	Norton Home vs Barberton
# 9	10/12	(only used to make up C division byes)
#
# Core Rules/Constraints:
# * each team has 4 Home, 4 Away games
# * no team plays same team twice
# * no more than 3 home or away games in a row
# * same field cannot be used for more than one game at a time
#
# Possible Algorithm:
# * schedule the B division with all 12 teams, no byes
# * copy B division to start of C team schedule
#       - no TAG team ... remove those games, replacing with BYE
#       - 2 remaining teams need to be facing each other in some week
#         (preferably middle of season), add that game as a bye (making 3 byes
#         in 1 week)
#       - add 9th week to C team calendar, pushing all bye TEAMs into that week
#         and attempting to distribute matchups to those that haven't played
#         each other
#
overrides_byfc_2019 = [
    dict(team='TAB', avoid_opponent='SPR'),
    dict(team='TAB', avoid_opponent='TAG'),

    dict(team='BAR', week=2, force_home=True),
    dict(team='NRT', week=4, force_home=True),
    dict(team='NRT', week=2, force_away=True),
    dict(team='BAR', week=8, force_away=True, force_opponent='NRT'), #REQUESTED
    dict(team='COV', week=6, force_home=True),

    # Due to field install delays
    dict(team='CHI', week=1, force_away=True),
    dict(team='CHI', week=2, force_away=True),
    dict(team='CHI', week=4, force_away=True),

    # Special request
    dict(team='ELL', week=2, force_home=True, force_opponent='SPR'),
    dict(team='BAR', week=7, force_home=True, force_opponent='TAB'), #TURF

    # Make sure smaller teams play each other
    dict(team='SPR', week=5, force_home=True, force_opponent='CHI'),
]

teams_byfc_north_2020 = dict(
    BAR=Team('BAR', fields[9]),
    COV=Team('COV', fields[13]),
    ELL=Team('ELL', fields[1]),
    NRT=Team('NRT', fields[7]),
    TAB=Team('TAB', fields[2]),
    TAG=Team('TAG', fields[2]),
    MOG=Team('MOG', None),
    WOD=Team('WOD', None),
    STR=Team('STR', None),

    BYE=Team('BYE', None), #Represents a *BYE* to get to even number of teams in conference
)

teams_byfc_south_2020 = dict(
    CHI=Team('CHI', fields[11]),
    TUS=Team('TUS', fields[16]),
    RIT=Team('RIT', fields[15]),
    SPR=Team('SPR', fields[6]),
    MAN=Team('MAN', fields[5]),
    NRW=Team('NRW', fields[4]),
    MAS=Team('MAS', None),
    PER=Team('PER', None),

    BYE1=Team('BYE1', None), #Represents a *BYE* to get to even number of teams in conference
    BYE2=Team('BYE2', None), #Represents a *BYE* to get to even number of teams in conference
)

# 2020 Season Weeks
#   1 - 8/15
#   2 - 8/22
#   3 - 8/29
#   4 - 9/5
#   5 - 9/12
#   6 - 9/19
#   7 - 9/26
#   8 - 10/3
#   9 - 10/10
# Norton home game 10/3
# Barberton home game 8/22 at high school turf
#
# Northwest home games Aug. 29th and Sept. 26th.
# Chippewa home games Sept 5th, 19th and October 3rd (turf)
# Tuslaw home 9/12 at high school ... also home 10/17 if possible
# Perry home games only on August 22nd; September 5th and 26th; October 3rd, 10th, 24th, 31st
# Massillon home Aug 15 thru Oct 24 ... Plus possible PBTS ... Cannot October 3, road game
overrides_byfc_north_2020 = [
    dict(team='TAB', avoid_opponent='TAG'),
    dict(team='NRT', week=8, force_home=True, force_opponent='TAG'),
    dict(team='BAR', week=2, force_home=True, force_opponent='TAB'),
]
overrides_byfc_south_2020 = [
    dict(team='NRW', week=3, force_home=True),
    dict(team='NRW', week=7, force_home=True),
    dict(team='CHI', week=4, force_home=True),
    dict(team='CHI', week=6, force_home=True),
    dict(team='CHI', week=8, force_home=True),
    dict(team='TUS', week=5, force_home=True),
    dict(team='PER', week=2, force_home=True),
    dict(team='PER', week=4, force_home=True),
    dict(team='PER', week=7, force_home=True),
    dict(team='PER', week=8, force_home=True),
    dict(team='MAS', week=8, force_away=True),
]

#teams = teams_byfc_north_2020
#overrides = overrides_byfc_north_2020
teams = teams_byfc_south_2020
overrides = overrides_byfc_south_2020
overrides_by_week = {}

def get_overrides_by_week(week):
    if len(overrides_by_week.keys()) == 0:
        for override in overrides:
            if overrides_by_week.get(override.get('week')) is None:
                overrides_by_week[override.get('week')] = []
            overrides_by_week[override.get('week')].append(override)
    return overrides_by_week.get(week) or []

number_weeks = 8

def try_make_b_team_schedule():
    """ Generate the schedule for the B division, returning an instance
        of LeagueSchedule.

        Note: the schedule returned here does not satisfy all constraints
        (home/away balance, etc.) but can be used as a starting point.
    """

    schedule = LeagueSchedule(teams.copy(), num_weeks=number_weeks)

    for i in range(number_weeks):
        week = i + 1
        week_teams = teams.copy()

        for override in get_overrides_by_week(week):
            if override.get('force_opponent'):
                team = teams[override['team']]
                opponent = teams[override['force_opponent']]
                if team.abbrev not in week_teams or opponent.abbrev not in week_teams or schedule.already_played(team, opponent):
                    raise CannotFulfillOverride
                if override.get('force_home'):
                    schedule.add(Game(team, opponent, week, forced=True))
                else:
                    schedule.add(Game(opponent, team, week, forced=True))
                del week_teams[team.abbrev]
                del week_teams[opponent.abbrev]

            elif override.get('force_home'):
                team = teams[override['team']]
                if team.abbrev not in week_teams:
                    raise CannotFulfillOverride
                opponent = pick_random_opponent(team, week_teams, schedule)
                schedule.add(Game(team, opponent, week, forced=True))
                del week_teams[team.abbrev]
                del week_teams[opponent.abbrev]

            elif override.get('force_away'):
                team = teams[override['team']]
                if team.abbrev not in week_teams:
                    raise CannotFulfillOverride
                opponent = pick_random_opponent(team, week_teams, schedule)
                schedule.add(Game(opponent, team, week, forced=True))
                del week_teams[team.abbrev]
                del week_teams[opponent.abbrev]

        for abbrev, team in week_teams.items():
            if abbrev not in week_teams:
                continue
            try:
                opponent = pick_random_opponent(team, week_teams, schedule)
                schedule.add(Game(team, opponent, week))
                del week_teams[team.abbrev]
                del week_teams[opponent.abbrev]
            except NoAvailableOpponnentError:
                raise NoAvailableOpponnentError, "Cannot find opponent for %s in week %s" % (team, week)

    # Validate opponent avoids
    for override in overrides:
        if override.get('avoid_opponent'):
            if schedule.contains_matchup(override['team'], override['avoid_opponent']):
                raise IterationError('%s and %s should not play' % (override['team'], override['avoid_opponent']))

    # Validate Tallmadge 2 teams not sharing field
    for week in range(number_weeks):
        week = week + 1
        if schedule.is_home_in_week('TAG', week) and schedule.is_home_in_week('TAB', week):
            raise IterationError('TAG and TAB both home in week %s' % week)

    return schedule


pick_random_opponent_counter = 0

def pick_random_opponent(team, eligible_teams, schedule):
    """ Pick a random opponent for the given team that has not yet
        been played against in the given schedule.
    """
    global pick_random_opponent_counter
    pick_random_opponent_counter += 1

    teams = eligible_teams.values()
    random.shuffle(teams)
    for t in teams:
        if team.abbrev == t.abbrev:
            continue
        if schedule.already_played(team, t):
            continue
        return t
    raise NoAvailableOpponnentError



def make_schedules():
    """ Run an iterative constraint solver to attempt to generate a set of
        league schedules that satisfies all constraints.
    """
    max_outer_loop_iterations = 1000000
    max_rebalance_home_away_iterations = 500000
    for i in range(max_outer_loop_iterations):
        if i % 1000 == 0:
            print("-", end="")
            sys.stdout.flush()
        try:
            b_schedule = try_make_b_team_schedule()
            print("--- MADE DIVISION SCHEDULE ---")
            b_schedule.print_schedule()

            # Now try to balance home game count for each team
            print("Now attempting to balance...")
            balanced = b_schedule.rebalance_home_away(max_rebalance_home_away_iterations)
            print("")
            print("--- HOME/AWAY BALANCED DIVISION SCHEDULE ---")
            b_schedule.print_schedule()

            if not balanced:
                print("Unable to balance teams.  Will try again.")
                continue

            # print("B Division is balanced. Now trying for C Division (with no Tallmadge Gold)...")
            # c_teams = teams.copy()
            # del c_teams['TAG']
            # c_schedule = LeagueSchedule(c_teams, num_weeks=number_weeks)
            # byes = []
            # for g in b_schedule.games:
            #     if g.home.abbrev == 'TAG':
            #         c_schedule.add(Game(None, g.away, g.week, is_bye=True))
            #         byes.append(g.away.abbrev)
            #     elif g.away.abbrev == 'TAG':
            #         c_schedule.add(Game(g.home, None, g.week, is_bye=True))
            #         byes.append(g.home.abbrev)
            #     else:
            #         c_schedule.add(Game(g.home, g.away, g.week, forced=g.forced))

            # # TODO: The C division week 9 matches for now are manually arranged using the
            # # data printed to standard out.  This algorithm could be extended to
            # # solve for a valid arrangement of games/byes.
            # c_schedule.print_schedule()
            # needs_a_bye_still = list(set(c_teams.keys()) - set(byes))
            # print("Still needs a bye: %s", needs_a_bye_still)

            break
        except IterationError, err:
            if str(err) and debug:
                print('Error: %s' %err)
            continue
    else:
        print("")
        print("Cannot find satisfactory schedule")

    print("{}M matches analyzed".format(1.0*pick_random_opponent_counter/1000000.0))


class IterationError(Exception):
    pass

class CannotFulfillOverride(IterationError):
    pass

class NoAvailableOpponnentError(IterationError):
    pass

if __name__ == "__main__":
    make_schedules()


