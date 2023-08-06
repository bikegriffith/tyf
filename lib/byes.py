from config import number_weeks, teams


def is_bye(team, opponent):
    return team.is_pseudo_team_bye() or opponent.is_pseudo_team_bye()


def add_bye_if_needed(schedule):
    if number_weeks % 2 == 0:
        return
    needs_bye = []
    for team in teams:
        if team.startswith('BY'):  # BYE
            continue
        if not schedule.has_bye(team):
            needs_bye.append(team)

    if len(needs_bye) == 2:
        g = schedule.contains_matchup(*needs_bye)
        if g and not g.forced:
            g.is_bye = True
            print('Changing game %s to bye' % g)
            return

    if len(needs_bye) == 4:
        g = schedule.contains_matchup(needs_bye[0], needs_bye[1])
        if g and not g.forced:
            g.is_bye = True
            print('Changing game %s to bye' % g)
            g = schedule.contains_matchup(needs_bye[2], needs_bye[3])
            if g and not g.forced:
                g.is_bye = True
                print('Changing game %s to bye' % g)
                return
            else:
                print('Unable to add bye for %s', needs_bye)
                return
        g = schedule.contains_matchup(needs_bye[0], needs_bye[2])
        if g and not g.forced:
            g.is_bye = True
            print('Changing game %s to bye' % g)
            g = schedule.contains_matchup(needs_bye[1], needs_bye[3])
            if g and not g.forced:
                g.is_bye = True
                print('Changing game %s to bye' % g)
                return
            else:
                print('Unable to add bye for %s', needs_bye)
                return
        g = schedule.contains_matchup(needs_bye[0], needs_bye[3])
        if g and not g.forced:
            g.is_bye = True
            print('Changing game %s to bye' % g)
            g = schedule.contains_matchup(needs_bye[1], needs_bye[2])
            if g and not g.forced:
                g.is_bye = True
                print('Changing game %s to bye' % g)
                return
            else:
                print('Unable to add bye for %s', needs_bye)
                return
    print('Unable to add bye for %s', needs_bye)
