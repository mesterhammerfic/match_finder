## Table of Contents:
#### Data Overview
#### 5 Tables from UFCstats
1. [Table Summaries](https://github.com/mesterhammerfic/match_stats/new/master#ufcstats-data-tables)
2. [Schema](https://github.com/mesterhammerfic/match_stats/new/master#postgresql)
3. [Data Dictionaries](https://github.com/mesterhammerfic/match_stats/new/master#3-data-dictionaries)

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

### 2. Scheme
These 5 tables are then [transferred](notebooks/01_data_cleaning/00_create_database.ipynb) to a local postgresql database follow this schema:
<img src="schema.png"
align="center"
alt="Markdown Monster icon"
width="600"/>

## 3. Data Dictionaries
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

#### rounds.csv
Column|Meaning
------|-------
fighter     
ss          
h_ss        
b_ss        
l_ss        
d_ss        
c_ss        
g_ss        
kd          
ts          
td          
sba         
ps          
rev         
outcome     
bout_id     
fighter_id  
round       
ss_s        
ss_a        
h_ss_s      
h_ss_a       
b_ss_s       
b_ss_a       
l_ss_s       
l_ss_a       
d_ss_s       
d_ss_a       
c_ss_s       
c_ss_a       
g_ss_s       
g_ss_a       
ts_s         
ts_a         
td_s         
td_a         

