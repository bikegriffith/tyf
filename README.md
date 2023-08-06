# tyf

Scripts used to assist with Tallmadge Youth Football and the Buckeye Youth Football Conference

- [Schedule Maker](schedule.py): Randomized schedule generator, based on your [config](config.py).
- [2019 SportsEngine CSV Import Maker](sportsengine_csv.py): Takes the output of
  the schedule maker and transforms it into the SportsEngine CSV format required
  for schedule entry.

## Why?

Simple round-robin scheduling isn't adequate to properly create a schedule for a league like ours. You can try to make it in Excel with grit and determination alone, but you'll quickly find how complex it is.

This repository contains a python project that implements a randomized scheduler using mutation and constraint solving techniques to generate a valid schedule for the league that satifies all rules and requests.

Some of the rules this helps solve:

- Handling requests for specific matchups on specific days
- Balancing equal number of home/away games
- Avoiding too many home or away games in a row
- Keeping teams that share the same field from playing home on the same week
- Ensuring everyone has the right number of byes
- Balancing large vs. small school matchups
- Matching up across different age groups with different teams in each division

## Usage

Update the values in `config.py` to reflect the season settings

When ready, run `schedule.py`. This may take millions of iterations to solve, depending on the complexity of the season's requirements. Eventually, the process will end and you will be left with output similar to the following:

```
--- BALANCED DIVISION SCHEDULE ---
BAR:	@WOD	ELL	@STR	*BYE*	NWR	PER	@NRT	@RAV	CHI	<MAN,BY1,TAG,TAB,BY2>	4
CHI:	PER	NRT	@TAB	TAG	*BYE*	@NWR	@RAV	WOD	@BAR	<ELL,MAN,BY1,STR,BY2>	4
ELL:	RAV	@BAR	*BYE*	@NRT	TAB	WOD	@PER	NWR	@MAN	<BY1,STR,TAG,CHI,BY2>	4
MAN:	@TAB	@TAG	@RAV	WOD	*BYE*	STR	@NWR	PER	ELL	<BY1,BAR,NRT,CHI,BY2>	4
NRT:	@STR	@CHI	*BYE*	ELL	@WOD	@TAG	BAR	TAB	RAV	<MAN,BY1,PER,NWR,BY2>	4
NWR:	TAG	*BYE*	@WOD	PER	@BAR	CHI	MAN	@ELL	@TAB	<BY1,RAV,STR,NRT,BY2>	4
PER:	@CHI	TAB	TAG	@NWR	*BYE*	@BAR	ELL	@MAN	STR	<BY1,RAV,NRT,WOD,BY2>	4
RAV:	@ELL	@STR	MAN	*BYE*	@TAG	TAB	CHI	BAR	@NRT	<BY1,PER,NWR,WOD,BY2>	4
STR:	NRT	RAV	BAR	@TAB	*BYE*	@MAN	WOD	@TAG	@PER	<ELL,BY1,NWR,CHI,BY2>	4
TAB:	MAN	@PER	CHI	STR	@ELL	@RAV	*BYE*	@NRT	NWR	<BY1,BAR,TAG,WOD,BY2>	4
TAG:	@NWR	MAN	@PER	@CHI	RAV	NRT	*BYE*	STR	@WOD	<ELL,BY1,BAR,TAB,BY2>	4
WOD:	BAR	*BYE*	NWR	@MAN	NRT	@ELL	@STR	@CHI	TAG	<BY1,RAV,PER,TAB,BY2>	4
```

To run more processes in parallel, execute `run_concurrent.py` -- this will stop once any one of the processes finds a valid solution.
