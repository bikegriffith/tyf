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
import random, sys, math

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
            line += "\t" + str(self.home_game_count_for_team(ta))
            print(line)

    def add(self, game):
        if debug:
            print(game)
        self.games.append(game)

    def add_bye_if_needed(self):
        if number_weeks % 2 == 0:
            return
        needs_bye = []
        for team in teams:
            if team is 'BYE':
                continue
            if not self.has_bye(team):
                needs_bye.append(team)

        if len(needs_bye) == 2:
            g = self.contains_matchup(*needs_bye)
            if g:
                g.is_bye = True
                print('Changing game %s to bye' % g)
                return

        if len(needs_bye) == 4:
            g = self.contains_matchup(needs_bye[0], needs_bye[1])
            if g:
                g.is_bye = True
                print('Changing game %s to bye' % g)
                g = self.contains_matchup(needs_bye[2], needs_bye[3])
                if g:
                    g.is_bye = True
                    print('Changing game %s to bye' % g)
                    return
                else:
                    print('Unable to add bye for %s', needs_bye)
                    return
            g = self.contains_matchup(needs_bye[0], needs_bye[2])
            if g:
                g.is_bye = True
                print('Changing game %s to bye' % g)
                g = self.contains_matchup(needs_bye[1], needs_bye[3])
                if g:
                    g.is_bye = True
                    print('Changing game %s to bye' % g)
                    return
                else:
                    print('Unable to add bye for %s', needs_bye)
                    return
            g = self.contains_matchup(needs_bye[0], needs_bye[3])
            if g:
                g.is_bye = True
                print('Changing game %s to bye' % g)
                g = self.contains_matchup(needs_bye[1], needs_bye[2])
                if g:
                    g.is_bye = True
                    print('Changing game %s to bye' % g)
                    return
                else:
                    print('Unable to add bye for %s', needs_bye)
                    return
        print('Unable to add bye for %s', needs_bye)


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
                    return g.home.abbrev #'*BYE*'
                return '@' + g.home.abbrev
            if g.home is not None and g.home.abbrev == abbrev:
                if g.is_bye:
                    return g.away.abbrev #'*BYE*'
                return g.away.abbrev
        return None

    def has_bye(self, abbrev):
        for g in self.games:
            if (g.away.abbrev == abbrev or g.home.abbrev == abbrev) and g.is_bye:
                return True
        return False

    def contains_matchup(self, abbrev1, abbrev2, mode=None):
        for g in self.games:
            if mode != 'home' and g.away.abbrev == abbrev1 and g.home.abbrev == abbrev2:
                return g
            if mode != 'away' and g.away.abbrev == abbrev2 and g.home.abbrev == abbrev1:
                return g
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

    def pick_random_away_game_for_team(self, abbrev, sort_key=None):
        games = []
        for g in self.games:
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

    def pick_random_home_game_for_team(self, abbrev, sort_key=None):
        games = []
        for g in self.games:
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

    def rebalance_home_away(self, max_iterations):
        any_team_unbalanced = False
        game_balance = number_weeks / 2.0  # XXX: doesn't support odd schedules

        for i in range(max_iterations):
            if debug and (i % 1000 == 0):
                print(".", end="")
                sys.stdout.flush()

            any_team_unbalanced = False
            for team in teams:
                # Byes don't matter
                if team.startswith('BY'): #BYE
                    continue
                # Parma wrench
                #if team in ('PRM', 'BYE'):
                #    continue
                #if team in ('COP2'): # COP2 in D Division
                #    continue

                home_count = int(self.home_game_count_for_team(team))

                #print("%s - %s - %s" % (team, home_count, (home_count in [2, 3, 4])))

                balanced_home_counts = [int(game_balance)]

                if self.contains_matchup(team, 'PRM'):
                    balanced_home_counts = [int(math.ceil(game_balance)), int(math.floor(game_balance))]

                # Equal number of home/away ... now check more complex requirements
                if home_count in balanced_home_counts:
                    # Cannot not have more than 3 consecutive home/away
                    if enable_consecutive_check:
                        max_consecutive = self.max_consecutive_home_or_away_games(team)
                        if max_consecutive > 3:
                            any_team_unbalanced = True
                            g1 = self.pick_random_home_game_for_team(team)
                            g2 = self.pick_random_away_game_for_team(team)
                            if not g1.forced and not g2.forced:
                                g1.swap()
                                g2.swap()

                    # # TAG/TAB cannot be both Home in same week (shared field)
                    # if team == "TAG" or team == "TAB":
                    #     g_home_weeks = map(lambda g: g.week,
                    #             filter(lambda g: g.home.abbrev == 'TAG' and not g.is_bye, self.games_for_team('TAG')))
                    #     b_home_weeks = map(lambda g: g.week,
                    #             filter(lambda g: g.home.abbrev == 'TAB' and not g.is_bye, self.games_for_team('TAB')))
                    #     shared_weeks = list(set(g_home_weeks) & set(b_home_weeks))
                    #     if len(shared_weeks) > 0:
                    #         # print("Fixing TAG/TAB sharing home in weeks %s" % shared_weeks)
                    #         any_team_unbalanced = True
                    #         rand_teams = ['TAG', 'TAB']
                    #         random.shuffle(rand_teams)
                    #         random.shuffle(shared_weeks)
                    #         g = self.game_for_team_in_week(rand_teams[0], shared_weeks[0])
                    #         if not g.forced:
                    #             g.swap()

                    continue

                # More or less than 4 home games ... try to rebalance
                any_team_unbalanced = True

                if home_count > math.ceil(game_balance):
                    for i in range(home_count - int(math.ceil(game_balance))):
                        # be smarter than "random"; try to find one of the opponents
                        # that has too few home games if possible
                        g = self.pick_random_home_game_for_team(team,
                                sort_key=lambda game: self.home_game_count_for_team(game.away.abbrev))
                        if not g.forced:
                            g.swap()

                if home_count < math.floor(game_balance):
                    for i in range(home_count):
                        # be smarter than "random"; try to find one of the opponents
                        # that has too many home games if possible
                        g = self.pick_random_away_game_for_team(team,
                                sort_key=lambda game: -1 * self.home_game_count_for_team(game.away.abbrev))
                        if g and not g.forced:
                            g.swap()

            if not any_team_unbalanced:
                return True

        return False

    def __repr__(self):
        return "%s" % self.games


###
### League and Season Configuration
###

#
# Requests:
#     Perry home games only on September 26th; October 3rd, 10th, 24th, 31st
#       --> force away on 9/12, 9/19, 10/17
#     Tuslaw 9/12 home game @ HS
#     Norton 9/19 AWAY (and 10/3 home previously?)
#     Copley 3 road games 9/12, 9/19, 9/26...
#     Northwest must have home game 9/12
#     Nordonia has its High School field on September 19th ,26th and October 3rd.
#     Tallmadge D, C, B either all home or all away if possible....
#     Parma ALL road games (just give their away opponents an extra "home")
# Teams:
#     Parma
#     Hudson
#     Nordonia
#     Copley
#     Tallmadge
#     highland
#     ---------
#     Norton
#     Ellet
#     Barberton
#     Northwest
#     Tuslaw
#     Perry
# 6 regular season games, then gold (top 6), silver (bottom 6) playoffs
# starts 9/12
# Games times, D 9am, CV1030 jv immediately following, B 2p, jv
#
# Weeks
#     1   9/12    Tuslaw home, Copley away, Perry away, Northwest home
#     2   9/19    Norton away, Copley away, Perry away, Nordonia home
#     3   9/26    Copley away, Perry home, Nordonia home
#     4   10/3    [Copley home], Nordonia home
#     5   10/10   [Copley home]
#     6   10/17   Perry away
#     P1  10/24
#
# Updates 8/27 (TODO)
# B Teams - (11 Teams)
# Barberton-Copley-Ellet-Highland-Hudson Blue-Hudson White-Nordonia-Norton-Northwest-Perry-Parma-Tallmadge-Tuslaw 
# 
# C Teams - (10 Teams)
# Barberton-Copley-Ellet-Highland-Nordonia-Norton-Northwest-Perry-Tallmadge-Tuslaw
# 
# * Six game regular season schedule, with either a 2 or 3 week playoff depending upon completion of this schedule. I'm guessing a two week playoff schedule. (I only mention it because the goal would be to wrap up November 7 if possible, if not possible kids can play in the cold)
# * Equal home/away games if possible. This is also something if not possible, people would need to live with in 2020. Important, but people can F off if not possible.
# * Northwest home game 9/12
# * Tallmadge, Hudson & Tuslaw CANNOT play 9/5. If, for some reason we needed to start a division on 9/5 to make this work, those three teams need byes at all levels.
# * Nordonia would like a home game at least one, preferably twice 9/19, 9/26, 10/3 (HS turf). if one game opens your schedule up, once is fine.
# * Parma has one B Varsity only. Highland Green B JV should follow Parma's schedule though we shouldn't have to worry about that on your schedule. It'll just be known.
# * No Highland/Parma game. Director does not want his BJV's playing each other. If this is not possible, his teams can play each other. 
# * If it helps at all, Highland could host a D game (start early), Highland C & CJV games, Highland Black B games, and then Parma B/Highland Green JV games at his facility. If it is not possible or causes issues, then Highland Green BJV can travel around the globe with Parma B Varsity every single week. 
# * Hudson has two BV's and BJV's. Their Director would really prefer that both Hudson B Teams play at home on the same days and the road same weeks. He is having security, etc and like us, does not want to open his facility if unnecessary. If it is not possible, then he can deal with it but I told him we would do our best to accomodate.
# * Perry must be AWAY 9/12, 9/19, 10/3, 10/17
# * Anything previously mentioned with Copleys away schedule can be eliminated. They can play at any time now.
# * Tuslaw originally needed a home game 9/12, you can ELIMINATE this request.
# * Norton needs an AWAY game on 9/19 for all divisions
# 
# Obviously, the goal if possible for all Directors is to either be home or on the road. I can't imagine that is possible. We will worry about the D schedule once we iron this out. The issue with D becomes, we cannot find referees for ONE D game. So, ideally we have a D game going somewhere other games follow. Or, the nuclear option is we find a facility or two to host D games (can run both sides of the field) and we run the entire D schedule from those facilities only. 
#
#       


teams_2021_b_big = dict(
    BAR=Team('BAR', Field('Barberton')),
    ELL=Team('ELL', Field('Ellet')),
    NRT=Team('NRT', Field('Norton')),
    TAB=Team('TAB', Field('Tallmadge Blue')),
    TAG=Team('TAG', Field('Tallmadge Gold')),
    PER=Team('PER', Field('Perry')),
    STR=Team('STR', Field('Streetsboro')),
    BY1=Team('BY1', Field('*BYE 1*')),
    BY2=Team('BY2', Field('*BYE 2*')),
    BY3=Team('BY3', Field('*BYE 2*')),
    BY4=Team('BY4', Field('*BYE*')),
    BY5=Team('BY5', Field('*BYE*')),
)
teams_2021_b_sm = dict(
    NRW=Team('NRW', Field('Northwest')),
    TUS=Team('TUS', Field('Tuslaw')),
    BYE=Team('BYE', Field('*BYE*')),
)

overrides_2021_b_big = [
# Weeks
#     1   8/21  - Perry away
#     2   8/28 
#     3   9/4   - Barberton home (HS), Perry away
#     4   9/11
#     5   9/18  - Tallmadge home (HS - both), 
#     6   9/25  - Barberton home (HS)
#     7   10/2  - Barberton @ Norton
#     8   10/9  - Barberton home (HS)
#     9   10/16
#     P1  10/23

    dict(team='PER', week=1, force_away=True),
    dict(team='PER', week=3, force_away=True, force_opponent='BAR'),
    dict(team='TAB', week=5, force_home=True),
    dict(team='TAG', week=5, force_home=True),
    dict(team='BAR', week=6, force_home=True),
    dict(team='NRT', week=7, force_home=True, force_opponent='BAR'),
    dict(team='BAR', week=8, force_home=True),
    
]

teams_2021_c = dict(
    BAR=Team('BAR', Field('Barberton')),
    ELL=Team('ELL', Field('Ellet')),
    NRW=Team('NRW', Field('Northwest')),
    NRT=Team('NRT', Field('Norton')),
    TAL=Team('TAL', Field('Tallmadge')),
    TUS=Team('TUS', Field('Tuslaw')),
    PER=Team('PER', Field('Perry')),
    COP=Team('COP', Field('Copley')),
    NRD=Team('NRD', Field('Nordonia')),
    HGH=Team('HGH', Field('Highland')),
)

overrides_2021_c = [
    dict(team='NRT', week=1, force_home=True, avoid_opponents_this_week=['NRT', 'HGH', 'NRW', 'COP', 'BAR',]),
    dict(team='HGH', week=1, force_home=True, avoid_opponents_this_week=['NRT', 'HGH', 'NRW', 'COP', 'BAR',]),
    dict(team='NRW', week=1, force_home=True, avoid_opponents_this_week=['NRT', 'HGH', 'NRW', 'COP', 'BAR',]),
    dict(team='COP', week=1, force_home=True, avoid_opponents_this_week=['NRT', 'HGH', 'NRW', 'COP', 'BAR',]),
    dict(team='BAR', week=1, force_home=True, avoid_opponents_this_week=['NRT', 'HGH', 'NRW', 'COP', 'BAR',]),


    dict(team='TUS', week=2, force_home=True, avoid_opponents_this_week=['TUS', 'COP', 'ELL', 'NRD', 'BAR',]),
    dict(team='COP', week=2, force_home=True, avoid_opponents_this_week=['TUS', 'COP', 'ELL', 'NRD', 'BAR',]),
    dict(team='ELL', week=2, force_home=True, avoid_opponents_this_week=['TUS', 'COP', 'ELL', 'NRD', 'BAR',]),
    dict(team='NRD', week=2, force_home=True, avoid_opponents_this_week=['TUS', 'COP', 'ELL', 'NRD', 'BAR',]),
    #dict(team='BAR', week=2, force_home=True, avoid_opponents_this_week=['TUS', 'COP', 'ELL', 'NRD', 'BAR',]),


    dict(team='TUS', week=3, force_home=True, avoid_opponents_this_week=['TUS', 'NRW', 'BAR', 'PER', 'NRD',]),
    dict(team='NRW', week=3, force_home=True, avoid_opponents_this_week=['TUS', 'NRW', 'BAR', 'PER', 'NRD',]),
    dict(team='BAR', week=3, force_home=True, avoid_opponents_this_week=['TUS', 'NRW', 'BAR', 'PER', 'NRD',]),
    dict(team='PER', week=3, force_home=True, avoid_opponents_this_week=['TUS', 'NRW', 'BAR', 'PER', 'NRD',]),
    dict(team='NRD', week=3, force_home=True, avoid_opponents_this_week=['TUS', 'NRW', 'BAR', 'PER', 'NRD',]),


    dict(team='HGH', week=4, force_home=True, avoid_opponents_this_week=['HGH', 'TAL', 'TUS', 'NRT',]),
    dict(team='TAL', week=4, force_home=True, avoid_opponents_this_week=['HGH', 'TAL', 'TUS', 'NRT',]),
    dict(team='TUS', week=4, force_home=True, avoid_opponents_this_week=['HGH', 'TAL', 'TUS', 'NRT',]),
    dict(team='NRT', week=4, force_home=True, avoid_opponents_this_week=['HGH', 'TAL', 'TUS', 'NRT',]),


    dict(team='PER', week=5, force_home=True, avoid_opponents_this_week=['PER', 'ELL', 'NRT', 'TAL',]),
    dict(team='ELL', week=5, force_home=True, avoid_opponents_this_week=['PER', 'ELL', 'NRT', 'TAL',]),
    dict(team='NRT', week=5, force_home=True, avoid_opponents_this_week=['PER', 'ELL', 'NRT', 'TAL',]),
    dict(team='TAL', week=5, force_home=True, avoid_opponents_this_week=['PER', 'ELL', 'NRT', 'TAL',]),


    dict(team='NRW', week=6, force_home=True, avoid_opponents_this_week=['NRW', 'HGH', 'TAL', 'NRD', 'BAR',]),
    dict(team='HGH', week=6, force_home=True, avoid_opponents_this_week=['NRW', 'HGH', 'TAL', 'NRD', 'BAR',]),
    dict(team='TAL', week=6, force_home=True, avoid_opponents_this_week=['NRW', 'HGH', 'TAL', 'NRD', 'BAR',]),
    dict(team='NRD', week=6, force_home=True, avoid_opponents_this_week=['NRW', 'HGH', 'TAL', 'NRD', 'BAR',]),
    dict(team='BAR', week=6, force_home=True, avoid_opponents_this_week=['NRW', 'HGH', 'TAL', 'NRD', 'BAR',]),
]


teams_2021_d = dict(
    BAR=Team('BAR', Field('Barberton')),
    ELL=Team('ELL', Field('Ellet')),
    NRT=Team('NRT', Field('Norton')),
    TAL=Team('TAL', Field('Tallmadge')),
    COP=Team('COP', Field('Copley')),
    CO2=Team('CO2', Field('Copley 2')),  # Plan to 
    NRD=Team('NRD', Field('Nordonia')),
    HGH=Team('HGH', Field('Highland')),
)

overrides_2021_d = [
]


number_weeks = 9
enable_consecutive_check = False
teams = teams_2021_b_big
overrides = overrides_2021_b_big
overrides_by_week = {}

def get_overrides_by_week(week):
    if len(overrides_by_week.keys()) == 0:
        for override in overrides:
            if override is None:
                continue
            if overrides_by_week.get(override.get('week')) is None:
                overrides_by_week[override.get('week')] = []
            overrides_by_week[override.get('week')].append(override)
    return overrides_by_week.get(week) or []


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
            try:
                if override.get('force_opponent'):
                    team = teams[override['team']]
                    opponent = teams[override['force_opponent']]
                    if team.abbrev not in week_teams or opponent.abbrev not in week_teams or schedule.already_played(team, opponent):
                        raise CannotFulfillOverride
                    if override.get('force_home'):
                        schedule.add(Game(team, opponent, week, forced=True, is_bye=override.get('is_bye')))
                    else:
                        schedule.add(Game(opponent, team, week, forced=True, is_bye=override.get('is_bye')))
                    del week_teams[team.abbrev]
                    del week_teams[opponent.abbrev]

                elif override.get('force_home'):
                    team = teams[override['team']]
                    if team.abbrev not in week_teams:
                        raise CannotFulfillOverride
                    opponent = pick_random_opponent(team, week_teams, schedule, avoid_teams=override.get('avoid_opponents_this_week'))
                    schedule.add(Game(team, opponent, week, forced=True))
                    del week_teams[team.abbrev]
                    del week_teams[opponent.abbrev]

                elif override.get('force_away'):
                    team = teams[override['team']]
                    if team.abbrev not in week_teams:
                        raise CannotFulfillOverride
                    opponent = pick_random_opponent(team, week_teams, schedule, avoid_teams=override.get('avoid_opponents_this_week'))
                    schedule.add(Game(opponent, team, week, forced=True))
                    del week_teams[team.abbrev]
                    del week_teams[opponent.abbrev]
            except KeyError, e:
                raise e
                raise NoAvailableOpponnentError, "Cannot find opponent for %s in week %s" % (team, week)

        for abbrev, team in week_teams.items():
            if abbrev not in week_teams:
                continue
            try:
                opponent = pick_random_opponent(team, week_teams, schedule)

                # Check for bye
                schedule.add(Game(team, opponent, week, is_bye=_is_bye(team, opponent)))
                del week_teams[team.abbrev]
                del week_teams[opponent.abbrev]
            #except KeyError:
            #    raise NoAvailableOpponnentError, "Cannot find opponent for %s in week %s" % (team, week)
            except NoAvailableOpponnentError:
                raise NoAvailableOpponnentError, "Cannot find opponent for %s in week %s" % (team, week)

    # Validate opponent avoids
    for override in overrides:
        if override is not None and override.get('avoid_opponent'):
            if schedule.contains_matchup(override['team'], override['avoid_opponent']):
                raise IterationError('%s and %s should not play' % (override['team'], override['avoid_opponent']))

    # Validate Tallmadge 2 teams not sharing field
    for week in range(number_weeks):
        week = week + 1
        if schedule.is_home_in_week('TAG', week) and schedule.is_home_in_week('TAB', week):
            raise IterationError('TAG and TAB both home in week %s' % week)

    return schedule

def _is_bye(team, opponent):
    return team.abbrev is 'BYE' or opponent.abbrev is 'BYE' or team.abbrev.startswith('BY') or opponent.abbrev.startswith('BY')


pick_random_opponent_counter = 0

def pick_random_opponent(team, eligible_teams, schedule, avoid_teams=None):
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
        if avoid_teams and t.abbrev in avoid_teams:
            continue
        if schedule.already_played(team, t):
            continue
        return t
    raise NoAvailableOpponnentError



def make_schedules():
    """ Run an iterative constraint solver to attempt to generate a set of
        league schedules that satisfies all constraints.
    """
    max_outer_loop_iterations = 5000000
    max_rebalance_home_away_iterations = 5 * ((len(teams) * number_weeks) ** 2) #500000
    for i in range(max_outer_loop_iterations):
        if debug and (i % 1000 == 0):
            print("-", end="")
            sys.stdout.flush()
        try:
            b_schedule = try_make_b_team_schedule()
            b_schedule.add_bye_if_needed()
            print("--- MADE DIVISION SCHEDULE ---")
            b_schedule.print_schedule()

            # Special requests
            #if not b_schedule.contains_matchup('TAL', 'PER') and not b_schedule.contains_matchup('TAL', 'HUD'):
            #    print("Missing Tallmadge vs Perry|Hudson. Will try again (attempt %s)" % i)
            #    continue
            #if not b_schedule.contains_matchup('NRT', 'COP'):
            #    print("Missing Norton vs Copley. Will try again (attempt %s)" % i)
            #    continue

            # Now try to balance home game count for each team
            print("Now attempting to balance...")
            balanced = b_schedule.rebalance_home_away(max_rebalance_home_away_iterations)
            print("")
            print("--- HOME/AWAY BALANCED DIVISION SCHEDULE ---")
            b_schedule.print_schedule()

            #if not b_schedule.contains_matchup('TAL', 'PER', mode='away') and not b_schedule.contains_matchup('TAL', 'HUD', mode='away'):
            #    print("Missing Tallmadge @ Perry|Hudson. Will try again (attempt %s)" % i)
            #    continue

            if not balanced:
                print("Unable to balance teams.  Will try again (attempt %s)" % i)
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
            elif str(err):
                print("Unable to find optimal schedule.  Will try again (attempt %s)" % i)
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


