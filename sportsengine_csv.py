# vim:filetype=python:fileencoding=utf-8
#
# https://tallmadgeyouthfootball.sportngin.com/schedule_import
# https://help.sportsengine.com/customer/portal/articles/619699

from __future__ import print_function

se_vars = dict(
    CHI=dict(b_v='5171001', b_jv='5171015', c_v='5171028', c_jv='5171041'),
    ELL=dict(b_v='5171002', b_jv='5171017', c_v='5171030', c_jv='5171043', d='5171053'),
    MAN=dict(b_v='5171003', b_jv='5171018', c_v='5171031', c_jv='5171044', d='5171058'),
    NRW=dict(b_v='5171004', b_jv='5171019', c_v='5171032', c_jv='5171045'),
    NRT=dict(b_v='5171005', b_jv='5171020', c_v='5171033', c_jv='5171046', d='5171054'),
    SPR=dict(b_v='5171006', b_jv='5171022', c_v='5171035', c_jv='5171048', d='5171074'),
    TAB=dict(b_v='5171007', b_jv='5171023', c_v='5171036', c_jv='5171049', d='5171055'),
    TAG=dict(b_v='5171008', b_jv='5171024'),
    BAR=dict(b_v='5171009', b_jv='5171014', c_v='5171027', c_jv='5171040', d='5171059'),
    COV=dict(b_v='5171010', b_jv='5171016', c_v='5171029', c_jv='5171042'),
    RIT=dict(b_v='5171011', b_jv='5171021', c_v='5171034', c_jv='5171047'),
    TUS=dict(b_v='5171012', b_jv='5171025', c_v='5171038', c_jv='5171051'),
)

teams = dict(
    ELL=['Ellet', 'Ellet Youth Field', 'https://www.google.com/maps/place/2443+Wedgewood+Dr,+Akron,+OH+44312/@41.0508743,-81.4426126,17z/data=!3m1!4b1!4m2!3m1!1s0x8831295b6fb9f9c7:0xa668af2bd19f42c1', '2443 Wedgewood Dr, Akron'],
    TAB=['Tallmadge Blue', 'Tallmadge Overdale Field', 'https://www.google.com/maps/place/89+W+Overdale+Dr,+Tallmadge,+OH+44278/@41.106422,-81.443676,17z/data=!3m1!4b1!4m2!3m1!1s0x883128b92556a1c3:0xaaca2b04960afbcf', '89 W. Overdale Dr, Tallmadge'],
    TAG=['Tallmadge Gold', 'Tallmadge Overdale Field', 'https://www.google.com/maps/place/89+W+Overdale+Dr,+Tallmadge,+OH+44278/@41.106422,-81.443676,17z/data=!3m1!4b1!4m2!3m1!1s0x883128b92556a1c3:0xaaca2b04960afbcf', '89 W. Overdale Dr, Tallmadge'],
    NRW=['Northwest', 'Northwest Youth Fields', 'https://www.google.com/maps/place/8845+Erie+Ave+NW,+Canal+Fulton,+OH+44614/@40.9124449,-81.6234869,17z/data=!3m1!4b1!4m2!3m1!1s0x88372c15c938b217:0x1727523a64affc3f', '8845 Erie Ave NW, Canal Fulton'],
    MAN=['Manchester', 'Manchester Lockhart Field', 'https://www.google.com/maps/place/6100+Cherry+Alley,+Akron,+OH+44319/@40.9385034,-81.5716256,17z/data=!3m1!4b1!4m2!3m1!1s0x88372b0f5657bf81:0xf1df3c1d87ae2d6a', '6100 Cherry Alley, Akron'],
    SPR=['Springfield', 'Springfield Schrop MS', 'https://www.google.com/maps/place/2215+Pickle+Rd,+Akron,+OH+44312/@41.0036478,-81.4722628,17z/data=!3m1!4b1!4m2!3m1!1s0x88312afffd12a819:0x8f48886787cafad5', '2215 Pickle Rd, Akron'],
    NRT=['Norton', 'Norton Youth Field', 'https://www.google.com/maps/place/4060+Columbia+Woods+Dr,+Norton,+OH+44203/@41.0239512,-81.6474674,17z/data=!3m1!4b1!4m2!3m1!1s0x8830d253521d97d7:0x625f667f816456b2!6m1!1e1', '4060 Columbia Woods Dr, Norton'],
    BAR=['Barberton', 'Barberton Middle School', 'https://www.google.com/maps/place/Barberton+Middle+School/@41.0232237,-81.6071931,137m/data=!3m1!1e3!4m5!3m4!1s0x0:0x9a622b6119a2107!8m2!3d41.0237121!4d-81.6077026', '477 4th St NW, Barberton'],
    CHI=['Chippewa', 'Chippewa Middle School', 'https://www.google.com/maps/place/Chippewa+Middle+School/@40.9700088,-81.6944653,18z/data=!4m5!3m4!1s0x0:0x7b07482c758a6309!8m2!3d40.9706482!4d-81.6926757', '257 High St, Doylestown'],
    COV=['Coventry', 'Coventry Logan Field', 'https://www.google.com/maps/place/2701+N+Turkeyfoot+Rd,+Akron,+OH+44319/@41.014672,-81.5335387,820m/data=!3m2!1e3!4b1!4m5!3m4!1s0x8830d59c09ca9073:0x914549adeee737f9!8m2!3d41.014668!4d-81.53135', '2701 N. Turkeyfoot Rd, Akron'],
    RIT=['Rittman', 'Rittman Youth Field', 'https://www.google.com/maps/place/275+N+2nd+St,+Rittman,+OH+44270/@40.974878,-81.7874846,821m/data=!3m2!1e3!4b1!4m5!3m4!1s0x883734a43e5df131:0x27f5d435603008ae!8m2!3d40.974874!4d-81.785295', '275 N. Second St, Rittman'],
    TUS=['Tuslaw', 'Tuslaw Youth Field', 'https://www.google.com/maps/place/11881+Orrville+St+NW,+Massillon,+OH+44647/@40.838352,-81.5746997,17z/data=!3m1!4b1!4m5!3m4!1s0x883728ee684b943f:0x52637cbc5003c9e1!8m2!3d40.838352!4d-81.572511', '11881 Orrville St NW, Massillon'],
)

weeks = [
    '08/17/2019',
    '08/24/2019',
    '08/31/2019',
    '09/07/2019',
    '09/14/2019',
    '09/21/2019',
    '09/28/2019',
    '10/05/2019',
    '10/12/2019',
]

game_matrix_b_division = """
BAR	@TAG	MAN	ELL	@NRW	COV	@SPR	TAB	@NRT
CHI	@MAN	@COV	RIT	@TAG	@SPR	NRW	NRT	TUS
COV	@RIT	CHI	@MAN	TAB	@BAR	NRT	SPR	@ELL
ELL	NRW	SPR	@BAR	@TUS	@RIT	TAB	@MAN	COV
MAN	CHI	@BAR	COV	SPR	@TUS	@TAG	ELL	@TAB
NRT	SPR	@NRW	@TAB	RIT	TAG	@COV	@CHI	BAR
NRW	@ELL	NRT	TAG	BAR	@TAB	@CHI	TUS	@RIT
RIT	COV	@TAB	@CHI	@NRT	ELL	TUS	@TAG	NRW
SPR	@NRT	@ELL	TUS	@MAN	CHI	BAR	@COV	TAG
TAB	@TUS	RIT	NRT	@COV	NRW	@ELL	@BAR	MAN
TAG	BAR	@TUS	@NRW	CHI	@NRT	MAN	RIT	@SPR
TUS	TAB	TAG	@SPR	ELL	MAN	@RIT	@NRW	@CHI
"""

game_matrix_c_division = """
BAR	BYE	MAN	ELL	@NRW	COV	@SPR	TAB	@NRT	@TUS
CHI	@MAN	@COV	RIT	BYE	@SPR	NRW	NRT	TUS	@ELL
COV	@RIT	CHI	@MAN	TAB	@BAR	NRT	SPR	BYE	@NRW
ELL	NRW	SPR	@BAR	@TUS	@RIT	TAB	@MAN	BYE	CHI
MAN	CHI	@BAR	COV	SPR	@TUS	BYE	ELL	@TAB	@NRT
NRT	SPR	@NRW	@TAB	RIT	BYE	@COV	@CHI	BAR	MAN
NRW	@ELL	NRT	BYE	BAR	@TAB	@CHI	TUS	@RIT	COV
RIT	COV	@TAB	@CHI	@NRT	ELL	TUS	BYE	NRW	@SPR
SPR	@NRT	@ELL	TUS	@MAN	CHI	BAR	@COV	BYE	RIT
TAB	@TUS	RIT	NRT	@COV	NRW	@ELL	@BAR	MAN	BYE
TUS	TAB	BYE	@SPR	ELL	MAN	@RIT	@NRW	@CHI	BAR
"""

game_matrix_d_division = """
BAR	MAN	ELL	@NRT	TAB	@SPR	@MAN
ELL	SPR	@BAR	TAB	@SPR	MAN	@NRT
MAN	@BAR	@TAB	SPR	NRT	@ELL	BAR
NRT	@TAB	@SPR	BAR	@MAN	TAB	ELL
SPR	@ELL	NRT	@MAN	ELL	BAR	@TAB
TAB	NRT	MAN	@ELL	@BAR	@NRT	SPR
"""


# Handle B division (varsity and JV together)
rows = [r for r in game_matrix_b_division.split('\n') if r.strip() != ""]
for row in rows:
    cells = row.split('\t')
    home = cells[0]
    for i, opp in enumerate(cells):
        if i == 0:
            continue
        if '@' in opp:
            continue
        if opp == 'BYE':
            continue
        team_home = teams[home]
        team_opp = teams[opp]
        se_home = se_vars[home]
        se_opp = se_vars[opp]
        week = weeks[i - 1]

        print(
            week + '\t1:30 PM\t' + week + '\t3:00 PM\t' +
            'B Varsity - ' + team_opp[0] + ' @ ' + team_home[0] + '\t' +
            'Tackle - B Varsity\t' + team_home[1] + '\t' + team_home[2] + '\t' +
            ' \tGAME\t \t' +
            se_home['b_v'] + '\t \t1\t' + se_opp['b_v']
        )
        print(
            week + '\t3:00 PM\t' + week + '\t4:30 PM\t' +
            'B JV - ' + team_opp[0] + ' @ ' + team_home[0] + '\t' +
            'Tackle - B JV\t' + team_home[1] + '\t' + team_home[2] + '\t' +
            ' \tGAME\t \t' +
            se_home['b_jv'] + '\t \t1\t' + se_opp['b_jv']
        )

# Handle C division (varsity and JV together)
rows = [r for r in game_matrix_c_division.split('\n') if r.strip() != ""]
for row in rows:
    cells = row.split('\t')
    home = cells[0]
    for i, opp in enumerate(cells):
        if i == 0:
            continue
        if '@' in opp:
            continue
        if opp == 'BYE':
            continue
        team_home = teams[home]
        team_opp = teams[opp]
        se_home = se_vars[home]
        se_opp = se_vars[opp]
        week = weeks[i - 1]

        print(
            week + '\t12:00 PM\t' + week + '\t1:30 PM\t' +
            'C Varsity - ' + team_opp[0] + ' @ ' + team_home[0] + '\t' +
            'Tackle - C Varsity\t' + team_home[1] + '\t' + team_home[2] + '\t' +
            ' \tGAME\t \t' +
            se_home['c_v'] + '\t \t1\t' + se_opp['c_v']
        )
        print(
            week + '\t10:30 AM\t' + week + '\t12:00 PM\t' +
            'C JV - ' + team_opp[0] + ' @ ' + team_home[0] + '\t' +
            'Tackle - C JV\t' + team_home[1] + '\t' + team_home[2] + '\t' +
            ' \tGAME\t \t' +
            se_home['c_jv'] + '\t \t1\t' + se_opp['c_jv']
        )

# Handle D division
rows = [r for r in game_matrix_d_division.split('\n') if r.strip() != ""]
for row in rows:
    cells = row.split('\t')
    home = cells[0]
    for i, opp in enumerate(cells):
        if i == 0:
            continue
        if '@' in opp:
            continue
        if opp == 'BYE':
            continue
        team_home = teams[home]
        team_opp = teams[opp]
        se_home = se_vars[home]
        se_opp = se_vars[opp]
        week = weeks[i] # note, D team starts 1 week delayed

        print(
            week + '\t09:00 AM\t' + week + '\t10:30 AM\t' +
            'D Team - ' + team_opp[0] + ' @ ' + team_home[0] + '\t' +
            'Rookie Tackle - D Team\t' + team_home[1] + '\t' + team_home[2] + '\t' +
            ' \tGAME\t \t' +
            se_home['d'] + '\t \t1\t' + se_opp['d']
        )

