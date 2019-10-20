import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

#chose where to save the data (PATH) and the plots (save_plots_path)
PATH = '/Users/Sarah/Documents/GitHub/assignment-2-sarah-gill'
#PATH = '/Users/Sarah/Documents/GitHub/assignment-2-sarah-gill/weather'
save_plots_path = '/Users/Sarah/Documents/GitHub/assignment-2-sarah-gill'
os.chdir(os.path.expanduser(PATH)) #set working directory -Needed for Mac
#Talk to 

#chose 4 states to plot
STATE_LIST = [('k-','Illinois'), ('r-','California'), 
              ('b-', 'New York'), ('g-','Texas')]

def build_urls():
    urls = []
    temp_list = list(range(1,49))
    for state_number in temp_list:
        state_number = str(state_number)
        urls.append('https://www.ncdc.noaa.gov/cag/statewide/time-series/'+state_number+'-tavg-1-1-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000')
        urls.append('https://www.ncdc.noaa.gov/cag/statewide/time-series/'+state_number+'-tavg-1-8-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000' )
    return urls

#url = 'https://www.ncdc.noaa.gov/cag/statewide/time-series/1-tavg-1-1-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000'

def download_data(url):
    response = requests.get(url)

    state, measure, month = response.text.split('\n')[0].split(', ')

    with open(os.path.join(PATH, 'weather', state+'_'+month+'.csv'), 'w') as ofile:
        ofile.write(response.text)
#can't get it to work unless I have the working directory point to the already created folder!

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
def state_month_df(df, month_number, state_string):
    df['Month'] = df['Date'].map(lambda d: d.month)
    df_aug = df[df['Month'] == month_number]
    state = df_aug[df_aug['State'] == state_string]
    return state

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
    urls = build_urls()
    #download toggle 
    if len(os.listdir(PATH)) >=len(urls):
        pass
        #print('got it')
    else:
        print('some files are missing: downloading weather data now')
        for url in urls:
            download_data(url)
    #Cite: https://stackoverflow.com/questions/49284015/how-to-check-if-folder-is-empty-with-python
    
    df_contents = []
    for filepath in os.listdir(PATH):
        data = read_df(filepath)
        df_contents.append(data)
    
    df = pd.concat(df_contents)
    df = df.sort_values(['State', 'Date']) 
    df['Year'] = df['Date'].map(lambda d: d.year) #add a col for year, we need this for plot 1 and 2

    jan_aug_diff_plot(df, STATE_LIST)
    aug_temp_plot(df, STATE_LIST)
    summary_stats(df, STATE_LIST) 


#call
main()

