import os
import us
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import itertools
import datetime as dt

do_downloads = False


PATH = r'c:\users\rache\Documents\GitHub\assignment-2-rachel-steiner-dillon'


months = (1, 8)
states = range(1, 49)
base_url = 'https://www.ncdc.noaa.gov/cag/statewide/time-series/{}-tavg-1-{}-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000'
energy_url = 'https://www.eia.gov/electricity/data/state/annual_consumption_state.xls'


def build_url(st, mo, base):
    return base.format(st, mo)


urls = [build_url(st, mo, base_url) for st, mo in itertools.product(states, months)]
urls.append(energy_url)


def get_page(url):
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
    
    

if do_downloads:
    for url in urls:
        get_page(url)
    


weather_data = os.listdir(os.path.join(PATH, 'weather'))


#see Sarah's read weather function
def load_weather():
    dfs = []
    for f in weather_data:
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


weather_df = load_weather()
energy_df = load_energy(PATH, 'energy.xls')


def month_df(df, month_number):
    df = df[df['Month'] == month_number]
    return df

jan_df = month_df(weather_df, 1)
aug_df = month_df(weather_df, 8)  

jan_merged = energy_df.merge(jan_df, on=['State', 'Year'], how='inner') 
aug_merged = energy_df.merge(aug_df, on=['State', 'Year'], how='inner')

for m in months:
    month+'_df' = month_df(modern_weather, month)
    



#weather_df.to_csv(r'c:\users\rache\Desktop\weather_test.csv', index=False)
#energy_df.to_csv(r'c:\users\rache\Desktop\energy_test.csv', index=False)


def plot_weather_energy(df, states):
    fig, ax = plt.subplots(len(states), 1)
    
    colors = ['k-', 'r-', 'b-', 'g-']

    for i, st in enumerate(states):
        ax2[i]=ax[i].twinx()
        
        d = df[df['State'] == st]
        ax[i].plot(d['Year'], d['Consumption'], colors[i])
        ax2[i].plot(d['Year'], d['Value'], colors[i])
        ax[i].set_ylabel(st)

        if i == 0:
            ax[i].xaxis.tick_top()
        elif i == len(states)-1:
            pass
        else:
            ax[i].set_label('')
            ax[i].set_xticks([])
            ax[i].xaxis.set_ticks_position('none')

    plt.suptitle('Annual Energy Consumption by State')
    #plt.savefig(os.path.join(PATH, 'jan_consumption.png'))
    plt.show()

states = ['California', 'Illinois', 'New York', 'Texas']
plot_weather_energy(jan_merged, states)












def plot_multi_state(df, states):
    df['Jan-Aug Delta'] = df.groupby(['State', 'Year'])['Value'].diff()
    df_delta = df.dropna(subset=['Jan-Aug Delta'])[['State', 'Year', 'Jan-Aug Delta']]

    fig, ax = plt.subplots(len(states), 1)
    
    colors = ['k-', 'r-', 'b-', 'g-']

    for i, st in enumerate(states):
        d = df_delta[df_delta['State'] == st]
        ax[i].plot(d['Year'], d['Jan-Aug Delta'], colors[i])
        ax[i].set_ylabel(st)

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

states = ['California', 'Illinois', 'New York', 'Texas']
plot_multi_state(weather_df, states)







def plot_on_one(df, states):
    df['Month'] = df['Date'].map(lambda d: d.month)
    df_aug = df[df['Month'] == 8]

    fig, ax = plt.subplots(1, 1)

    colors = ['k-', 'r-', 'b-', 'g-']

    for st in states:
        d = df_aug[df_aug['State'] == st]
        ax.plot(d['Year'], d['Value'], colors[i], label=st)

    ax.legend(loc='upper right')
    plt.suptitle('Average August Temperature')
    plt.savefig(os.path.join(PATH, 'weather', 'Aug_Temp.png'))
    plt.show()

states = ['Georgia', 'Maine']
plot_on_one(weather_df, states)
