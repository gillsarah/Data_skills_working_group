import os
import us 
import pandas as pd
import requests
#from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter  #just need it if we want to fomat the y-axis
import itertools 
import numpy as np 

#chose where to save the data (PATH) and the plots (PATH)
PATH = '/Users/Sarah/Documents/GitHub/assignment-2-sarah-gill'
#PATH = '/Users/Sarah/Documents/GitHub/assignment-2-sarah-gill/weather'
#PATH = '/Users/Sarah/Documents/GitHub/assignment-2-sarah-gill'
os.chdir(os.path.expanduser(PATH)) #set working directory -Needed for Mac

#chose 4 states to plot and the colors for their lines.
STATE_LIST = [('k','Illinois'), ('r','California'), 
              ('b', 'New York'), ('darkgreen','Texas')]

months = [1, 8]
states = range(1, 49)
base_url = 'https://www.ncdc.noaa.gov/cag/statewide/time-series/{}-tavg-1-{}-1895-2019.csv?base_prd=true&begbaseyear=1901&endbaseyear=2000'
energy_url = 'https://www.eia.gov/electricity/data/state/annual_consumption_state.xls'


def build_url(st, mo, base):
    return base.format(st, mo)


#urls = [build_url(st, mo, base_url) for st, mo in itertools.product(states, months)]
#urls.append(energy_url)

#weather_data = os.listdir(os.path.join(PATH, 'weather')) #PC
#weather_data = os.listdir(os.path.join(PATH)) #mac


def get_data(url,PATH): #check toggle
    #if len([f for f in weather_data]) == len(urls)-1:
        #print('files have been downloaded')
    if len(weather_data) >=len(urls): #Sarah
        print('files have been downloaded')
    #Cite: https://stackoverflow.com/questions/49284015/how-to-check-if-folder-is-empty-with-python
    else:
        print('some files are missing: downloading data now')
        for url in urls:
    
            if url.endswith('.xls'):
                energy_response = requests.get(energy_url)
        
                with open(os.path.join(PATH, 'energy.xls'), 'wb') as output:
                    output.write(energy_response.content)
                    #code source: https://stackoverflow.com/questions/25415405/downloading-an-excel-file-from-the-web-in-python
    
            else:   
                weather_response = requests.get(url)

                state, measure, month = weather_response.text.split('\n')[0].split(', ')
   
                with open(os.path.join(PATH, 'weather', state+'_'+month+'.csv'), 'w') as ofile:
                #with open(os.path.join(PATH, state+'_'+month+'.csv'), 'w') as ofile: #mac
                    ofile.write(weather_response.text)


#call
#get_data(urls) 

#test from Rachel
#call
#weather_data = os.listdir(os.path.join(PATH, 'weather'))

def load_and_read_weather(listdir, path):
    dfs = []
    for fname in listdir:
        if fname.endswith('.csv'):
            st, month = fname.split('_')
            df = pd.read_csv(os.path.join(path, 'weather', fname), skiprows=4)
            df['State'] = st
            df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')
            dfs.append(df)

        df = pd.concat(dfs)
        df = df.sort_values(['State', 'Date'])
        df['Year'] = df['Date'].map(lambda d: d.year)
        df['Month'] = df['Date'].map(lambda d: d.month)
    
    return df

#weather_df = load_and_read_weather(weather_data, PATH)

#end test
#works!!!!

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
    
    df['Consumption'] = df['Consumption'].map(lambda c:c/1000000) #unit conversion on Consumption (now in millions)

    return df

#call
#energy_df = load_energy(PATH, 'energy.xls')

#energy_df.head()
#energy_df.tail()

#weather df doesn't have a coll Month -oh, we'll use mine -re-fixing
#now it does...
def month_df(df, month_number):
    df1 = df[df['Month'] == month_number]
    return df1



#call
#df_jan = month_df(weather_df, 1)
#df_aug = month_df(weather_df, 8)
  
#inner gets rid of years that do not exist in both datasets (so years before 1990 and after 2019)
#jan_merged_df = df_jan.merge(energy_df, on=['State','Year'], how = 'inner') 
#aug_merged_df = df_aug.merge(energy_df, on=['State','Year'], how = 'inner') 
#cite https://stackoverflow.com/questions/41815079/pandas-merge-join-two-data-frames-on-multiple-columns


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
#plot_multi_state(weather_df, STATE_LIST)

#cite for graph:
# https://stackoverflow.com/questions/44825950/matplotlib-create-two-subplots-in-line-with-two-y-axes-each 



#will use this one
#updated to use month_df instead of state_month_df
def month_temp_plot(df, month_num, month_name, STATE_LIST):
    fig, ax = plt.subplots(1, 1)
    for color, label in STATE_LIST:
        #state = state_month_df(df, month_num, label)
        df_month = month_df(df, month_num)
        state = df_month[df_month['State'] == label]
        ax.plot(state['Year'], state['Value'], color, label = label)
    ax.legend(loc='upper right')
    plt.suptitle('Average '+ month_name + ' Temperature')
    plt.savefig(PATH+'/Aug_Temp.png')
    plt.show()

#month_temp_plot(weather_df, 8, 'August', STATE_LIST)

'''
def summary_stats(df, STATE_LIST, month_num):
    for color, label in STATE_LIST:
        df_month = month_df(df, month_num)
        state = df_month[df_month['State'] == label]
        #state = state_month_df(df, 8, label)
        print('Max/Mean/Min for '+label+':', state['Value'].max(), state['Value'].mean(), state['Value'].min())
'''
#works
def summary_stats(df, STATE_LIST, month_num, colum_name, quiry):
    for color, label in STATE_LIST:
        df_month = month_df(df, month_num)
        state = df_month[df_month['State'] == label]
        #state = state_month_df(df, 8, label)
        print('Max/Mean/Min '+ quiry + ' for ' +label+':', state[colum_name].max(), state[colum_name].mean(), state[colum_name].min())


#call
#summary_stats(weather_df, STATE_LIST, 8, 'Value', 'August Temperature')
#summary_stats(aug_merged_df, STATE_LIST, 8, 'Consumption', 'Energy Use')

#stack overflow 
#need to get the ledend working!
#changed order of energy use and temp -so the line goes over the bar graph
def two_scales(ax1, axis, data1, data2, c1, c2, state_string, month):
    ax2 = ax1.twinx()
    #ax1.plot(axis, data1, color=c1, label = 'temp')
    ax1.bar(axis, data1, color=c1, label = 'Energy Use')
    #ax1.set_xlabel('Year')
    ax1.set_ylabel('Energy Use in millions')
    ax1.plot(np.NaN, color = c2, label='Average '+month+' Temp') #plot an empty line so that we can have a legend
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    #cite: https://stackoverflow.com/questions/29188757/matplotlib-specify-format-of-floats-for-tick-lables 
    ax2.plot(axis, data2, color=c2, label = 'Average '+month+' Temp')
    #ax2.bar(axis, data2, color=c2, label = 'energy')
    #ax[i].bar('Year', 'Consumption', data=d)
    #ax2.set_ylabel('Average '+month+' Temp')
    ax2.set_ylabel('Degrees Fahrenheit', rotation=270,labelpad=15)
    #rotates the second axis lable 180 degrees from start (it is at 90 degrees by default)
    #cite: https://stackoverflow.com/questions/27671748/how-to-print-y-axis-label-horizontally-in-a-matplotlib-pylab-chart 
    #ax1.legend(loc='upper right')
    ax1.legend(loc='upper right', bbox_to_anchor=(1.11,1.25), fontsize = 'small')
    #cite: bbox_to_anchor https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot 
    #cite: fontsize https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.axes.Axes.legend.html
    
    plt.title(state_string)
    return ax1, ax2

#ymax = ax1.get_ylim()[1] #-> botom, top this just gives us the top
#so this includes matplotlib's automatic padding

#TA was helping me with the energy plot: was on this cite
#matplotlib.org/decdocs/gallery/subplots_axes_and_figures/subplots_demo.html

#works
def weather_energy_state_plot(jan_merged_df, STATE_LIST, month_string):
    #fig, ([ax[0], ax[1]], [ax[2], ax[3]]) = plt.subplots(2,2,figsize=(12,6))
    fig, ax_2x2 = plt.subplots(2,2,figsize=(12,6))
    ax = [l for l2 in ax_2x2 for l in l2] #flaten 
    #cite: help from Jeff Levy
    energy_colors = ['tab:blue','gold', 'c', 'cornflowerblue']
    #cite https://matplotlib.org/3.1.0/gallery/color/named_colors.html
    for index, (color, label) in enumerate(STATE_LIST):
        #print(index,color, label)#debug
        ax[index] = two_scales(ax[index], jan_merged_df[jan_merged_df['State'] == label]['Year'],
                jan_merged_df[jan_merged_df['State'] == label]['Consumption'],
                jan_merged_df[jan_merged_df['State'] == label]['Value'],
                energy_colors[index], color,label, month_string)
    plt.tight_layout()
    plt.savefig(PATH+'/'+month_string+'Energy_temp_plot.png')
    plt.show()  

#cite for graph:
# https://stackoverflow.com/questions/44825950/matplotlib-create-two-subplots-in-line-with-two-y-axes-each 

#call
def main():
    urls = [build_url(st, mo, base_url) for st, mo in itertools.product(states, months)]
    urls.append(energy_url)
    weather_data = os.listdir(os.path.join(PATH, 'weather')) #PC
    weather_df = load_and_read_weather(weather_data, PATH)
    energy_df = load_energy(PATH, 'energy.xls')
    df_jan = month_df(weather_df, 1)
    df_aug = month_df(weather_df, 8)
  
    #inner gets rid of years that do not exist in both datasets (so years before 1990 and after 2019)
    jan_merged_df = df_jan.merge(energy_df, on=['State','Year'], how = 'inner') 
    aug_merged_df = df_aug.merge(energy_df, on=['State','Year'], how = 'inner') 
    #cite https://stackoverflow.com/questions/41815079/pandas-merge-join-two-data-frames-on-multiple-columns

    plot_multi_state(weather_df, STATE_LIST)
    month_temp_plot(weather_df, 8, 'August', STATE_LIST)

    weather_energy_state_plot(jan_merged_df, STATE_LIST, 'January')
    weather_energy_state_plot(aug_merged_df, STATE_LIST, 'August')
    summary_stats(weather_df, STATE_LIST, 8, 'Value', 'August Temperature')
    summary_stats(aug_merged_df, STATE_LIST, 8, 'Consumption', 'Energy Use')

main()
#jan_merged_df.head()
#list(jan_merged_df)
'''
CAyear = jan_merged_df[jan_merged_df['State'] == "California"]['Year']
CAconsum = jan_merged_df[jan_merged_df['State'] == "California"]['Consumption']
CAtemp = jan_merged_df[jan_merged_df['State'] == "California"]['Value']
Ayear = jan_merged_df[jan_merged_df['State'] == "Alabama"]['Year']
Aconsum = jan_merged_df[jan_merged_df['State'] == "Alabama"]['Consumption']
Atemp = jan_merged_df[jan_merged_df['State'] == "Alabama"]['Value']
energy_colors = ['tab:blue','gold', 'c', 'cornflowerblue']
weather_colors = ['k', 'r', 'b', 'darkgreen']

#working:
fig, ax = plt.subplots(2,1)
#ax0 = ax[0]
#ax1 = ax[1]
ax[0] = two_scales(ax[0], CAyear, CAconsum,CAtemp, energy_colors[0], weather_colors[0],"California", "Jan")
ax[1] = two_scales(ax[1], Ayear, Aconsum,Atemp, energy_colors[1], weather_colors[1],"Alabama", "Jan")          
plt.tight_layout()
plt.show()             
'''


    






#not in use
'''
def main():
    #jan_aug_diff_plot(df, STATE_LIST)
    month_temp_plot(weather_df, 8, 'August', STATE_LIST)
    #month_temp_plot(df, 1, STATE_LIST)
    summary_stats(df, STATE_LIST) 


#call
main()
'''

