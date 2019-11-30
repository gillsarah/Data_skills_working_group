import os 
import pandas as pd
import matplotlib.pyplot as plt

path= '/Users/Sarah/Documents/GitHub/assignment-6-gillsarah'

#from Final Project last Quarter altered for HW2...
def read_df(path, filename):
    df = pd.read_csv(os.path.join(path, filename))
    return df


#inst_df = read_df(path, 'EducationDataPortal_11.27.2019_institutions.csv')
stu_df = read_df(path, 'EducationDataPortal_11.27.2019_level_of_studyRaceSex.csv')
inst_df = read_df(path, 'EducationDataPortal_11.28.2019_institutions.csv')
#df2 = read_df(path, 'EducationDataPortal_11.28.2019_level_of_study.csv')

def filter_df(df, col, col_value):
    '''
    takes a df, a col name from that df and one value in that col
    returns a df filtered to include only entries that have col_value in col
    Note: need to use unitid to get one uni bc uni name sometimes changes
    '''
    filtered_df = df[stu_df[col] == col_value]
    return filtered_df

def merge_dfs(df1, df2, merge_how, merge_on):

    merge_df = df1.merge(df2, how = merge_how, on = merge_on)
 
    return merge_df

df = filter_df(stu_df, 'sex', 'Total')
df2 = filter_df(df, 'race', 'White')
df3 = filter_df(df2, 'year', 2016)

df4 = filter_df(inst_df, 'year', 2016)

df4['year'].unique()
df3['year'].unique()

inst_df['year'].dtype

df3.head()

m_df = merge_dfs(df3, df4, merge_how= 'inner', merge_on = 'inst_name')
m_df.shape

test = filter_df(m_df, 'unitid', 142832)

def death_green_SES_plot(df, y, ylabel):
    x = 'headcount'
    z = df['inst_name']
    #a_list = df['Per_Capita_Income']/1000
    ax = df.plot(kind='scatter', x=x, y= y,  figsize= (8,8)) #, s = a_list, figsize= (10,8))
    #cite https://github.com/pandas-dev/pandas/issues/16827
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Percent of Area that is Green')
    #lable point with Community_Area_Name, only if enough green or max death (for viewability) 

    temp_list = []
    for i, txt in enumerate(z): 
        ax.annotate(txt, (df[x][i], df[y][i]), horizontalalignment='center', verticalalignment='bottom')
        '''
        if df[x][i] >= 2:
            ax.annotate(txt, (df[x][i], df[y][i]), horizontalalignment='center', verticalalignment='bottom')
        elif df[y][i] == df[y].max():
            temp_list.append(i)
            temp_list.append(txt)
            if len(temp_list) >=4:
                ax.annotate(temp_list[1], (df[x][temp_list[0]], df[y][temp_list[0]]), 
                            horizontalalignment='left', verticalalignment='bottom')
                ax.annotate(temp_list[3], (df[x][temp_list[2]], df[y][temp_list[2]]), 
                            horizontalalignment='left', verticalalignment='top')
            else:
                ax.annotate(temp_list[1], (df[x][temp_list[0]], df[y][temp_list[0]]), 
                            horizontalalignment='left', verticalalignment='bottom')
        else:
            pass 
            '''
    #cite: https://stackoverflow.com/questions/14432557/matplotlib-scatter-plot-with-different-text-at-each-data-point
    #https://matplotlib.org/3.1.0/gallery/text_labels_and_annotations/annotation_demo.html
    #remove spines
    ax.spines['right'].set_visible(False) 
    ax.spines['top'].set_visible(False)
    # Make a legend for per-capita income
    #for a_list in [10, 20, 30]:
    #    plt.scatter([], [], c='k', alpha=0.3, s=a_list,
    #                label=str(a_list) + 'k')
    #plt.legend(scatterpoints=1, frameon=False, labelspacing=1, title='Per-Capita Income')
    #cite https://jakevdp.github.io/PythonDataScienceHandbook/04.06-customizing-legends.html
    #plt.savefig('SES_Green_and_Deaths_by_' +y)
    #plt.close()
    plt.show()

death_green_SES_plot(m_df, 'number_admitted', 'number_admitted')


print(m_df.loc[10])
print(m_df.loc[11])
print(m_df.loc[12])

