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
#STATE_LIST = [('k-','Illinois'), ('r-','California'), 
#              ('b-', 'New York'), ('g-','Texas')]

#chose 4 states to plot and the colors for their lines.
STATE_LIST = [('k','Illinois'), ('r','California'), 
              ('b', 'New York'), ('darkgreen','Texas')]

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

weather_df = read_weather(PATH)

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
    #plt.suptitle('Average Jan-Aug Temperature Variation')
    #plt.savefig(save_plots_path+'/Jan-Aug_Variation.png')
    plt.show()  
    #cite: https://stackoverflow.com/questions/14880192/iterate-a-list-of-tuples
'''

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
plot_multi_state(weather_df, STATE_LIST)


#stack overflow 
#need to get the ledend working!
#changed order of energy use and temp -so the line goes over the bar graph
def two_scales(ax1, axis, data1, data2, c1, c2, state_string, month):
    ax2 = ax1.twinx()
    #ax1.plot(axis, data1, color=c1, label = 'temp')
    ax1.bar(axis, data1, color=c1, label = 'temp')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Energy Use')
    ax2.plot(axis, data2, color=c2, label = 'energy')
    #ax2.bar(axis, data2, color=c2, label = 'energy')
    #ax[i].bar('Year', 'Consumption', data=d)
    ax2.set_ylabel('Average '+month+' Temp')
    #ax1.legend(loc='upper right')
    #ax2.legend(loc='upper right')
    #plt.legend([ax1,ax2], ['first', 'second']) #doesn't work!
    #cite:https://jakevdp.github.io/PythonDataScienceHandbook/04.06-customizing-legends.html
    plt.title(state_string)
    return ax1, ax2

#can't do histogram bc x-axis needs to be year for both and that is not how a hist works
#ax2.plot(axis, data2, color=c2, label = 'energy')


#works
def temp_energy_state_plot(jan_merged_df, STATE_LIST, month_string):
    fig, ([ax[0], ax[1]], [ax[2], ax[3]]) = plt.subplots(2,2,figsize=(12,6))
    #weather_colors = ['k', 'r', 'b', 'darkgreen']
    energy_colors = ['tab:blue','gold', 'c', 'cornflowerblue']
    #cite https://matplotlib.org/3.1.0/gallery/color/named_colors.html
    for index, (color, label) in enumerate(STATE_LIST):
        #print(index,color, label)#debug
        '''
        ax[index] = two_scales(ax[index], jan_merged_df[jan_merged_df['State'] == label]['Year'],
                jan_merged_df[jan_merged_df['State'] == label]['Value'],
                jan_merged_df[jan_merged_df['State'] == label]['Consumption'],
                weather_colors[index], energy_colors[index], label, month_string)
        '''
        ax[index] = two_scales(ax[index], jan_merged_df[jan_merged_df['State'] == label]['Year'],
                jan_merged_df[jan_merged_df['State'] == label]['Consumption'],
                jan_merged_df[jan_merged_df['State'] == label]['Value'],
                energy_colors[index], color,label, month_string)
    plt.tight_layout()
    plt.savefig(save_plots_path+'/'+month_string+'Energy_temp_plot.png')
    plt.show()  

temp_energy_state_plot(jan_merged_df, STATE_LIST, 'January')
temp_energy_state_plot(aug_merged_df, STATE_LIST, 'August')


'''   
state_energy_use = jan_merged_df[jan_merged_df['State'] == 'Alabama']
t = state_energy_use['Year']
s1 = state_energy_use['Value']
s2 = state_energy_use['Consumption']
CA_energy_use = jan_merged_df[jan_merged_df['State'] == 'California']['Year']
p = CA_energy_use['Year']
s3 = CA_energy_use['Value']
s4 = CA_energy_use['Consumption']
'''


# Create axes
'''
fig, ([ax1, ax2], [ax3, ax4]) = plt.subplots(2,2)
ax1= two_scales(ax1, t, s1, s2, 'r', 'b', 'Alabama')
ax2 = two_scales(ax2, p, s3, s4, 'gold', 'limegreen', 'California')
ax3 = two_scales(ax3, p, s3, s4, 'gold', 'limegreen', 'a')
ax4= two_scales(ax4, p, s3, s4, 'gold', 'limegreen', 'b')
plt.show()

fig, ([ax1, ax2], [ax3, ax4]) = plt.subplots(2,2)
ax1, ax1a = two_scales(ax1, t, s1, s2, 'r', 'b', 'Alabama')
ax2, ax2a = two_scales(ax2, p, s3, s4, 'gold', 'limegreen', 'California')
ax3, ax3a = two_scales(ax3, p, s3, s4, 'gold', 'limegreen', 'a')
ax4, ax4a = two_scales(ax4, p, s3, s4, 'gold', 'limegreen', 'b')

#works!
fig, ([ax[0], ax[1]], [ax[2], ax[3]]) = plt.subplots(2,2)
ax[0] = two_scales(ax[0], t, s1, s2, 'r', 'b', 'Alabama')
ax[1] = two_scales(ax[1], p, s3, s4, 'gold', 'limegreen', 'California')
ax[2]= two_scales(ax[2], p, s3, s4, 'gold', 'limegreen', 'a')
ax[3]= two_scales(ax[3], p, s3, s4, 'gold', 'limegreen', 'b')
plt.tight_layout()
plt.show()
'''
#ax1.xaxis.tick_top()
#ax2.set_label('')
#ax2.set_xticks([])
#ax2.xaxis.set_ticks_position('none')
#ax3.set_label('') #ledgend lable
#ax3.set_xticks([]) #removes the label of x-axis
#ax3.xaxis.set_ticks_position('none')


# Change color of each axis
#can't use this anymore -can iether use this or be able to automiate axes numbering
'''
def color_y_axis(ax, color):
    """Color your axes."""
    for t in ax.get_yticklabels():
        t.set_color(color)

color_y_axis(ax1, 'r')
color_y_axis(ax1a, 'b')
color_y_axis(ax2, 'gold')
color_y_axis(ax2a, 'limegreen')

plt.tight_layout()
plt.show()
'''
#cite for graph:
# https://stackoverflow.com/questions/44825950/matplotlib-create-two-subplots-in-line-with-two-y-axes-each 








#working 
'''
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
'''


'''
#output is a df of one state for one month (e.g. IL for Aug of each year)
#not useing this
def state_month_df(df, month_number, state_string):
    df['Month'] = df['Date'].map(lambda d: d.month)
    df_month = df[df['Month'] == month_number]
    state = df_month[df_month['State'] == state_string]
    return state
'''

#useing this
def month_df(df, month_number):
    df['Month'] = df['Date'].map(lambda d: d.month)
    df_month = df[df['Month'] == month_number]
    #state = df_month[df_month['State'] == state_string]
    return df_month

df_jan = month_df(weather_df, 1)
df_aug = month_df(weather_df, 8)

df_aug_CA = state_month_df(weather_df, 8, 'California')

#inner gets rid of years that do not exist in both datasets (so years before 1990 and after 2019)
jan_merged_df = df_jan.merge(energy_df, on=['State','Year'], how = 'inner') 
aug_merged_df = df_aug.merge(energy_df, on=['State','Year'], how = 'inner') 
#cite https://stackoverflow.com/questions/41815079/pandas-merge-join-two-data-frames-on-multiple-columns


#aug_CA_merged_df = df_aug_CA.merge(energy_df, on=['State','Year'], how = 'inner') 

#aug_CA_merged_df.head()
'''
def make_modern(weather_df):
    modern_weather = pd.DataFrame(weather_df.drop(weather_df[weather_df['Year'] < 1990].index))
    return modern_weather
#call
df_new_jan = make_modern(df_jan)

#modern_weather = pd.DataFrame(weather_df.drop(weather_df[weather_df['Year'] < 1990].index))
#modern_grouped = modern_weather.groupby(['Date', pd.Grouper(freq='m')])
'''



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
    plt.savefig(save_plots_path+'/Aug_Temp.png')
    plt.show()


def summary_stats(df, STATE_LIST, month_num):
    for color, label in STATE_LIST:
        df_month = month_df(df, month_num)
        state = df_month[df_month['State'] == label]
        #state = state_month_df(df, 8, label)
        print('Max/Mean/Min for '+label+':', state['Value'].max(), state['Value'].mean(), state['Value'].min())

#working
def summary_stats(df, STATE_LIST, month_num, colum_name, quiry):
    for color, label in STATE_LIST:
        df_month = month_df(df, month_num)
        state = df_month[df_month['State'] == label]
        #state = state_month_df(df, 8, label)
        print('Max/Mean/Min '+ quiry + ' for ' +label+':', state[colum_name].max(), state[colum_name].mean(), state[colum_name].min())


#call
summary_stats(weather_df, STATE_LIST, 8, 'Value', 'August Temperature')
summary_stats(aug_merged_df, STATE_LIST, 8, 'Consumption', 'Energy Use')



def main():
    #jan_aug_diff_plot(df, STATE_LIST)
    month_temp_plot(weather_df, 8, 'August', STATE_LIST)
    #month_temp_plot(df, 1, STATE_LIST)
    summary_stats(df, STATE_LIST) 


#call
main()

