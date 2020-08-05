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
                         (df['Date']<date)]
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
                         (df['Date']<date)].sort_values('Date')

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
    data['Date'] = data['Date'].map(pd.to_datetime)
    data['round'] = data['round'].map(str)
    data = get_all_ids(data, fighter=fighter, bout=bout, event=event)
    data.drop_duplicates(inplace=True)
    return data

def create_fighter_bout_instance_table(data):
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

    sss_bout = fighter_bout_inst_group.sig_str_successful.mean()
    date = fighter_bout_inst_group['Date'].max()
    fighter_id = fighter_bout_inst_group['fighter_id'].max()
    bout_id = fighter_bout_inst_group['bout_id'].max()

    fighter_bout_inst = pd.DataFrame(dict(bout_id = bout_id, fighter_id = fighter_id, date = date, sss_bout = sss_bout))
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