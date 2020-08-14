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
CSV files which were [generated](notebooks/01_data_cleaning/07c_advanced_statistics_by_round.ipynb) from those 5 original tables.
For more details on the data, including data dictionaries, checkout the data_descriptions file [here](data_description.md).

### Modelling
#### First Simple Model
The FSM for this project looked only at each fighters career average successful significant strikes per round and attempted
to predict the combined total number of successful significant strikes for the entire bout. This target was changed because
it does take into account differing match lengths. For instance, main event fights, which last 5 rounds will have significantly
higher strike counts just because they last longer.


#### Latest Model
The latest model is a Poisson Regressor that uses 40 features to predict the Combined Significant Strike Attempts per 
Minute in a single fight. The features included the 3 fight and career averages for Significant Strike Attempts per 
Minute as well as differentials for grappling and striking stats including takedowns, ground strikes, distance strikes,
etc. The features were scaled using sklearns Standard Scaler object which standardizes values. It's performance was 
evaluated using the standard metric for Poisson regression, mean Poisson deviance, as well as r-squared, so that it 
can be compared to other types of models easily. Our goal is to predict at least 95% of the matches to within 5 strikes 
of the actual result, so this metric is also included.

Metric|First Simple Model|Latest Model
------|------------------|------------
Mean Poisson Deviance|.122|.143
R-Squared|.111|.128
% Within 5 Strikes|7.2%|47.7%

#### Previous Iterations
There is a notebook for each model iteration in the [modelling](notebooks/03_modelling) folder under the notebooks directory.
Each iteration builds upon the previous iteration with new features added (or previous features removed). Each notebook
is prefixed with a number indicating which iteration it is; these numbers can be matched up to corresponding notebooks
in the data_cleaning and data_exploration folders. Each iteration follows this workflow:
1. Import Data
2. Split into X and y
3. Split into train and test
4. Scale (usually a StandardScaler, some used a MinMaxScaler)
5. Cross validate
6. Score on test set


#### Next Steps
This and previous model iterations can be found in the [notebooks/03_modelling](notebooks_03_modelling) folder. Attempts 
to implement min-max scaling, polynomial features, and Random Forest Regressors failed to improve model performance. 
The features used are believed to lack enough predictive power for any significant improvement, so next steps will focus
on the development of new features using the original data set.

### Methodology
This project follows the CRISP-DM model which starts with framing the problem using business understanding and cycles through
data understanding, data preperation, modelling, and evaluation before moving onto deployement.

<img src=references/CRISPDM_Process_Diagram.png width=400>

Due to the high emphasis on feature engineering, the notebook directory in this project breaks this process down into three stages:
1. 01_data_cleaning - new features are created using the original data set.
2. 02_data_exploration - new features are examined and tested using EDA.
3. 03_modelling - new features used on models to evaluate predictive abilities.

The numbered prefixes of each notebook indicate which iteration they are a part of such that the 01 notebook in datacleaning
is responsible for creating the features used in the 01 notebook of modelling.

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
3. Run the 00_create_database notebook to set up your PostgreSQL data tables
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
│   └───01_data_cleaned - All data cleaning and feature engineering
│   │ 
│   └───02_data_exploration - All EDA
│   |
│   └───03_modelling - All model iterations
|           
└───references - literature and images used ofr research
|
└───report - latest report presentation and notebook
│   │
│   └───figures - figures used for reports
|
└───src - custom functions and pickled objects
```
