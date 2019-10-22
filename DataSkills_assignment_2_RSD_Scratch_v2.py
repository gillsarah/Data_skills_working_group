import os
import us
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import itertools
import datetime as dt


PATH = r'c:\users\rache\Documents\GitHub\assignment-2-rachel-steiner-dillon'

# Mac Paths:
#PATH = '/Users/Sarah/Documents/GitHub/assignment-2-sarah-gill'
#PATH = '/Users/Sarah/Documents/GitHub/assignment-2-sarah-gill/weather'
#save_plots_path = '/Users/Sarah/Documents/GitHub/assignment-2-sarah-gill'
#os.chdir(os.path.expanduser(PATH)) #set working directory -Needed for Mac

State_List = [('k','Illinois'), ('r','California'), 
              ('b', 'New York'), ('darkgreen','Texas')]

months = [1, 8]
states = range(1, 49)
base_url = 'https://www.ncdc.noaa.gov/cag/statewide/time-series/{}-tavg-1-{}-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000'
energy_url = 'https://www.eia.gov/electricity/data/state/annual_consumption_state.xls'


def build_url(st, mo, base):
    return base.format(st, mo)


urls = [build_url(st, mo, base_url) for st, mo in itertools.product(states, months)]
urls.append(energy_url)


weather_data = os.listdir(os.path.join(PATH, 'weather'))


def get_data(list):
    if len([f for f in weather_data]) == len(urls)-1:
        print('files have been downloaded')
    
    else:
        print('some files are missing: downloading data now')
        for url in list:
    
            if url.endswith('.xls'):
                energy_response = requests.get(energy_url)
        
                with open(os.path.join(PATH, 'energy.xls'), 'wb') as output:
                    output.write(energy_response.content)
                    #code source: https://stackoverflow.com/questions/25415405/downloading-an-excel-file-from-the-web-in-python
    
            else:   
                weather_response = requests.get(url)

                state, measure, month = weather_response.text.split('\n')[0].split(', ')
   
                with open(os.path.join(PATH, 'weather', state+'_'+month+'.csv'), 'w') as ofile:
                    ofile.write(weather_response.text)


#call
get_data(urls)


'''
Jeff's solution:
    
assert(all([fname.endswith('.csv') for fname in weather_data])), 'Non-csv file type found in "weather" folder'

def load_weather(path):
    dfs = []
    for f in path:
        st, month = f.split('_')
        df = pd.read_csv(os.path.join(PATH, 'weather', f), skiprows=4)
        df['State'] = st
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')
        dfs.append(df)

    df = pd.concat(dfs)
    df = df.sort_values(['State', 'Date'])
    df['Year'] = df['Date'].map(lambda d: d.year)
    df['Month'] = df['Date'].map(lambda d: d.month)
    
    return df

weather_df = load_weather(weather_data)
'''



def load_and_read_weather(path):
    dfs = []
    for fname in path:
        if fname.endswith('.csv'):
            st, month = fname.split('_')
            df = pd.read_csv(os.path.join(PATH, 'weather', fname), skiprows=4)
            df['State'] = st
            df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')
            dfs.append(df)

        df = pd.concat(dfs)
        df = df.sort_values(['State', 'Date'])
        df['Year'] = df['Date'].map(lambda d: d.year)
        df['Month'] = df['Date'].map(lambda d: d.month)
    
    return df


#call
weather_df = load_and_read_weather(weather_data)


'''
I cannot get this code to run. Would prefer not to break up the function. 

def read_df(listdir):
    for fname in listdir:
        if fname.endswith('.csv'):
            st, month = fname.split('_')
            df = pd.read_csv(os.path.join(PATH, 'weather', fname), skiprows = 4)
            df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')
            df['State'] = st
            return df
    
        else:
            print('unexpected file type in folder')

#call
read_df(weather_data)


def read_weather(listdir):
    df_contents = []
    for file in listdir:
        data = read_df(file)
        df_contents.append(data)
    
    df = pd.concat(df_contents)
    df = df.sort_values(['State', 'Date']) 
    df['Year'] = df['Date'].map(lambda d: d.year) #add a col for year, we need this for plot 1 and 2

    return df


weather_df = read_weather(weather_data)
'''





def load_energy(PATH, filename):
    df = pd.read_excel(os.path.join(PATH, filename), skiprows=1)
    df = pd.DataFrame(df)

    df = df.rename(index=str, columns={'STATE':'St_Abbr',
                                       'CONSUMPTION for ELECTRICITY':'Consumption'})
    
    df['Year'] = pd.to_datetime(df['YEAR'], format='%Y').map(lambda d: d.year)
    
    xwalk = us.states.mapping('abbr', 'name')
    df['State'] = df['St_Abbr'].map(xwalk)
    #code reference: https://stackoverflow.com/questions/40814187/map-us-state-name-to-two-letter-acronyms-that-was-given-in-dictionary-separately
    
    df = df.drop(df[df['TYPE OF PRODUCER'] != 'Total Electric Power Industry'].index)
    df = df.drop(df[df['Consumption'] == "."].index)
    df = df.dropna(axis=0)
    df = df.drop(['YEAR', 'St_Abbr', 'TYPE OF PRODUCER', 'ENERGY SOURCE              (UNITS)'], axis=1)
    
    df = pd.DataFrame(df.groupby(['State', 'Year'])['Consumption'].sum()).reset_index()
    #code reference: https://stackoverflow.com/questions/40553002/pandas-group-by-two-columns-to-get-sum-of-another-column
    #code reference: https://stackoverflow.com/questions/10373660/converting-a-pandas-groupby-output-from-series-to-dataframe

    return df



#call
energy_df = load_energy(PATH, 'energy.xls')


#this doesn't work, and I can't figure out why. The second dataframe is always blank. 
def separate_months(df):
    month_dfs = []
    for m in months:
        df = df[df['Month'] == m]
        month_dfs.append(df)
    
    return month_dfs
 
       
month_dfs = separate_months(weather_df)    
month_dfs


'''
This does work, but only if I call them individually. 

def month_df(df, m):
    df = df[df['Month'] == m]
    return df

month_df(weather_df, 1)
month_df(weather_df, 8)
'''


merged_month_dfs = []
for df in month_dfs:
    merged = energy_df.merge(df, on=['State', 'Year'], how='inner')
    merged_month_dfs.append(merged)    





#weather_df.to_csv(r'c:\users\rache\Desktop\weather_test.csv', index=False)
#energy_df.to_csv(r'c:\users\rache\Desktop\energy_test.csv', index=False)


def plot_multi_state(df, states):
    df['Jan-Aug Delta'] = df.groupby(['State', 'Year'])['Value'].diff()
    df_delta = df.dropna(subset=['Jan-Aug Delta'])[['State', 'Year', 'Jan-Aug Delta']]

    fig, ax = plt.subplots(len(states), 1)
    
    for i, (color, label) in enumerate(states):
        d = df_delta[df_delta['State'] == label]
        ax[i].plot(d['Year'], d['Jan-Aug Delta'], color)
        ax[i].set_ylabel(label)

        if i == 0:
            ax[i].xaxis.tick_top()
        elif i == len(states)-1:
            pass
        else:
            ax[i].set_label('')
            ax[i].set_xticks([])
            ax[i].xaxis.set_ticks_position('none')

    plt.suptitle('Average Jan-Aug Temperature Variation')
    plt.savefig(os.path.join(PATH, 'Jan_Aug_Temp_Delta.png'))
    plt.show()

#call
plot_multi_state(weather_df, State_List)



def avg_aug(df, states):
    df['Month'] = df['Date'].map(lambda d: d.month)
    df_aug = df[df['Month'] == 8]

    fig, ax = plt.subplots(1, 1)

    for i, (c, l) in enumerate(states):
        d = df_aug[df_aug['State'] == l]
        ax.plot(d['Year'], d['Value'], color=c, label=l)

    ax.legend(loc='upper right')
    plt.suptitle('Average August Temperature')
    plt.savefig(os.path.join(PATH, 'weather', 'Aug_Temp.png'))
    plt.show()


avg_aug(weather_df, State_List)








