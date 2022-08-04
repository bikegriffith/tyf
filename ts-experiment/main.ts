class Team {
  abbrev: string;
  division: string;

  constructor(abbrev: string, division: string) {
    this.abbrev = abbrev;
    this.division = division;
  }
}

class Game {
  home: Team;
  away: Team;
  week: number;
  forced: boolean;
  is_bye: boolean;

  constructor(
    home: Team,
    away: Team,
    week: number,
    forced: boolean,
    is_bye: boolean
  ) {
    this.home = home;
    this.away = away;
    this.week = week;
    this.forced = forced;
    this.is_bye = is_bye;
  }

  swap() {
    const temp = this.home;
    this.home = this.away;
    this.away = temp;
  }

  toString() {
    return `Week ${this.week} - ${this.home.abbrev} vs ${this.away.abbrev}`;
  }
}

class LeagueSchedule {
  teams: Team[];
  games: Game[];
  weeks: number;

  constructor(teams: Team[], weeks: number) {
    this.teams = teams;
    this.weeks = weeks;
    this.games = [];
  }

  add(game: Game) {
    this.games.push(game);
  }

  printSchedule() {
    const teams = this.teams.sort((a, b) => a.abbrev.localeCompare(b.abbrev));
    teams.forEach((t) => {
      const ta = t.abbrev;
      const opponents = [];
      for (let i = 0; i < this.weeks; i++) {
        opponents.push(this.opponentInWeek(ta, i + 1));
      }
      const unplayed = [];
      // TODO: unplayed = list(set(t for t in self.teams.keys() if t != ta) - set(o.lstrip('@') for o in opponents))
      console.log(`${ta}:\t${opponents.join('\t')}\t[-${unplayed.join(', ')}]`);
    });
  }

  opponentInWeek(team: Team, week: number): string {
    for (let i = 0; i < this.games.length; i++) {
      const g = this.games[i];
      if (g.week !== week) continue;
      if (g.home === team) {
        return g.is_bye ? '*BYE*' : g.away.abbrev;
      }
      if (g.away === team) {
        return g.is_bye ? '*BYE*' : `@${g.home.abbrev}`;
      }
    }
    return '';
  }

  alreadyPlayed(team: Team, opponent: Team): boolean {
    for (let i = 0; i < this.games.length; i++) {
      const g = this.games[i];
      if (g.home == team && g.away == opponent) {
        return true;
      }
      if (g.away == team && g.home == opponent) {
        return true;
      }
    }
    return false;
  }
}

const teams = [
  // B-Big
  new Team('BAR', 'BB'),
  new Team('ELL', 'BB'),
  new Team('NRT', 'BB'),
  new Team('PER', 'BB'),
  new Team('STR', 'BB'),
  new Team('TAB', 'BB'),
  new Team('TAG', 'BB'),
  // B-Small
  new Team('SPR', 'BS'),
  new Team('COV', 'BS'),
  new Team('WOD', 'BS'),
  new Team('CHI', 'BS'),
  new Team('NWR', 'BS'),
  new Team('MAN', 'BS'),
  new Team('TUS', 'BS'),
];


const schedule = new LeagueSchedule(teams, 9);

schedule.add(new Game(teams[0], teams[1], 1, false, false));
schedule.add(new Game(teams[2], teams[3], 1, false, false));
schedule.add(new Game(teams[0], teams[2], 2, false, false));
schedule.add(new Game(teams[1], teams[3], 2, false, false));
schedule.add(new Game(teams[0], teams[3], 3, false, false));
schedule.add(new Game(teams[1], teams[2], 3, false, false));

schedule.printSchedule();
