import pandas as pd
import pickle

def get_id(string):
    """
    input: ufcstats link (string)
    output: last digits of link after the final '/'
    """
    return string.split('/')[-1]

def get_all_ids(df, fighter=True, bout=True, event=True):
    if fighter:
        df['fighter_id'] = df['fighter_link'].map(get_id)
    if bout:
        df['bout_id'] = df['bout_link'].map(get_id)
    if event:
        df['event_id'] = df['event_link'].map(get_id)
    return df

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

    fighter_metric = last_3_stats[metric].mean()
    return fighter_metric

def black_list_entry(entry, black_list):
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
    data = get_all_ids(data, fighter=fighter, bout=bout, event=event)
    data.drop_duplicates(inplace=True)
    return data


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

    ssa_m = fighter_bout_inst_group[target].mean()
    date = fighter_bout_inst_group['date'].max()
    fighter_id = fighter_bout_inst_group['fighter_id'].max()
    bout_id = fighter_bout_inst_group['bout_id'].max()

    fighter_bout_inst = pd.DataFrame(dict(bout_id = bout_id, fighter_id = fighter_id, date = date, ssa_m = ssa_m))
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
    if rounds:
        instances_df['round_id'] = instances_df['bout_id']+instances_df['round']
        key = 'round_id'
    else:
        key = 'bout_id'
        
    instances_df['inst_id'] = instances_df['bout_id'] + instances_df['fighter_id']
    
    fighter_0 = list(instances_df.groupby(key).inst_id.max())
    fighter_1 = list(instances_df.groupby(key).inst_id.min())

    mask = instances_df['inst_id'].map(lambda x: black_list_entry(x, fighter_0))
    instances_df_1 = instances_df[mask]
    instances_df_1

    mask = instances_df['inst_id'].map(lambda x: black_list_entry(x, fighter_1))
    instances_df_0 = instances_df[mask]
    instances_df_0
    
    if flip:
        model_df = pd.merge(instances_df_1, instances_df_0, on=key, suffixes=('_0', '_1'))
        return model_df
    else:
        model_df = pd.merge(instances_df_0, instances_df_1, on=key, suffixes=('_0', '_1'))
        return model_df
    
    
def remove_debut_bouts(df):
    """
    input: dataframe, bout or round instances with bout_id column
    output: dataframe with all debut bouts filtered out
    """
    debut_bouts = pickle.load(open('../../src/debut_bouts.pkl', 'rb'))
    
    mask = df['bout_id'].map(lambda x: black_list_entry(x, debut_bouts))
    df = df[mask]

    return df



def get_accuracy(row, stat):
    """
    input: dataframe row
    output: accuracy for a givent stat
    """
    if row[stat+'_a'] == 0:
        return pd.NA
    else:
        return row[stat+'_s']/row[stat+'_a']

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
    round_length = bout_groups.Time.max()
    # create row for final rounds
    final_round_lengths = pd.DataFrame(dict(round_id = round_id, round_length = round_length))
    final_round_lengths.set_index('round_id', inplace=True)
    # Fill in non-final rounds
    new_data = df.join(final_round_lengths, on='round_id', how='outer')
    new_data.round_length = new_data.round_length.fillna('5:00')
    # convert to timedelta
    new_data.round_length = '00:0' + new_data.round_length
    new_data.round_length = pd.to_timedelta(new_data.round_length)
    new_data.round_length.describe()
    
    #convert to minutes as a float
    new_data['minutes'] = new_data.round_length.map(lambda x: x.total_seconds()/60)
    return new_data

    
def filter_rounds(df):
    #filter out non-5-minute rounds
    non_standard_rounds = ['No Time Limit', '1 Rnd + OT (31-5)', '1 Rnd (20)', '1 Rnd (30)',
                   '1 Rnd + OT (30-5)', '1 Rnd + OT (30-3)', '1 Rnd (15)', '1 Rnd (18)',
                   '1 Rnd + OT (27-3)', '1 Rnd (10)', '1 Rnd + 2OT (15-3-3)',
                   '1 Rnd + OT (12-3)', '1 Rnd + 2OT (24-3-3)', '1 Rnd + OT (15-3)',
                   '1 Rnd (12)']
    mask = df.Timeformat.map(lambda x: black_list_entry(x, non_standard_rounds))
    data = df[mask]
    data.Timeformat.value_counts()
    return data
    

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
    This operates the same as the calculate_stats except that it is used only for stats
    that do not distinguish between attempts and successes. Accuracy and Defense is
    not calculated in this function.
    
    input: df - dataframe, round performances
           stat - the type of technique being measured {sig_str, td, total_str, td, etc.}
    output: dataframe with the the following metrics
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
        data[stat+'_p1m'] = data[stat] / data.minutes
        data[stat+'_p15m'] = data[stat] / (data.minutes/15)
    
    # add opponent stats to each row for defense and differential calculation
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