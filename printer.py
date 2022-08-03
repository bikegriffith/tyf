
def print_schedule(schedule):
    teams = list(schedule.teams.values())
    teams.sort(key=lambda t: t.abbrev)
    for team in teams:
        ta = team.abbrev
        if team.is_pseudo_team_bye():
            continue
        opponents = [schedule.opponent_in_week(ta, i+1) for i in range(schedule.num_weeks)]
        unplayed = list(set(t for t in list(schedule.teams.keys()) if t != ta) - set(o.lstrip('@') for o in opponents))
        line = "%s:\t" % ta
        for opponent in opponents:
            if opponent.startswith('BY'):
                opponent = '*BYE*'
            line += "%s\t" % opponent
        line += "<" + ",".join(unplayed) + ">"
        line += "\t" + str(schedule.home_game_count_for_team(ta))
        print(line)