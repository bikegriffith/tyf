# tyf

Scripts used to assist with Tallmadge Youth Football and the Buckeye Youth Football Conference

* [2019 Schedule Maker](schedule.py): Randomized scheduler using mutation and
  constraint solving techniques to generate a valid schedule for the league that
  satifies all rules and requests asdf.
* [2019 SportsEngine CSV Import Maker](sportsengine_csv.py): Takes the output of
  the schedule maker and transforms it into the SportsEngine CSV format required
  for schedule entry.
