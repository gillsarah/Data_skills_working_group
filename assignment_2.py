import os
import us 
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import itertools #new package downloaded

#chose where to save the data (PATH) and the plots (save_plots_path)
#PATH = '/Users/Sarah/Documents/GitHub/assignment-2-sarah-gill'
PATH = '/Users/Sarah/Documents/GitHub/assignment-2-sarah-gill/weather'
save_plots_path = '/Users/Sarah/Documents/GitHub/assignment-2-sarah-gill'
os.chdir(os.path.expanduser(PATH)) #set working directory -Needed for Mac
#Talk to 

#chose 4 states to plot
STATE_LIST = [('k-','Illinois'), ('r-','California'), 
              ('b-', 'New York'), ('g-','Texas')]


months = (1, 8)
states = range(1, 49)
base_url = 'https://www.ncdc.noaa.gov/cag/statewide/time-series/{}-tavg-1-{}-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000'
energy_url = 'https://www.eia.gov/electricity/data/state/annual_consumption_state.xls'
'''
def build_urls():
    urls = []
    temp_list = list(range(1,49))
    for state_number in temp_list:
        state_number = str(state_number)
        urls.append('https://www.ncdc.noaa.gov/cag/statewide/time-series/'+state_number+'-tavg-1-1-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000')
        urls.append('https://www.ncdc.noaa.gov/cag/statewide/time-series/'+state_number+'-tavg-1-8-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000' )
    return urls
'''

#call
#urls = build_urls() 
#url = 'https://www.ncdc.noaa.gov/cag/statewide/time-series/1-tavg-1-1-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000'
def build_url(st, mo, base):
    return base.format(st, mo)

urls = [build_url(st, mo, base_url) for st, mo in itertools.product(states, months)]
urls.append(energy_url)

def download_data(url):
    response = requests.get(url)
    if url.endswith('.xls'):
        with open(os.path.join(PATH, 'energy'), 'wb') as ofile:
            ofile.write(response.text)

    else:
        state, measure, month = response.text.split('\n')[0].split(', ')

    with open(os.path.join(PATH, state+'_'+month+'.csv'), 'w') as ofile:
        ofile.write(response.text)
download_data(energy_url)

def download_data(url, filename):
    response = requests.get(url)
    if filename.endswith('.xls'):
        open_as = 'wb'
        output = response.content

download_data(energy_url, 'energy.xls')

#download toggle  -not working anymore
if len(os.listdir(PATH)) >=len(urls):
    pass
    #print('got it')
else:
    print('some files are missing: downloading weather data now')
    for url in urls:
        download_data(url)
    #Cite: https://stackoverflow.com/questions/49284015/how-to-check-if-folder-is-empty-with-python
download_data(energy_url)

'''
#can't get it to work unless I have the working directory point to the already created folder!
def download_data(url, filename):
    response = requests.get(url)
    if filename.endswith('.csv'):
        open_as = 'w'
        output = response.text
        #return open_as
    elif filename.endswith('.xls'):
        open_as = 'wb'
        output = response.content
        #return open_as
    else:
        return 'unexpected file type in download_data'
'''

weather_data = os.listdir(os.path.join(PATH))   

#currenlty only accomodates csv form data
def read_df(path):
    if path.endswith('.csv'):
        st, month = path.split('_')
        df = pd.read_csv(os.path.join(path), skiprows = 4)
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')
        df['State'] = st
        return df
    else:
        print('unexpected file type in folder')

#call
read_df(PATH)

def read_weather(path):
    df_contents = []
    for filepath in os.listdir(path):
        data = read_df(filepath)
        df_contents.append(data)
    
    df = pd.concat(df_contents)
    df = df.sort_values(['State', 'Date']) 
    df['Year'] = df['Date'].map(lambda d: d.year) #add a col for year, we need this for plot 1 and 2

    return df

df = read_weather(PATH)

def load_energy(path, filename):
    df = pd.read_excel(os.path.join(path, filename), skiprows = 1, na_values = '.')
    #cite https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html 
    df = pd.DataFrame(df)

    df = df.rename(index=str, columns={'STATE':'St_Abbr',
                                       'CONSUMPTION for ELECTRICITY':'Consumption'})
    
    df['Year'] = pd.to_datetime(df['YEAR'], format='%Y').map(lambda d: d.year)
    
    xwalk = us.states.mapping('abbr', 'name')
    df['State'] = df['St_Abbr'].map(xwalk)
    #code reference: https://stackoverflow.com/questions/40814187/map-us-state-name-to-two-letter-acronyms-that-was-given-in-dictionary-separately
    
    df = df.drop(df[df['TYPE OF PRODUCER'] != 'Total Electric Power Industry'].index)
    #df = df.drop(df[df['Consumption'] == "."].index)
    df = df.dropna(axis=0)
    df = df.drop(['YEAR', 'St_Abbr', 'TYPE OF PRODUCER', 'ENERGY SOURCE              (UNITS)'], axis=1)
    
    df = pd.DataFrame(df.groupby(['State', 'Year'])['Consumption'].sum()).reset_index()
    #code reference: https://stackoverflow.com/questions/40553002/pandas-group-by-two-columns-to-get-sum-of-another-column
    #code reference: https://stackoverflow.com/questions/10373660/converting-a-pandas-groupby-output-from-series-to-dataframe

    return df

energy_df = load_energy(PATH, 'Energy_use.xls')

'''
def df_maker():
    df_contents = []
    for filepath in os.listdir(PATH):
        data = read_df(filepath)
        df_contents.append(data)
    
    df = pd.concat(df_contents)
    df = df.sort_values(['State', 'Date']) 
    df['Year'] = df['Date'].map(lambda d: d.year) #add a col for year, we need this for plot 1 and 2
    return df
'''
'''
def load_data():
    dfs = []
    for f in weather_data:
        st, month = f.split('_')
        df = pd.read_csv(os.path.join(PATH, 'weather', f), skiprows=4)
        df['State'] = st
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')
        dfs.append(df)

    df = pd.concat(dfs)
    df = df.sort_values(['State', 'Date'])
    return df
'''

#output is a df of the temperature difference between jan and aug for one state 
def jan_aug_diff(df, state_string):
    #df['Year'] = df['Date'].map(lambda d: d.year)
    df['Jan-Aug Delta'] = df.groupby(['State', 'Year'])['Value'].diff()
    df_delta = df.dropna(subset=['Jan-Aug Delta'])[['State', 'Year', 'Jan-Aug Delta']]
    state = df_delta[df_delta['State'] == state_string]
    return state

def jan_aug_diff_plot(df,STATE_LIST):
    fig, ax = plt.subplots(4, 1)
    for index, (color, label) in enumerate(STATE_LIST):
        #print(index,color, label)
        state = jan_aug_diff(df, label)
        ax[index].plot(state['Year'], state['Jan-Aug Delta'], color)
        ax[index].set_ylabel(label) 
    ax[0].xaxis.tick_top()
    ax[1].set_label('')
    ax[1].set_xticks([])
    ax[1].xaxis.set_ticks_position('none')
    ax[2].set_label('') #ledgend lable
    ax[2].set_xticks([]) #removes the label of x-axis
    ax[2].xaxis.set_ticks_position('none') #removes the ticks on x-axis
    plt.suptitle('Average Jan-Aug Temperature Variation')
    plt.savefig(save_plots_path+'/Jan-Aug_Variation.png')
    plt.show()  
    #cite: https://stackoverflow.com/questions/14880192/iterate-a-list-of-tuples

#output is a df of one state for one month (e.g. IL for Aug of each year)
#not useing this
def state_month_df(df, month_number, state_string):
    df['Month'] = df['Date'].map(lambda d: d.month)
    df_month = df[df['Month'] == month_number]
    state = df_month[df_month['State'] == state_string]
    return state

#useing this
def month_df(df, month_number):
    df['Month'] = df['Date'].map(lambda d: d.month)
    df_month = df[df['Month'] == month_number]
    #state = df_month[df_month['State'] == state_string]
    return df_month

df_jan = month_df(df, 1)
df_aug = month_df(df, 8)



def aug_temp_plot(df, STATE_LIST):
    fig, ax = plt.subplots(1, 1)
    for color, label in STATE_LIST:
        state = state_month_df(df, 8, label)
        ax.plot(state['Year'], state['Value'], color, label = label)
    ax.legend(loc='upper right')
    plt.suptitle('Average August Temperature')
    plt.savefig(save_plots_path+'/Aug_Temp.png')
    plt.show()

def summary_stats(df, STATE_LIST):
    for color, label in STATE_LIST:
        state = state_month_df(df, 8, label)
        print('Max/Mean/Min for '+label+':', state['Value'].max(), state['Value'].mean(), state['Value'].min())

def main():
    

    

    jan_aug_diff_plot(df, STATE_LIST)
    aug_temp_plot(df, STATE_LIST)
    summary_stats(df, STATE_LIST) 


#call
main()

