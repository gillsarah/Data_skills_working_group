
#Rachel Steiner-Dillon and Sarah Gill

import os
import us
import pandas as pd
import requests
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter  #just need it if we want to fomat the y-axis
import itertools
import numpy as np

PATH = '/Users/Sarah/Documents/GitHub/assignment-2-sarah-gill'
#PATH = r'c:\users\rache\Documents\GitHub\assignment-2-sarah-gill'
os.chdir(os.path.expanduser(PATH)) #set working directory required for Mac



#choose 4 states to plot and the colors of their lines
STATE_LIST = [('k','Illinois'), ('r','California'), 
              ('b', 'New York'), ('darkgreen','Texas')]


months = [1, 8]
states = range(1, 49)
base_url = 'https://www.ncdc.noaa.gov/cag/statewide/time-series/{}-tavg-1-{}-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000'
energy_url = 'https://www.eia.gov/electricity/data/state/annual_consumption_state.xls'


def build_url(st, mo, base):
    return base.format(st, mo)


def create_folder(path):
        if not os.path.exists(path):
            os.makedirs(path)
        #code source: https://gist.github.com/keithweaver/562d3caa8650eefe7f84fa074e9ca949



'''
urls = [build_url(st, mo, base_url) for st, mo in itertools.product(states, months)]
urls.append(energy_url)


weather_data = os.listdir(os.path.join(PATH, 'weather'))
'''

def get_data(list, path, folder):
    if len(folder) >= len(list)-1:
        print('files have been downloaded')
        #Cite: https://stackoverflow.com/questions/49284015/how-to-check-if-folder-is-empty-with-python
        
    else:
        print('some files are missing: downloading data now')
        for url in list:
    
            if url.endswith('.xls'):
                energy_response = requests.get(energy_url)
        
                with open(os.path.join(path, 'energy.xls'), 'wb') as output:
                    output.write(energy_response.content)
                    #code source: https://stackoverflow.com/questions/25415405/downloading-an-excel-file-from-the-web-in-python
    
            else:   
                weather_response = requests.get(url)

                state, measure, month = weather_response.text.split('\n')[0].split(', ')
   
                with open(os.path.join(path, 'weather', state+'_'+month+'.csv'), 'w') as ofile:
                    ofile.write(weather_response.text)


def load_and_read_weather(listdir, path):
    #print('in the fn') #debug
    #print(listdir) #debug
    dfs = []
    for fname in listdir:
        #print('in the for loop') #debug
        if fname.endswith('.csv'):
            #print('I am in') #debug
            st, month = fname.split('_')
            df = pd.read_csv(os.path.join(path, 'weather', fname), skiprows=4)
            df['State'] = st
            df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')
            dfs.append(df)
        else:
            print('unexpected filetype in folder')

    df = pd.concat(dfs)
    df = df.sort_values(['State', 'Date'])
    df['Year'] = df['Date'].map(lambda d: d.year)
    df['Month'] = df['Date'].map(lambda d: d.month)
    
    return df
'''
def load_weather(listdir, path):
    dfs = []
    print('I am in load_weather') #debug
    for fname in listdir:
        if fname.endswith('.csv'):
            st, month = fname.split('_')
            df = pd.read_csv(os.path.join(path, 'weather', fname), skiprows=4)
            df['State'] = st
            df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')
            dfs.append(df)
    return dfs

#dfs = load_weather(weather_data, PATH)

def parse_weather(dfs):
    print('I am in parse_weather')
    #dfs = load_weather(listdir, path)
    df = pd.concat(dfs)
    df = df.sort_values(['State', 'Date'])
    df['Year'] = df['Date'].map(lambda d: d.year)
    df['Month'] = df['Date'].map(lambda d: d.month)
    
    return df
#df = parse_weather(weather_data, PATH)
'''
def load_energy(path, filename):
    df = pd.read_excel(os.path.join(path, filename), skiprows=1)
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
    df['Consumption'] = [v/1000000 for v in df['Consumption']] #unit conversion. consumption now in millions
    df = df.drop(['YEAR', 'St_Abbr', 'TYPE OF PRODUCER', 'ENERGY SOURCE              (UNITS)'], axis=1)
    
    df = pd.DataFrame(df.groupby(['State', 'Year'])['Consumption'].sum()).reset_index()
    #code reference: https://stackoverflow.com/questions/40553002/pandas-group-by-two-columns-to-get-sum-of-another-column
    #code reference: https://stackoverflow.com/questions/10373660/converting-a-pandas-groupby-output-from-series-to-dataframe

    return df



def plot_multi_state(df, states, path):
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
    plt.savefig(os.path.join(path, 'Jan_Aug_Temp_Delta.png'))
    plt.show()


def month_df(df, month_number):
    df1 = df[df['Month'] == month_number]
    return df1


def month_temp_plot(df, month_num, month_name, state_list):
    fig, ax = plt.subplots(1, 1)
    for color, label in state_list:
        df_month = month_df(df, month_num)
        state = df_month[df_month['State'] == label]
        ax.plot(state['Year'], state['Value'], color, label = label)
    ax.legend(loc='upper right')
    plt.suptitle('Average '+ month_name + ' Temperature')
    plt.savefig(os.path.join(PATH, 'Aug_Temp.png'))
    plt.show()


#create the base for the energy_weather_state_plot: generate two y-axise, set plot type and create ledgane
#output is the basis for a single plot
def two_scales(ax1, axis, data1, data2, c1, c2, state_string, month):
    ax2 = ax1.twinx()
    ax1.bar(axis, data1, color=c1, label = 'Annual Energy Use')
    ax1.set_ylabel('Energy Use in millions')
    ax1.plot(np.NaN, color = c2, label='Average '+month+' Temp') #plot an empty line so that we can have a legend
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    #cite: https://stackoverflow.com/questions/29188757/matplotlib-specify-format-of-floats-for-tick-lables 
    ax2.plot(axis, data2, color=c2, label = 'Average '+month+' Temp')
    ax2.set_ylabel('Degrees Fahrenheit', rotation=270,labelpad=15)
    #rotates the second axis lable 180 degrees from start (it is at 90 degrees by default)
    #cite: https://stackoverflow.com/questions/27671748/how-to-print-y-axis-label-horizontally-in-a-matplotlib-pylab-chart 
    ax1.legend(loc='upper right', bbox_to_anchor=(1.11,1.25), fontsize = 'small')
    #cite: bbox_to_anchor https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot 
    #cite: fontsize https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.axes.Axes.legend.html
    plt.title(state_string)
    return ax1, ax2

#takes two_scales output and creates a multi-plot (2x2). 
def weather_energy_state_plot(jan_merged_df, STATE_LIST, month_string):
    fig, ax_2x2 = plt.subplots(2,2,figsize=(12,6))
    ax = [l for l2 in ax_2x2 for l in l2] #flaten
    energy_colors = ['tab:blue','gold', 'c', 'cornflowerblue']
    #cite https://matplotlib.org/3.1.0/gallery/color/named_colors.html
    for index, (color, label) in enumerate(STATE_LIST):
        ax[index] = two_scales(ax[index], jan_merged_df[jan_merged_df['State'] == label]['Year'],
                jan_merged_df[jan_merged_df['State'] == label]['Consumption'],
                jan_merged_df[jan_merged_df['State'] == label]['Value'],
                energy_colors[index], color,label, month_string)
    plt.tight_layout()
    plt.savefig(os.path.join(PATH, month_string+ '_Energy_temp_plot.png'))
    plt.show()  

#cite for two_scales and weather_energy_state_plot:
# https://stackoverflow.com/questions/44825950/matplotlib-create-two-subplots-in-line-with-two-y-axes-each 



def summary_stats(df, STATE_LIST, month_num, colum_name, quiry):
    for color, label in STATE_LIST:
        df_month = month_df(df, month_num)
        state = df_month[df_month['State'] == label]
        print('Max/Mean/Min '+ quiry + ' for ' +label+':', state[colum_name].max(), state[colum_name].mean(), state[colum_name].min())



def main():
    create_folder(os.path.join(PATH, 'weather'))
    weather_data_check = os.listdir(os.path.join(PATH, 'weather'))  #listdirectory to for use to see if folder has the data 
    urls = [build_url(st, mo, base_url) for st, mo in itertools.product(states, months)]
    urls.append(energy_url)
    
    get_data(urls, PATH, weather_data_check) 

    weather_data = os.listdir(os.path.join(PATH, 'weather'))  #listdirectory
    #dfs = load_weather(weather_data, PATH)
    #print(dfs[0]) #debug
    weather_df = load_and_read_weather(weather_data, PATH)
    #weather_df = parse_weather(dfs)
    energy_df = load_energy(PATH, 'energy.xls')
    
    df_jan = month_df(weather_df, 1)
    df_aug = month_df(weather_df, 8)
  
    #inner gets rid of years that do not exist in both datasets (so years before 1990 and after 2019)
    jan_merged_df = df_jan.merge(energy_df, on=['State','Year'], how = 'inner') 
    aug_merged_df = df_aug.merge(energy_df, on=['State','Year'], how = 'inner') 
    #cite https://stackoverflow.com/questions/41815079/pandas-merge-join-two-data-frames-on-multiple-columns

    plot_multi_state(weather_df, STATE_LIST, PATH)
    month_temp_plot(weather_df, 8, 'August', STATE_LIST)

    weather_energy_state_plot(jan_merged_df, STATE_LIST, 'January')
    weather_energy_state_plot(aug_merged_df, STATE_LIST, 'August')
    
    summary_stats(weather_df, STATE_LIST, 8, 'Value', 'August Temperature')
    summary_stats(aug_merged_df, STATE_LIST, 8, 'Consumption', 'Energy Use')
  
    
main()
'''

def get_data_main():
    create_folder(os.path.join(PATH, 'weather')) 
    weather_data = os.listdir(os.path.join(PATH, 'weather'))
    urls = [build_url(st, mo, base_url) for st, mo in itertools.product(states, months)]
    urls.append(energy_url)

    get_data(urls, PATH, weather_data)



def use_data_main():
    #dfs = load_weather(weather_data, PATH)
    #print(dfs[0]) #debug
    weather_data = os.listdir(os.path.join(PATH, 'weather'))
    weather_df = load_and_read_weather(weather_data, PATH)
    #weather_df = parse_weather(dfs)
    energy_df = load_energy(PATH, 'energy.xls')
    
    df_jan = month_df(weather_df, 1)
    df_aug = month_df(weather_df, 8)
  
    #inner gets rid of years that do not exist in both datasets (so years before 1990 and after 2019)
    jan_merged_df = df_jan.merge(energy_df, on=['State','Year'], how = 'inner') 
    aug_merged_df = df_aug.merge(energy_df, on=['State','Year'], how = 'inner') 
    #cite https://stackoverflow.com/questions/41815079/pandas-merge-join-two-data-frames-on-multiple-columns

    plot_multi_state(weather_df, STATE_LIST, PATH)
    month_temp_plot(weather_df, 8, 'August', STATE_LIST)

    weather_energy_state_plot(jan_merged_df, STATE_LIST, 'January')
    weather_energy_state_plot(aug_merged_df, STATE_LIST, 'August')
    
    summary_stats(weather_df, STATE_LIST, 8, 'Value', 'August Temperature')
    summary_stats(aug_merged_df, STATE_LIST, 8, 'Consumption', 'Energy Use')


get_data_main()
use_data_main()
'''
