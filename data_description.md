## Table of Contents:
#### Data Overview
#### 5 Tables from UFCstats
1. [Table Summaries](https://github.com/mesterhammerfic/match_stats/new/master#ufcstats-data-tables)
2. [SQL Schema](https://github.com/mesterhammerfic/match_stats/new/master#postgresql)
3. [Data Dictionaries]

#### [12 Advanced Statistics Tables]
1. [Naming Conventions]
2. [Table Summaries]


# Data Overview
The data I'm using is scraped from the official [UFC stats website](http://www.ufcstats.com/statistics/events/completed),
which provides round-by-round data on strikes and grappling techniques used in a fight for each fighter. I scraped data
for every bout up until August 1st. The scraping and data preparation takes a singificant amount of time, so I provided 
the [data](data/ufcstats_data) in this repository through 5 separate CSV files as well as 12 [advanced statistics](data/ufc_stats/advanced_stats) 
CSV files which were [generated](notebooks/01_data_cleaning/07c_advanced_statistics_by_round.ipynb) from those 5 original tables.




### 1. UFCStats Data Tables
Table Name | Row Represents | Number of Observations | Unique ID column
-----------|----------------|------------------------|-----------------
events.csv |one UFC Event   |525                     |link
bouts.csv  |one UFC bout    |5,688                   |link
fighters.csv|one UFC fighter|2,045                   |link
general.csv|one fighter in round|26,244              |bout_link + fighter_link + round
events.csv |one fighter in round|26,244              |bout_link + fighter_link + round

### 2. PostgreSQL
These 5 tables are then [transferred](notebooks/01_data_cleaning/00_create_database.ipynb) to a local postgresql database with the following schema:
<img src="schema.png"
align="center"
alt="Markdown Monster icon"
width="600"/>

### 3. Data Dictionaries
#### events.csv
Column|Meaning
------|-------
Date|Date of Event
Location|City/State/Country
Attendance|Attendance at stadium
name|Official event name
link|link to ufcstats.com event page

#### bouts.csv
Column|Meaning
------|-------
Method|Method by which the winner was determined
Round|Round at which the bout ended
Time|Time in the round at which the bout ended
Timeformat|The length and number of rounds scheduled
Referee|Self-explanatory
details|Judges scorecards if it went to decision
event_link|link to ufcstats.com page of the event this bout was in
link|link to ufcstats.com bout page

#### fighters.csv
Column|Meaning
------|-------
Height|Height in feet and inches
Weight|Weight in lbs
Reach |Reach in inches
STANCE|Most common stance the fighter uses
DOB|Date of birth
name|fighter name recorded by UFC
link|link to ufcstats.com fighter page

#### general.csv
#### bouts.csv
Column|Meaning
------|-------
fighter|fighter name
kd|number of knockdowns
sig_str|(successful significant strikes) of (total sig. strike attempts)
sig_str_prcnt|Percent of sig. strikes that landed
total_str|includes non-significant strikes- (successful strikes) of (total attempts)

