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

month_temp_plot(weather_df, 8, 'August', STATE_LIST)

fig, ax = plt.subplots()
ax2 = ax.twinx()
plt.show()

for index, (color, label) in enumerate(STATE_LIST):
        #print(index,color, label)
    state = jan_aug_diff(df, label)
    ax[index].plot(state['Year'], state['Jan-Aug Delta'], color)
    ax[index].set_ylabel(label) 

    plt.show()

#stack overflow 
def two_scales(ax1, axis, data1, data2, c1, c2):
    ax2 = ax1.twinx()
    ax1.plot(axis, data1, color=c1)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Average August Temp')
    ax2.plot(axis, data2, color=c2)
    ax2.set_ylabel('Energy Use')
    return ax1, ax2

# Create some mock data
state_energy_use = jan_merged_df[jan_merged_df['State'] == 'Alabama']
t = state_energy_use['Year']
s1 = state_energy_use['Value']
s2 = state_energy_use['Consumption']
CA_energy_use = jan_merged_df[jan_merged_df['State'] == 'California']
p = CA_energy_use['Year']
s3 = CA_energy_use['Value']
s4 = CA_energy_use['Consumption']

# Create axes
fig, (ax1, ax2) = plt.subplots(1,2, figsize=(10,4))
ax1, ax1a = two_scales(ax1, t, s1, s2, 'r', 'b')
ax2, ax2a = two_scales(ax2, p, s3, s4, 'gold', 'limegreen')

# Change color of each axis
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
#cite:https://stackoverflow.com/questions/44825950/matplotlib-create-two-subplots-in-line-with-two-y-axes-each 

state_energy_use = energy_df[energy_df['State'] == 'Alabama']
plt.bar(state_energy_use['Consumption'])
plt.show() 

#working 
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

df_jan = month_df(weather_df, 1)
df_aug = month_df(weather_df, 8)

'''
def make_modern(weather_df):
    modern_weather = pd.DataFrame(weather_df.drop(weather_df[weather_df['Year'] < 1990].index))
    return modern_weather
#call
df_new_jan = make_modern(df_jan)

#modern_weather = pd.DataFrame(weather_df.drop(weather_df[weather_df['Year'] < 1990].index))
#modern_grouped = modern_weather.groupby(['Date', pd.Grouper(freq='m')])
'''

#inner gets rid of years that do not exist in both datasets (so years before 1990 and after 2019)
jan_merged_df = df_jan.merge(energy_df, on=['State','Year'], how = 'inner') 
aug_merged_df = df_aug.merge(energy_df, on=['State','Year'], how = 'inner') 





#will use this one
def month_temp_plot(df, month_num, month_name, STATE_LIST):
    fig, ax = plt.subplots(1, 1)
    for color, label in STATE_LIST:
        state = state_month_df(df, month_num, label)
        ax.plot(state['Year'], state['Value'], color, label = label)
    ax.legend(loc='upper right')
    plt.suptitle('Average '+ month_name + ' Temperature')
    plt.savefig(save_plots_path+'/Aug_Temp.png')
    plt.show()


def summary_stats(df, STATE_LIST):
    for color, label in STATE_LIST:
        state = state_month_df(df, 8, label)
        print('Max/Mean/Min for '+label+':', state['Value'].max(), state['Value'].mean(), state['Value'].min())

def main():
    

    

    jan_aug_diff_plot(df, STATE_LIST)
    month_temp_plot(weather_df, 8, 'August', STATE_LIST)
    #month_temp_plot(df, 1, STATE_LIST)
    summary_stats(df, STATE_LIST) 


#call
main()

