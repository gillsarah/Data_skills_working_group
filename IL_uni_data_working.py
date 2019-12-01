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
    filtered_df = df[df[col] == col_value]
    return filtered_df

def merge_dfs(df1, df2, merge_how, merge_on, suffix_left='_x', suffix_right='_y'):

    merge_df = df1.merge(df2, how = merge_how, on = merge_on, suffixes = (suffix_left, suffix_right))
 
    return merge_df

race = list(stu_df['race'].unique())

#this is a very janky solution. There has got to be a better way to make percent_white colum
#however I could not get this to work another way and preserve unitid
def parse_df_for_scatter(stu_df, inst_df, race, sex = 'Total', year = 2016):
    df = filter_df(stu_df, 'sex', sex)
    df2 = filter_df(df, 'year', year)

    df_race = filter_df(df2, 'race', race)
    test = df_race.groupby('unitid').sum() #sum over graduite and undergrduite students
    df_tot = filter_df(df2, 'race', 'Total')
    df_tot2 = df_tot.groupby('unitid').sum() #sum over graduite and undergrduite students

    test2 = merge_dfs(test, df2, merge_how= 'inner', merge_on = 'unitid', 
                    suffix_left = '_'+race, suffix_right = '')
    test3 = merge_dfs(test2, df_tot2, merge_how= 'inner', merge_on = 'unitid',
                    suffix_left = '', suffix_right = '_Total')

    test3['percent_'+race] = (test3['headcount_'+race]/test3['headcount_Total'])*100

    test4=test3.groupby('unitid').mean()

    df4 = filter_df(inst_df, 'year', year)
    m_df = merge_dfs(test4, df4, merge_how= 'inner', merge_on = 'unitid')
    #m_df.shape

    m_df['admission_rate'] = m_df['number_admitted']/m_df['number_applied']

    return m_df 


m_df = parse_df_for_scatter(stu_df, inst_df, race= 'White')

def scatter_plot_annotated(df, x, y, xlabel, ylabel, title, sub_title):
    #x = 'headcount'
    z = df['inst_name']
    #a_list = df['Per_Capita_Income']/1000
    ax = df.plot(kind='scatter', x=x, y= y,  figsize= (8,6)) #, s = a_list, figsize= (10,8))
    #cite https://github.com/pandas-dev/pandas/issues/16827
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    #lable point with Community_Area_Name, only if enough green or max death (for viewability) 

    for i, txt in enumerate(z): 
        if df[x][i] <= df[x].min()+0.1:
            ax.annotate(txt, (df[x][i], df[y][i]), horizontalalignment='left', verticalalignment='bottom')
        elif df[y][i]<=df[y].min()+25:
            ax.annotate(txt, (df[x][i], df[y][i]), horizontalalignment='center', verticalalignment='bottom')
        #elif df[y][i]>25 and df[y][i]<=30 :
        #    ax.annotate(txt, (df[x][i], df[y][i]), horizontalalignment='center', verticalalignment='bottom')
        elif df[x][i]>df[x].max()-0.1 or df[y][i]> df[y].max()-19:
            ax.annotate(txt, (df[x][i], df[y][i]), horizontalalignment='center', verticalalignment='bottom')
        elif df[x][i]>0.2 and df[x][i]<0.3: #hardcoded to fix one point overlap!
            ax.annotate(txt, (df[x][i], df[y][i]), horizontalalignment='center', verticalalignment='top')
   
    #cite: https://stackoverflow.com/questions/14432557/matplotlib-scatter-plot-with-different-text-at-each-data-point
    #https://matplotlib.org/3.1.0/gallery/text_labels_and_annotations/annotation_demo.html
    #remove spines
    ax.spines['right'].set_visible(False) 
    ax.spines['top'].set_visible(False)
    plt.suptitle(title)
    plt.title(sub_title)
    
    # Make a legend for per-capita income
    #for a_list in [10, 20, 30]:
    #    plt.scatter([], [], c='k', alpha=0.3, s=a_list,
    #                label=str(a_list) + 'k')
    #plt.legend(scatterpoints=1, frameon=False, labelspacing=1, title='Per-Capita Income')
    #cite https://jakevdp.github.io/PythonDataScienceHandbook/04.06-customizing-legends.html
    plt.savefig(os.path.join(path, 'scatterplot'))
    #plt.close()
    plt.show()

scatter_plot_annotated(m_df, 'admission_rate', 'percent_white', 'Admission Rate','Percent White',
                        'IL Universities in 2016:', 'Student Body in The Most Selective Universities is Less Ratially Homogonous')



