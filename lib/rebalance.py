import random
import sys
import math
from config import number_weeks, debug, max_consecutive_home_away_game_limit
from lib.picker import pick_random_away_game_for_team, pick_random_home_game_for_team


def rebalance_home_away(schedule, max_iterations):
    any_team_unbalanced = False
    game_balance = number_weeks / 2.0  # XXX: doesn't support odd schedules
    #balanced_home_counts = [int(game_balance)]
    balanced_home_counts = [
        int(math.ceil(game_balance)), int(math.floor(game_balance))]

    for i in range(max_iterations):
        if debug and (i % 1000 == 0):
            print(".", end="")
            sys.stdout.flush()

        any_team_unbalanced = False
        for team in schedule.teams:
            # Byes don't matter
            if team.startswith('BY'):  # BYE
                continue

            home_count = int(schedule.home_game_count_for_team(team))

            #print("%s - %s - %s" % (team, home_count, (home_count in [2, 3, 4])))

            # Equal number of home/away ... now check more complex requirements
            if home_count in balanced_home_counts:
                # Cannot not have more than 3 consecutive home/away
                if max_consecutive_home_away_game_limit:
                    max_consecutive = schedule.max_consecutive_home_or_away_games(
                        team)
                    if max_consecutive > max_consecutive_home_away_game_limit:
                        any_team_unbalanced = True
                        g1 = pick_random_home_game_for_team(schedule, team)
                        g2 = pick_random_away_game_for_team(schedule, team)
                        if not g1.forced and not g2.forced:
                            g1.swap()
                            g2.swap()

                # TAG/TAB cannot be both Home in same week (shared field)
                if team == "TAG" or team == "TAB":
                    g_home_weeks = map(lambda g: g.week,
                                       filter(lambda g: g.home.abbrev == 'TAG' and not g.is_bye, schedule.games_for_team('TAG')))
                    b_home_weeks = map(lambda g: g.week,
                                       filter(lambda g: g.home.abbrev == 'TAB' and not g.is_bye, schedule.games_for_team('TAB')))
                    shared_weeks = list(set(g_home_weeks) & set(b_home_weeks))
                    if len(shared_weeks) > 0:
                        # print("Fixing TAG/TAB sharing home in weeks %s" % shared_weeks)
                        any_team_unbalanced = True
                        rand_teams = ['TAG', 'TAB']
                        random.shuffle(rand_teams)
                        random.shuffle(shared_weeks)
                        g = schedule.game_for_team_in_week(
                            rand_teams[0], shared_weeks[0])
                        if not g.forced:
                            g.swap()

                continue

            # More or less than 4 home games ... try to rebalance
            any_team_unbalanced = True

            if home_count > math.ceil(game_balance):
                for i in range(home_count - int(math.ceil(game_balance))):
                    # be smarter than "random"; try to find one of the opponents
                    # that has too few home games if possible
                    g = pick_random_home_game_for_team(schedule, team,
                                                       sort_key=lambda game: schedule.home_game_count_for_team(game.away.abbrev))
                    if not g.forced:
                        g.swap()

            if home_count < math.floor(game_balance):
                for i in range(home_count):
                    # be smarter than "random"; try to find one of the opponents
                    # that has too many home games if possible
                    g = pick_random_away_game_for_team(schedule, team,
                                                       sort_key=lambda game: -1 * schedule.home_game_count_for_team(game.away.abbrev))
                    if g and not g.forced:
                        g.swap()

        if not any_team_unbalanced:
            return True

    return False
