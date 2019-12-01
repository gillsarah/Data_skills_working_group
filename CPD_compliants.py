
from zipfile import ZipFile
import os 
import pandas as pd

#this is the path to the chicago-police-data GitHub, 
#used to access unified_data.zip and discipline_penalty_codes.csv
#data_path = '/Users/Sarah/Documents/GitHub/chicago-police-data/data'

#this is the save-to path, this is where the unified_data.zip unzips to
#and where we read the accused, investigators and victims data from (out of the unzipped contents)
#path =  '/Users/Sarah/Documents/GitHub/assignment-4-gillsarah'
path= '/Users/Sarah/Documents/GitHub/assignment-5-sarah-gill-1'

#profile_path = 'unified_data/profiles/officer-profiles.csv.gz' #path for reading from chicago-police-data
profile_path = 'fully-unified-data/profiles/officer-profiles.csv.gz'
codes_path = 'context_data/discipline_penalty_codes.csv'
base_path = 'fully-unified-data/complaints/complaints-{}_2000-2016_2016-11.csv.gz'
file_name = ['accused', 'investigators', 'victims']


def pathmaker(base_path, file):
    return base_path.format(file)


def unzip(path, filename, save_to_path):
    zf = ZipFile(os.path.join(path, filename), 'r')
    zf.extractall(save_to_path)
    zf.close()
    #cite: https://stackoverflow.com/questions/3451111/unzipping-files-in-python


def read_df(path, filename):
    df = pd.read_csv(os.path.join(path, filename))
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

def parse_profile(profile_df):
    profile_df['org_hire_date'] = pd.to_datetime(profile_df['org_hire_date'], format='%Y-%m-%d')
    #profile_df['birth_year'] = pd.to_datetime(profile_df['birth_year'], format='%Y')
    profile_df['Year_hired'] = profile_df['org_hire_date'].map(lambda d: d.year)
    return profile_df

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
    merge_4['count'] = 1 
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

    #unzip(path, 'unified_data/unified_data.zip', path)

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
    dfs.append(read_df(path, codes_path))
    
    df2 = read_df(path, profile_path)
    dfs.append(parse_profile(df2))

    df = merge_dfs(dfs)

    #proportion = total_proportion(dfs[0])
    #print('Total proportion of complaints that are sustained: {:.4f}'.format(proportion))
    #print(' ')

    #race_df = outcome_by_race(df, 'sustained')


    #outcome_df = complaint_type_outcomes(dfs[0], 'SU', 'sustained')

    export_df(df, path, 'full_df.csv')
    #export_df(race_df, path, 'Proportion of compliants sustained by race.csv')
    #export_df(outcome_df, path, 'Most likely to be sustained.csv')

    return df


df = main()

#df['count'] = 1 

def read_profile(path, profile_path):
    profile_df = read_df(path, profile_path)
    parse_profile(profile_df)
    profile_df['Year_hired'] = profile_df['org_hire_date'].map(lambda d: d.year)
    profile_df['count'] = 1
    return profile_df

profile_df = read_profile(path, profile_path)


def small_df_maker(df, col1, col2, col3 = 'count'):
    '''
    takes a df and two strings: 3 column names in that df, that you want to work with
    returns a dictionary ready to be used in to my_fn
    '''
    drop_list = []
    for colname in df.columns:
        if colname == col1:
            pass
        elif colname == col2:
            pass
        elif colname == col3:
            pass
        else:
            drop_list.append(colname)
    df2 = df.drop(columns = drop_list)
    df3 = dict(tuple(df2.groupby(col1)))
    #cite https://stackoverflow.com/questions/19790790/splitting-dataframe-into-multiple-dataframes

    return df3



def my_fn(df, officer_string, col1, col2, col3 = 'count'):
    '''
    takes a string value for officer, what you want to groubby
    e.g. 'WHITE' or 'MALE'
    this needs to line up with the values for col1 (e.g. 'race' or 'gender')
    takes a string value for the colum name 
    e.g. 'victim_race' or 'victim_gender'
    output is the equivolent of a mini-df of one variable worth of a groupby by two variables
    '''
    df2 = small_df_maker(df, col1, col2, col3 = 'count')
    g = df2[officer_string].groupby(col2).sum()
    g.reset_index(inplace=True)
    return g
    #breaks df2 into a small df for just 1 race? 
    #plots that subset in a historgram 


'''
my_fn(df, 'WHITE', 'race', 'final_finding')


profile_df = read_df(path, profile_path)
profile_df.columns
profile_df.head()

profile_df['resignation_date'].dtype
profile_df['org_hire_date'] = pd.to_datetime(profile_df['org_hire_date'], format='%Y-%m-%d')
profile_df['org_hire_date'].head(20)

parse_profile(profile_df)

df.groupby('complaint_category').sum()

year = df.groupby('org_hire_date').sum()

df['Year_hired'] = df['org_hire_date'].map(lambda d: d.year)
year = df.groupby('Year_hired').sum()
year.reset_index(inplace = True)


#profile_df['birth_year'] = pd.to_datetime(profile_df['birth_year'], format='%Y')

profile_df.loc[10]

my_fn(df, '03C-SEARCH OF PREMISE/VEHICLE WITHOUT WARRANT', 'complaint_category', 'victim_gender' ,  col3 = 'count')


dv_df = df[df['complaint_category'] == '05K-DOMESTIC ALTERCATION/INCIDENT - OFF DUTY']

dv_df.head()
dv_df.reset_index(inplace=True)
dv_df.loc[0]

'''


def filter_df(df, col1, col2= 'gender', value1 = 'all', value2= 'all'):
    if value1 == 'all':
        filtered_df = df
    else:
        filtered_df = df[df[col1] == value1]
    
    if value2 == 'all':
        filtered_df2 = filtered_df
    else:
        filtered_df2 = filtered_df[filtered_df[col2]== value2]
    return filtered_df2


#filter_df(df, 'race', 'gender','HISPANIC',  'MALE')
#filter_df(df, 'race', 'all')
#filter_df(df, 'final_finding', value1='SU')