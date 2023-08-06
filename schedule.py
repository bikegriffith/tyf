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


import sys

from config import teams, overrides, number_weeks, debug, max_outer_loop_iterations, max_rebalance_home_away_iterations, require_bye

from lib.game import Game
from lib.team import Team
from lib.game import Game
from lib.printer import print_schedule
from lib.rebalance import rebalance_home_away
from lib.byes import is_bye, add_bye_if_needed
from lib.picker import pick_random_opponent, pick_random_opponent_counter
from lib.errors import NoAvailableOpponnentError, IterationError, CannotFulfillOverride


class LeagueSchedule:
    """ Used to build a schedule for the entire league for a given
        division and season.
    """

    def __init__(self, teams, num_weeks):
        self.teams = teams
        self.games = []
        self.num_weeks = num_weeks
        self.games_by_team = {}
        for abbrev in teams:
            self.games_by_team[abbrev] = []

    def print_schedule(self):
        print_schedule(self)

    def add(self, game):
        if debug:
            print(game)
        self.games.append(game)

        # optimization
        self.games_by_team[game.home.abbrev].append(game)
        self.games_by_team[game.away.abbrev].append(game)

    def already_played(self, a, b):
        for g in self.games_by_team[a.abbrev]:
            if g.home == a and g.away == b:
                return True
            if g.home == b and g.away == a:
                return True
        return False

    def game_for_team_in_week(self, abbrev, week):
        for g in self.games_by_team[abbrev]:
            if (g.away.abbrev == abbrev or g.home.abbrev == abbrev) and g.week == week:
                return g
        return None

    def games_for_team(self, abbrev):
        games = []
        for g in self.games_by_team[abbrev]:
            if g.away.abbrev == abbrev or g.home.abbrev == abbrev:
                games.append(g)
        games.sort(key=lambda g: g.week)
        return games

    def opponent_in_week(self, abbrev, week):
        for g in self.games_by_team[abbrev]:
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

    def has_bye(self, abbrev):
        for g in self.games_by_team[abbrev]:
            if (g.away.abbrev == abbrev or g.home.abbrev == abbrev) and g.is_bye:
                return True
        return False

    def every_team_has_one_bye(self):
        for team in teams:
            if not self.has_bye(team):
                return False
        return True

    def contains_matchup(self, abbrev1, abbrev2, mode=None):
        for g in self.games_by_team[abbrev1]:
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
        for g in self.games_by_team[abbrev]:
            if g.is_bye:
                continue
            if g.home.abbrev == abbrev:
                count = count + 1
        return count

    def is_away_in_week(self, abbrev, week):
        for g in self.games_by_team[abbrev]:
            if g.week != week:
                continue
            if g.is_bye:
                continue
            if g.away.abbrev == abbrev:
                return True
        return False

    def is_home_in_week(self, abbrev, week):
        for g in self.games_by_team[abbrev]:
            if g.week != week:
                continue
            if g.is_bye:
                continue
            if g.home.abbrev == abbrev:
                return True
        return False

    def max_cross_over_games_for_any_team(self):
        max_value = 0
        for team in teams:
            count = len([
                g for g in self.games_for_team(team)
                if not g.is_bye and g.home.division != g.away.division
            ])
            if count > max_value:
                max_value = count
            if count > 4:
                print("%s-%d, " % (team, count), end="")
        return max_value

    def validate_not_sharing_home_field(self):
        # Validate Tallmadge 2 teams not sharing field
        # XXX: Manual check
        for week in range(number_weeks):
            week = week + 1
            if self.is_home_in_week('TAG', week) and self.is_home_in_week('TAB', week):
                raise IterationError('TAG and TAB both home in week %s' % week)

    def __repr__(self):
        return "%s" % self.games


overrides_by_week = {}


def get_overrides_by_week(week):
    if len(list(overrides_by_week.keys())) == 0:
        for override in overrides:
            if override is None:
                continue
            if overrides_by_week.get(override.get('week')) is None:
                overrides_by_week[override.get('week')] = []
            overrides_by_week[override.get('week')].append(override)
    return overrides_by_week.get(week) or []


def generate_random_schedule_with_overrides():
    """ Generate the schedule randomly, returning an instance of LeagueSchedule.

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
                        schedule.add(
                            Game(team, opponent, week, forced=True, is_bye=override.get('is_bye')))
                    else:
                        schedule.add(
                            Game(opponent, team, week, forced=True, is_bye=override.get('is_bye')))
                    del week_teams[team.abbrev]
                    del week_teams[opponent.abbrev]

                elif override.get('force_home'):
                    team = teams[override['team']]
                    if team.abbrev not in week_teams:
                        raise CannotFulfillOverride
                    opponent = pick_random_opponent(
                        team, week_teams, schedule, avoid_teams=override.get('avoid_opponents_this_week'))
                    schedule.add(Game(team, opponent, week, forced=True))
                    del week_teams[team.abbrev]
                    del week_teams[opponent.abbrev]

                elif override.get('force_away'):
                    team = teams[override['team']]
                    if team.abbrev not in week_teams:
                        raise CannotFulfillOverride
                    opponent = pick_random_opponent(
                        team, week_teams, schedule, avoid_teams=override.get('avoid_opponents_this_week'))
                    schedule.add(Game(opponent, team, week, forced=True))
                    del week_teams[team.abbrev]
                    del week_teams[opponent.abbrev]
            except KeyError as e:
                raise e
                raise NoAvailableOpponnentError(
                    "Cannot find opponent for %s in week %s" % (team, week))

        for abbrev, team in list(week_teams.items()):
            if abbrev not in week_teams:
                continue
            if team.is_pseudo_team_bye():
                continue
            try:
                opponent = pick_random_opponent(team, week_teams, schedule)

                # Check for bye
                schedule.add(Game(team, opponent, week,
                             is_bye=is_bye(team, opponent)))
                del week_teams[team.abbrev]
                del week_teams[opponent.abbrev]
            # except KeyError:
            #    raise NoAvailableOpponnentError, "Cannot find opponent for %s in week %s" % (team, week)
            except NoAvailableOpponnentError:
                raise NoAvailableOpponnentError(
                    "Cannot find opponent for %s in week %s" % (team, week))

    # Validate opponent avoids
    for override in overrides:
        if override is not None and override.get('avoid_opponent'):
            if schedule.contains_matchup(override['team'], override['avoid_opponent']):
                raise IterationError('%s and %s should not play' % (
                    override['team'], override['avoid_opponent']))

    return schedule


def make_schedule():
    """ Run an iterative constraint solver to attempt to generate a set of
        league schedules that satisfies all constraints.
    """
    for i in range(max_outer_loop_iterations):
        if debug and (i % 1000 == 0):
            print("-", end="")
            sys.stdout.flush()
        try:
            schedule = generate_random_schedule_with_overrides()

            # Add byes in after we generate a schedule for any teams that didn't get one randomly assigned
            if require_bye:
                add_bye_if_needed(schedule)

            print("--- TENTATIVE DIVISION SCHEDULE ---")
            schedule.print_schedule()

            # Special requests not well modeled by other constraints/overrides
            # if not schedule.contains_matchup('TAL', 'PER') and not schedule.contains_matchup('TAL', 'HUD'):
            #    print("Missing Tallmadge vs Perry|Hudson. Will try again (attempt %s)" % i)
            #    continue

            # Everyone must have 1 and only 1 bye:
            if require_bye and not schedule.every_team_has_one_bye():
                print("Not everyone has a bye, will retry :(")
                continue

            # Now verify in division vs. cross-over count
            # if schedule.max_cross_over_games_for_any_team() > 4:
            #     print("Too many cross-over games. Will try again (attempt %s)" % i)
            #     continue

            # Now try to balance home game count for each team
            print("Now attempting to re-balance home/away...")
            balanced = rebalance_home_away(
                schedule, max_rebalance_home_away_iterations)

            # Final verifications
            print("Now checking for home field overbooking...")
            schedule.validate_not_sharing_home_field()

            print("")
            print("--- BALANCED DIVISION SCHEDULE ---")
            schedule.print_schedule()

            if not balanced:
                print("Unable to balance teams.  Will try again (attempt %s)" % i)
                continue

            break
        except IterationError as err:
            if str(err) and debug:
                print('Error: %s' % err)
            elif str(err):
                # print("Unable to find optimal schedule.  Will try again (attempt %s)" % i)
                print(".", end="")
            continue
    else:
        print("")
        print("Cannot find satisfactory schedule")

    print("{}M matches analyzed".format(
        1.0*pick_random_opponent_counter.value/1000000.0))


if __name__ == "__main__":
    make_schedule()
