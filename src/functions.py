import pandas as pd
import pickle


"""
===================================================================================
Data Cleaning
===================================================================================
"""
def get_id(string):
    """
    input: ufcstats link (string)
    output: last digits of link after the final '/'
    """
    return string.split('/')[-1]

def get_all_ids(df, fighter=True, bout=True, event=True):
    """
    input: dataframe with fighter_link, bout_link, and/or event_link columns
    output: dataframe with new columns set to the last string of characters of the link
            uses get_id()
            
    the resulting ids are for easier readability during trouble shooting only
    """
    if fighter:
        df['fighter_id'] = df['fighter_link'].map(get_id)
    if bout:
        df['bout_id'] = df['bout_link'].map(get_id)
    if event:
        df['event_id'] = df['event_link'].map(get_id)
    return df

def black_list_entry(entry, black_list):
    """
    This function will be deprecated soon and replaced with pandas isin method
    
    returns True if the entry is in the black_list
    used to create pandas masks for data cleaning
    
    example:
    df.column.map(lambda x: black_list_entry(x, [values to block]))
    """
    
    return entry not in black_list

def format_data(data, fighter=True, bout=True, event=True):
    """
    input: data - dataframe, either the general or the strikes dataframe from the postgresql database
    output: dataframe with no duplicates, 
            data column formatted to datetime, 
            round column converted to string, 
            and all id columns
    """
    data['date'] = pd.to_datetime(data['Date'])
    data['round'] = data['round'].map(str)
    return data

    
def remove_debut_bouts(df):
    """
    input: dataframe, bout or round instances with bout_id column
    output: dataframe with all debut bouts filtered out
    """
    debut_bouts = pickle.load(open('../../src/debut_bouts.pkl', 'rb'))
    
    mask = df['bout_id'].map(lambda x: black_list_entry(x, debut_bouts))
    df = df[mask]

    return df

def get_minutes(df):
    """
    input: dataframe with Time column
    output: dataframe with minutes column for each round
    """
    # create round_id
    df['round_id'] = df['bout_id']+df['round']
    # group into bouts
    bout_groups = df.groupby('bout_id')
    # create dataframe with round_id as index
    round_id = bout_groups.round_id.max()
    round_length = bout_groups.time.max()
    # create row for final rounds
    final_round_lengths = pd.DataFrame(dict(round_id = round_id, round_length = round_length))
    final_round_lengths.set_index('round_id', inplace=True)
    # Fill in non-final rounds
    new_data = df.join(final_round_lengths, on='round_id', how='outer')
    new_data.round_length = new_data.round_length.fillna('5:00')
    # convert to timedelta
    new_data.round_length = '00:0' + new_data.round_length
    new_data.round_length = pd.to_timedelta(new_data.round_length)
    
    #convert to minutes as a float
    new_data['minutes'] = new_data.round_length.map(lambda x: x.total_seconds()/60)
    return new_data

    
def five_minute_rounds(df):
    """
    returns the dataframe (df) with all non-5 minute rounds removed
    """
    standard_rounds = ['5 Rnd (5-5-5-5-5)', 
                       '3 Rnd (5-5-5)', 
                       '3 Rnd + OT (5-5-5-5)',
                       '2 Rnd (5-5)']
    mask = df.timeformat.isin(standard_rounds)
    data = df[mask]
    return data


def get_successful(string):
    """
    input: a string that follows the format: [number landed] of [number thrown] 
                                            ie 11 of 30 means they landed 11 strikes out of 30
    output: an integer of the number landed
                                            ie 11 from the example above
    """
    return int(string.split(' ')[0])

def get_attempts(string):
    """
    input: a string that follows the format: [number landed] of [number thrown] 
                                            ie 11 of 30 means they landed 11 strikes out of 30
    output: an integer of the number attempted
                                            ie 30 from the example above
    """
    return int(string.split(' ')[-1])

"""
===================================================================================
Metric Calculation
===================================================================================
"""
def calculate_metric_average(metric, fighter_id, date, df):
    """
    input: fighter_link - str, a unique fighter identifier
           date - datetime64, cut off date, metric will be calculated using every fight up until this date
           df - dataframe, a fighter-instance table containing the metric
    output: float, the metric for the fighter up until the date
    """
    fighter_history = df[(df['fighter_id']==fighter_id)&
                         (df['date']<date)]
    fighter_metric = fighter_history[metric].mean()
    return fighter_metric

def calculate_3_fight_average(metric, fighter_id, date, df):
    """
    input: fighter_link - str, a unique fighter identifier
           date - datetime64, cut off date, metric will be calculated using every fight up until this date
           df - dataframe, a fighter-instance table containing the metric
    output: float, the metric for the 3 fights prior to the date
    """
    fighter_history = df[(df['fighter_id']==fighter_id)&
                         (df['date']<date)].sort_values('Date')

    last_3 = fighter_history['bout_id'].unique()[-3:]
    mask = fighter_history['bout_id'].map(lambda x: True if x in last_3 else False)
    last_3_stats=fighter_history[mask]
    if len(last_3_stats)>=3:
        fighter_metric = last_3_stats[metric].mean()
        return fighter_metric
    else:
        return pd.NA

    
def calculate_stats(df, stat_list):
    """
    input: df - dataframe, round performances
           stat - the type of technique being measured {sig_str, td, total_str, td, etc.}
    output: dataframe with the the following metrics
     - A -  Attempts
     - S -  Successes
     - _AC_PR -  Accuracy Per Round
     - _DE_PR -  Defense Per Round
     - A_PR_DI - Attempt Differential
     - S_PR_DI - Success Differential
     - A_P1M -  Attempts Per 1 Minute
     - S_P1M -  Successes Per 1 Minute
     - A_P15M -  Attempts Per 15 Minute
     - S_P15M -  Successes Per 15 Minute
     - A_P1M_DI -  Attempts Per 1 Minute
     - S_P1M_DI -  Successes Per 1 Minute
     - A_P15M_DI -  Attempts Per 15 Minute
     - S_P15M_DI -  Successes Per 15 Minute
    """
    print('formatting data\n')
    data = format_data(df, event=False)
    
    #remove non-5-minute rounds
    data = filter_rounds(data)
    
    # calculate minutes
    print('calculating minutes\n')
    data = get_minutes(data)
    for stat in stat_list:
        data[stat+'_a_p1m'] = data[stat+'_a'] / data.minutes
        data[stat+'_s_p1m'] = data[stat+'_s'] / data.minutes
        data[stat+'_a_p15m'] = data[stat+'_a'] / (data.minutes/15)
        data[stat+'_s_p15m'] = data[stat+'_s'] / (data.minutes/15)

        # calculate accuracy
        print(f'calculating accuracy for {stat}\n')
        data[stat+'_ac'] = data.apply(lambda x: get_accuracy(x, stat), axis=1)
    
    # add opponent stats to each row for defense and differential calculation
    print('combining rows\n')
    data_0 = merge_fighter_instances(data, rounds=True)
    data_1 = merge_fighter_instances(data, rounds=True, flip=True)
    data = pd.concat((data_0, data_1))
    
    for stat in stat_list:
        # calculate defense
        print(f'calculating defense for {stat}\n')
        data[stat+'_de_0'] = 1 - data[stat+'_ac_1']

        # calculate differentials
        print(f'calculating differentials for {stat}\n')
        #per round differentials
        data[stat+'_s_pr_di_0'] = data[stat+'_s_0'] - data[stat+'_s_1']
        data[stat+'_a_pr_di_0'] = data[stat+'_a_0'] - data[stat+'_a_1']
        #per minute differentials
        data[stat+'_s_p1m_di_0'] = data[stat+'_s_p1m_0'] - data[stat+'_s_p1m_1']
        data[stat+'_a_p1m_di_0'] = data[stat+'_a_p1m_0'] - data[stat+'_a_p1m_1']
        #per 15 minute differentials
        data[stat+'_s_p15m_di_0'] = data[stat+'_s_p15m_0'] - data[stat+'_s_p15m_1']
        data[stat+'_a_p15m_di_0'] = data[stat+'_a_p15m_0'] - data[stat+'_a_p15m_1']

    print('cleaning df\n')
    # return only the first fighters stats
    columns_0 = [column for column in data.columns if column[-2:]=='_0']
    data = data.loc[:,columns_0]
    data.columns = [column[:-2].lower() for column in data.columns]
    return data

def calculate_stats_alt(df, stat_list):
    """
    input: df - dataframe, rounds table
           stat - the type of technique being measured {sig_str, td, total_str, td, etc.}
    output: dataframe with the the following metrics calculated for each stat (ss, td, etc)
     - _pr_di - Per Round Differential
     - _p1m - Per 1 Minute
     - _p15m - Per 15 Minute
     - _p1m_di- Per 1 Minute Differential
     - _p15m_di - Attempts Per 15 Minute
    """
    #remove non-5-minute rounds
    data = five_minute_rounds(df)
    
    # calculate minutes
    print('calculating minutes\n')
    data = get_minutes(data)
    for stat in stat_list:
        data[stat+'_p1m'] = data[stat] / data.minutes
        data[stat+'_p15m'] = data[stat] / (data.minutes/15)
    
    # add opponent stats to each row for differential calculation
    print('combining rows\n')
    data_0 = merge_fighter_instances(data, rounds=True)
    data_1 = merge_fighter_instances(data, rounds=True, flip=True)
    data = pd.concat((data_0, data_1))
    
    for stat in stat_list:
        # calculate differentials
        print(f'calculating differentials for {stat}\n')
        #per round differentials
        data[stat+'_pr_di_0'] = data[stat+'_0'] - data[stat+'_1']
        #per minute differentials
        data[stat+'_p1m_di_0'] = data[stat+'_p1m_0'] - data[stat+'_p1m_1']
        #per 15 minute differentials
        data[stat+'_p15m_di_0'] = data[stat+'_p15m_0'] - data[stat+'_p15m_1']

    print('cleaning df\n')
    # return only the first fighters stats
    columns_0 = [column for column in data.columns if column[-2:]=='_0']
    data = data.loc[:,columns_0]
    data.columns = [column[:-2].lower() for column in data.columns]
    return data

def get_accuracy(row, stat):
    """
    input: dataframe row
    output: accuracy for a givent stat
    """
    if row[stat+'_a'] == 0:
        return pd.NA
    else:
        return row[stat+'_s']/row[stat+'_a']
    

"""
===================================================================================
Table Transformations
===================================================================================
"""
def create_fighter_bout_instance_table(data, target):
    """
    input: dataframe, a formatted fighter round instance table, either general stats or strike stats.
    output: new fighter bout instance dataframe 

    A fighter-bout instance represents one fighter in one bout.
     - The same fighter has exactly one fighter-bout instance for every single bout he has been in. 
     - Every bout has exactly two fighter-bout instances, one for each fighter in the bout. 
    In this case a fighter-bout instance is assigned a unique identifier comprised of the bout_id combined with the fighter_link.
    """
    
    data['fighter_bout_inst'] = data['bout_id'] + data['fighter_id']
    fighter_bout_inst_group = data.groupby(['fighter_bout_inst'])

    target = fighter_bout_inst_group[target].mean()
    date = fighter_bout_inst_group['date'].max()
    fighter_id = fighter_bout_inst_group['fighter_id'].max()
    bout_id = fighter_bout_inst_group['bout_id'].max()

    fighter_bout_inst = pd.DataFrame(dict(bout_id = bout_id, fighter_id = fighter_id, date = date, target = target))
    return fighter_bout_inst


def merge_fighter_instances(instances_df, flip=False, rounds=False):
    """
    input: instance table where each row represents one fighter in one bout (in one round, if round instances)
    output: table where each row represents both fighters in a single bout (or round, if round instances)
    
    example input
    fighter_bout_instance_table:
    name:     |bout: 
    fighter_0 |1
    fighter_1 |1
    fighter_0 |2
    fighter_1 |2
    
    example output
    bout_table
    name_0:   |name_1:    |bout: 
    fighter_0 |fighter_1  |1
    fighter_0 |fighter_1  |2
    """
    # set the primary key for the rows to be joined on
    if rounds:
        instances_df['round_id'] = instances_df['bout_id']+instances_df['round']
        key = 'round_id'
    else:
        key = 'bout_id'
    
    # identifier for each fighter in each bout
    instances_df['inst_id'] = instances_df['bout_id'] + instances_df['fighter_id']
    
    # Create two lists of instance IDs, 
    # both list has one fighter per bout, 
    # both lists are unique.
    # if they are concatenated together they would 
    # create the original list of fighter instances
    fighter_0 = list(instances_df.groupby(key).inst_id.max())
    fighter_1 = list(instances_df.groupby(key).inst_id.min())
    
    # filter the instances dataframe using the lists above
    mask = instances_df['inst_id'].isin(fighter_0)
    instances_df_0 = instances_df[mask]
    instances_df_0

    mask = instances_df['inst_id'].isin(fighter_1)
    instances_df_1 = instances_df[mask]
    instances_df_1
    
    # Used for creating advanced statistics. reverses the order of the fighters
    if flip:
        model_df = pd.merge(instances_df_1, instances_df_0, on=key, suffixes=('_0', '_1'))
        return model_df
    else:
        model_df = pd.merge(instances_df_0, instances_df_1, on=key, suffixes=('_0', '_1'))
        return model_df
    

