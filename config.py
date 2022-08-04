###
### League and Season Configuration
###

from team import Team

number_weeks = 9

# XXX: this may be too aggressive; we can solve it with 3
max_consecutive_home_away_game_limit = 2

debug = False

teams = dict(
    BAR=Team('BAR', 'B'),
    ELL=Team('ELL', 'B'),
    NRT=Team('NRT', 'B'),
    TAB=Team('TAB', 'B'),
    TAG=Team('TAG', 'B'),
    PER=Team('PER', 'B'),
    STR=Team('STR', 'B'),
    RAV=Team('RAV', 'B'),
    WOD=Team('WOD', 'B'),
    CHI=Team('CHI', 'B'),
    NWR=Team('NWR', 'B'),
    MAN=Team('MAN', 'B'),

    # Byes
    BY1=Team('BY1', '-'),
    BY2=Team('BY2', '-'),
)

overrides = [
    dict(team='BAR', week=1, force_home=True),
    dict(team='NRT', week=7, force_home=True, force_opponent='BAR'),

    dict(team='PER', week=1, force_away=True),
    dict(team='PER', week=4, force_away=True),

    dict(team='STR', week=1, force_home=True, force_opponent='BY1'),

    dict(team='RAV', week=3, force_home=True),

    dict(team='WOD', week=7, force_away=True),

    dict(team='CHI', week=2, force_home=True, avoid_opponents_this_week=['BY1', 'BY2']),
    dict(team='CHI', week=3, force_home=True, avoid_opponents_this_week=['BY1', 'BY2']),
    dict(team='CHI', week=4, force_away=True, avoid_opponents_this_week=['BY1', 'BY2']),
    dict(team='CHI', week=5, force_home=True, avoid_opponents_this_week=['BY1', 'BY2']),
    dict(team='CHI', week=6, force_home=True, avoid_opponents_this_week=['BY1', 'BY2']),

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