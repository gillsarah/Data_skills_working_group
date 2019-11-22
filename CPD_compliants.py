
from zipfile import ZipFile
import os 
import pandas as pd

#this is the path to the chicago-police-data GitHub, 
#used to access unified_data.zip and discipline_penalty_codes.csv
data_path = '/Users/Sarah/Documents/GitHub/chicago-police-data/data'

#this is the save-to path, this is where the unified_data.zip unzips to
#and where we read the accused, investigators and victims data from (out of the unzipped contents)
path =  '/Users/Sarah/Documents/GitHub/assignment-4-gillsarah'
path_2 = '/Users/Sarah/Documents/GitHub/assignment-5-sarah-gill-1'

profile_path = 'unified_data/profiles/officer-profiles.csv.gz'
codes_path = 'context_data/discipline_penalty_codes.csv'
base_path = 'fully-unified-data/complaints/complaints-{}_2000-2016_2016-11.csv.gz'
file_name = ['accused', 'investigators', 'victims']

'''
#play
df_sal = pd.read_csv(os.path.join(data_path, 'unified_data/salary/salary-filled_2002-2017_2017-09.csv.gz'))
df_sal.columns
df_sal.loc[0]

df_pr = pd.read_csv(os.path.join(data_path, 'unified_data/profiles/officer-profiles.csv.gz'))
df_pr.loc[0]

df_invest = pd.read_csv(os.path.join(data_path, 'unified_data/complaints/complaints-investigators_2000-2016_2016-11.csv.gz'))
df_invest.loc[0]

df_acc = pd.read_csv(os.path.join(data_path, 'unified_data/complaints/complaints-accused_2000-2016_2016-11.csv.gz'))
df_acc.loc[0]

df_acc.shape 
df_pr.shape

merge= df_invest.merge(df_pr, how = 'left', on = 'UID')
#looks name matches -at lest for [0]

merge2 = df_acc.merge(df_pr, how = 'left', on = 'UID')
'''

def pathmaker(base_path, file):
    return base_path.format(file)


def unzip(data_path, filename, save_to_path):
    zf = ZipFile(os.path.join(data_path, filename), 'r')
    zf.extractall(save_to_path)
    zf.close()
    #cite: https://stackoverflow.com/questions/3451111/unzipping-files-in-python


def read_df(data_path, filename):
    df = pd.read_csv(os.path.join(data_path, filename))
    return df


def parse_accused(accused_df):
    accused_df.drop(columns = 'row_id', inplace = True)
    final_dummies = pd.get_dummies(accused_df['final_finding'])
    #recommend_dummies = pd.get_dummies(accused_df['recommended_finding'])
    #cite https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.get_dummies.html
    accused_df['sustained'] = final_dummies['SU']
    #accused_df['recommend_sustain'] = recommend_dummies['SU']
    return accused_df


def parse_investigarots(investigators_df):
    investigators_df.drop(columns = 'row_id', inplace = True)
    investigators_df.rename(columns = {'first_name':'investigator_first_name', 'last_name':'investigator_last_name',
                                   'middle_initial':'investigator_middle_initial', 'suffix_name':'investigator_suffix',
                                   'appointed_date': 'date_investigator_appointed', 'current_star':'investigator_current_star_number',
                                   'current_rank': 'investigator_current_rank', 'current_unit':'investigator_current_unit'}, inplace = True)
    return investigators_df

def parse_victims(victims_df):
    victims_df.rename(columns = {'gender':'victim_gender', 'age':'victim_age', 'race':'victim_race'}, inplace = True)
    return victims_df


def merge_dfs(dfs):
    '''
    takes a list of dfs, the order is decided in the list dfs. If you change the order, the function
    may need to be tweeked. The suffixes, and merges 3 and 4
    The frist df is accused, the second is investigators, the third is victims, the third is codes
    '''
    merge_0 = dfs[0].merge(dfs[4], how = 'left', on = 'UID', suffixes = ('_accused', '_profile'))
    merge_1 = merge_0.merge(dfs[1], how = 'inner', on =  "cr_id", suffixes = ('_accused','_investigators'))
    merge_2 = merge_1.merge(dfs[2], how = 'inner', on =  "cr_id")
    merge_3 = merge_2.merge(dfs[3], how = 'left', left_on = 'recommended_discipline', right_on = 'CODE')

    merge_3.drop(columns = 'CODE', inplace = True)
    merge_3.rename(columns={'recommended_discipline': 'recommended_discipline_code',
                            'ACTION_TAKEN'          : 'recommended_discipline'      }, inplace = True)       
    
    merge_4 = merge_3.merge(dfs[3], how = 'left', left_on = 'final_discipline', right_on = 'CODE',suffixes = ('_recommended_discipline', '_final_discipline'))

    merge_4.drop(columns = 'CODE', inplace = True)

    merge_4.rename(columns={'final_discipline': 'final_discipline_code',
                            'ACTION_TAKEN'    : 'final_discipline'     }, inplace = True) 
    
    return merge_4


#proportion sustained: looking at all complaints filed, one entry per accused individual
def total_proportion(accused_df):
    return accused_df['sustained'].sum()/len(accused_df.index)

#proportion sustained of complaints that have a line in victims, investigarots and accused 
def outcome_by_race(df, outcome_word):
    grouped = df.groupby('victim_race').sum()
    grouped[outcome_word]
    grouped['proportion_'+outcome_word] = grouped[outcome_word]/len(df.index)
    df = grouped['proportion_'+outcome_word]

    #print('The proportion of complaints '+outcome_word+', by race of the victim:')
    #print(grouped['proportion_'+outcome_word])
    return df


def complaint_type_outcomes(accused_df, outcome, outcome_word):
    '''
    takes the acccused df, the two letter string for final finding: e.g. 'SU' and a string 
    for the final finding abbreviation meaning (e.g. 'sustained' for 'SU')
    output is a list of the complaint catagories for which the outcome (e.g. 'SU')
    is the most likely final finding
    '''
    crosstab = pd.crosstab(accused_df['final_finding'], accused_df['complaint_category'])
    #cite https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.crosstab.html

    #print('The following complaint catagories are most likely to be ' + outcome_word + ':')
    temp_list = []
    for column in crosstab.columns:
        if crosstab[column].idxmax() == outcome:
            print(column)
            temp_list.append(column)
    #cite: https://stackoverflow.com/questions/15741759/find-maximum-value-of-a-column-and-return-the-corresponding-row-values-using-pan
    df = pd.DataFrame(temp_list, columns = ['complaint catagories most likely to be ' + outcome_word]) 
    #cite: https://www.geeksforgeeks.org/create-a-pandas-dataframe-from-lists/
    return df

def export_df(df, path, filename):
    df.to_csv(os.path.join(path, filename))



def main():
    files = []
    for f in file_name:
        files.append(pathmaker(base_path, f))

    unzip(data_path, 'unified_data/unified_data.zip', path)

    dfs = []
    for filename in files:
        df = read_df(path, filename)
        if filename.__contains__('accused'):
            dfs.append(parse_accused(df))
        elif filename.__contains__('investigators'):
            dfs.append(parse_investigarots(df))
        elif filename.__contains__('victims'):
            dfs.append(parse_victims(df))
        else:
            print('unexpected file')
    dfs.append(read_df(data_path, codes_path))
    dfs.append(read_df(data_path, profile_path))

    df = merge_dfs(dfs)

    #proportion = total_proportion(dfs[0])
    #print('Total proportion of complaints that are sustained: {:.4f}'.format(proportion))
    #print(' ')

    #race_df = outcome_by_race(df, 'sustained')


    #outcome_df = complaint_type_outcomes(dfs[0], 'SU', 'sustained')

    export_df(df, path_2, 'full_df.csv')
    #export_df(race_df, path, 'Proportion of compliants sustained by race.csv')
    #export_df(outcome_df, path, 'Most likely to be sustained.csv')

    return df


df = main()

df['count'] = 1 

df2 = df.drop(columns = ['complaints-accused_2000-2016_2016-11_ID', 'cr_id',
       'complaint_category', 'recommended_discipline_code',
       'final_discipline_code', 'recommended_finding', 'final_finding',
       'UID_accused', 'old_UID_accused', 'link_UID_accused', 'sustained',
       'first_name', 'last_name', 'middle_initial', 'middle_initial2',
       'suffix_name', 'birth_year', 'gender', 'appointed_date',
       'resignation_date', 'current_status', 'current_star', 'current_unit',
       'current_rank', 'start_date', 'org_hire_date', 'profile_count',
       'cleaned_rank', 'link_UID_profile',
       'complaints-investigators_2000-2016_2016-11_ID',
       'investigator_first_name', 'investigator_last_name',
       'investigator_middle_initial', 'investigator_suffix',
       'date_investigator_appointed', 'investigator_current_star_number',
       'investigator_current_rank', 'investigator_current_unit',
       'UID_investigators', 'old_UID_investigators', 'link_UID',
       'victim_gender', 'victim_age', 'recommended_discipline',
       'NOTES_recommended_discipline', 'final_discipline',
       'NOTES_final_discipline'])

acc_race = df2.groupby(['race', 'victim_race']).sum()

acc_race.columns
acc_race.head()








