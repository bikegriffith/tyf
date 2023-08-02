###
# League and Season Configuration
###

from team import Team

number_weeks = 8

require_bye = False

# XXX: this may be too aggressive; we can solve it with 3
max_consecutive_home_away_game_limit = 3

debug = False

teams = dict(
    TAB=Team('TAB', 'B'),
    TAG=Team('TAG', 'B'),
    CHI=Team('CHI', 'B'),
    RAV=Team('RAV', 'B'),
    WOD=Team('WOD', 'B'),
    PER=Team('PER', 'B'),
    ELL=Team('ELL', 'B'),
    NRT=Team('NRT', 'B'),
    NWR=Team('NWR', 'B'),
    STR=Team('STR', 'B'),
    BAR=Team('BAR', 'B'),
    MAN=Team('MAN', 'B'),

    # Byes
    # BY1=Team('BY1', '-'),
    # BY2=Team('BY2', '-'),
)

# Weeks
# 1 - 8/19
# 2 - 8/26
# 3 - 9/2
# 4 - 9/9
# 5 - 9/16
# 6 - 9/23
# 7 - 9/30
# 8 - 10/7

overrides = [
    # Barberton @ Norton 9/30
    dict(team='NRT', week=7, force_home=True, force_opponent='BAR'),

    # Chippeway Home 8/19, 8/26, 9/9, 10/7
    dict(team='CHI', week=1, force_home=True),
    dict(team='CHI', week=2, force_home=True),
    dict(team='CHI', week=4, force_home=True),
    dict(team='CHI', week=8, force_home=True),

    # Ravenna 9/16 bye or away
    dict(team='RAV', week=5, force_away=True),

    # Perry away 9/9
    dict(team='PER', week=4, force_away=True),

    # Woodridge away 9/30
    dict(team='WOD', week=7, force_away=True),

    # Streetsboro away 9/9
    dict(team='STR', week=4, force_away=True),

    # Ravenna/Woodridge/Chippewa should play (no C JVs)
    # TODO:

    # Tallmadge should not play itself
    dict(team='TAG', avoid_opponent='TAB'),
]

# number of random schedules to generate before giving up
max_outer_loop_iterations = 15000000

# number of attempts to rebalance home/away within a given schedule
# before giving up and trying a new randomly generated one
# cutting this back because it seems to either get it pretty quickly or never at all
# max_rebalance_home_away_iterations = 50 * ((len(teams) * number_weeks) ** 2) #500000
max_rebalance_home_away_iterations = ((len(teams) * number_weeks) ** 2)
