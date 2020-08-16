# Match Stats
A predictive analytics projects for Mixed Martial Arts

# Goal
To provide predictions on the stylistic outcome of an MMA match so that even casual fans can find events they 
will enjoy even if they have no prior knowledge of the fighters. Essentially, I am trying to predict how each
fighter will behave in a match.

##### Current Status
A report on the current status of the project can be found [here](report/match_stats.pdf)

## Objectives
1. Develop stats using round by round data from UFCStats.com
    * Develop metrics that accurately capture a fighters stylistics tendencies and capabilities
    * Create a way to categorize fighters based on their fighting styles
    * Create a way to measure how a fighter typically responds to certain fighting styles
2. Build a machine learning model that uses these stats to predict how many strikes and takedowns will be 
attempted in each match
3. Deploy this model as a web application that makes predictions on upcoming fights

### Context
The current pay-per-view price of a UFC event is $64.99, which can be a lot of money to spend on an event you 
might not even enjoy. Oftentimes fans are dissapointed by what they thought would be an exciting main event, 
like the matchup between Israel Adesanya and Yoel Romero which drew [criticism](https://talksport.com/sport/mma/679619/dana-white-ufc-248-adesanya-romero/) 
for it's lack of action. If we could have predicted that this fight would be boring, many fans might've saved 
$65. Our goal is to provide customers with a way of predicting the likelihood that these fights will be exciting 
so that they can find events they will enjoy.

### Data
The data I'm using is scraped from the official [UFC stats website](http://www.ufcstats.com/statistics/events/completed),
which provides round-by-round data on strikes and grappling techniques used in a fight for each fighter. I scraped data
for every bout up until August 1st. The scraping and data preparation takes a significant amount of time, so I provided 
the [data](data/ufcstats_data) with this repository through 5 CSVs, as well as 12 [advanced statistics](data/ufcstats_data/advanced_stats) 
CSV files which were generated from those 5 original tables.
For more details on the data, including data dictionaries, checkout the data_descriptions file [here](data_description.md).

### Modelling
#### Target
The target variable for the current model iterations is the Combined Average Standing Significant Strike Attempts per Minute of a match. This is is the sum of the distance and clinch strikes thrown by both fighters, and it excludes ground strikes. Previous iterations calculated the combined significant strikes landed in the bout and the combined significant strike attempts per minute, both of which can be found in the archive folders in the notebooks/ directory. 'Combined Significant Strikes Landed in the Bout' was dropped because it failed to account for exciting fights with early finishes and title fights, which would increase or decrease the total number of strikes without indicating the level of activity. Combined Significant Strike Attempts per Minute accounts for early stoppages and 5 round fights by measure the rate of strikes, but this was dropped because it included the significant strikes on the ground, which are indicative of a grappling-centric match. The new target counts only distance and clinch strikes, which occur while both fighters are on their feet.

#### First Simple Model
The FSM for this project looked only at each fighters career average significant strike attempts per 15 minutes and attempted
to predict the combined significant strike attempts per 15 minutes of both fighters in the bout. This model was a Linear Regressor
and the data was scaled using sklearns standard scaler.


#### Latest Model
The latest model is a Linear Regressor that uses career averages for Significant Strike Attempts per 15 minutes and Takedown Attempts per 15 minutes as well as differentials for both of those stats. Differentials measure the difference in the rate of techniques used between a fighter and his opponent. For instance, if fighter A lands 50 strikes-per-minute, and fighter B lands 30 strikes-per-minute, fighter A has a strikes-per-minute-differential (S/PM-Di) of 20, and fighter B would be rated at -20.

Metric|First Simple Model|Latest Model
------|------------------|------------
R-Squared|.157|.180

#### Note on previous iterations
Previous iterations, which used Combined Significant Strikes Landed in the Bout and Combined Significant Strike Attempts per Minute, incorporated career and 3 fight averages. These models failed to perform better than the latest model above. These iterations include attempts to include ground strike differentials, 3 fight averages, min-max scaling, and random forest regressors. Because these features were tested on different target variables, they should be revisited on the current target. You can find the records of these previous iterations in the archive folders in 01_feature_engineering, 02_data_exploration, and 03_modelling

#### Next steps
It's possible that career long averages don't capture a fighters current abilities because they could have gotten better or worse since their first few fights. This data set also includes fighters with only 1 or 2 fights, which likely does not include enough information to make reliable predictions. We will include 3 fight averages and exclude all fighters with less than 3 fights.

### Methodology
This project follows the CRISP-DM model which starts with framing the problem using business understanding and cycles through
data understanding, data preperation, modelling, and evaluation before moving onto deployement.

<img src=references/CRISPDM_Process_Diagram.png width=400>

Due to the high emphasis on feature engineering, the notebook directory in this project breaks this process down into three stages:
1. 01_feature_engineering - new features are created using the original data set.
2. 02_data_exploration - new features are examined and tested using EDA.
3. 03_modelling - new features used on models to evaluate predictive abilities.

The numbered prefixes of each notebook indicate which iteration they are a part of such that the 01 notebook in 01_feature_engineering
is responsible for creating the features used in the 01 notebook in 01_modelling.

#### Technologies Used
- Python
   - Pandas
   - SciKit-Learn
   - NumPy
   - SciPy
   - SQLAlchemy
- Jupyter Labs
- Conda
- SQL & PostgreSQL

### Contributing/Reproducing
1. Fork and clone this repo, which includes all necessary data
2. [Set up](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) the project environment using Conda
3. Run the 00_create_database and 01_advanced_statistics_by_round notebooks in the [data_preparation directory](notebooks/00_data_preparation) to set up your PostgreSQL data tables
4. Follow the Methodolgy steps outlined in the previous section

### Directory Structure
```
project
│   README.md 
└───data
│   │
│   └───ufcstats_data - All data from ufcstats.com, CSVs
│       │ 
│       └───advanced_stats - Advanced Stats CSVs
|
└───notebooks
│   │
│   └───00_data_preparation - Creating SQL tables and advanced statistics tables
│   │
│   └───01_feature_engineering - All data cleaning and feature engineering
│   │    │ 
│   |    └───archive
|   |
│   └───02_data_exploration - All EDA
│   │    │ 
│   |    └───archive
│   |
│   └───03_modelling - All model iterations
│        │ 
│        └───archive
|           
└───references - literature and images used ofr research
|
└───report - latest report presentation and notebook
│   │
│   └───figures - figures used for reports
|
└───src - custom functions and pickled objects
```
