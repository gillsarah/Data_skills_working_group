
'''
Explanation:

As it currently is, this code uses word associations to determine the predictions about the given energy types
This means that the words of interest have to be hard coded in (see below)
This is clunky, and will not be robust to word-choice changes in future publications
Investigation using gramatical structure may prove more robust, and should be attempted in the next update
Investigation useing noun chunks may also be helpful (much of the relevant information follows the pattern
Noun, Noun, Noun or Noun, Noun, Verb)

If something is prediced to increas and decerase or be exported and imported durring the projection period
Whicever is mentined more frequently is put in the tabel or else if they are mentioned with equal frequency
it will currently be marked down as 'unclear'
A more specific and accurite way to handle this would be either to say, for instance, export then import 
(as in the case of oil in 2019) or to have the output be the prediction for the majority of the projection
Either of these would require a function that understood the lenght of the projection period and the temporal
nature of the predictions 
'''
'''
Side note:
I worked on this alone, and that was a mistake. I do not know many peopl in this class, but I will put
the effort in to find a partner next time. 
'''

import PyPDF2 #pip install PyPDF2
import requests
import os
import spacy
import pandas as pd
import re 

nlp = spacy.load("en_core_web_sm") #English

path = '/Users/Sarah/Documents/GitHub/assignment-3-sarah_gill'
os.chdir(os.path.expanduser(path)) #needed for mac


base_url = 'https://www.eia.gov/outlooks/aeo/pdf/aeo{}.pdf'

#years of interest, add as needed
years = [2018, 2019]
#this is the index location of the relevant pages for each document
pages_2019 = list(range(4, 14)) 
pages_2018 = list(range(2, 16)) 


#True if files have already been downloaded, otherwise False
downloaded = True


#these are the words of interest, add as needed 
production_up = ['increase','increases', 'increasing','growth', 'grows', 'grow']
production_down = ['decreases','decreased', 'decline','declines','drops', 'falls', 'falling', 'fall']

production_list = ['production', 'Production','generation', 'Generation'] #can remove the last one
price_list = ['price', 'prices', 'costs', 'cost', 'Price', 'Prices', 'Cost', 'Costs']
emissions_list = ['emissions', 'Emissions', 'CO2', 'carbon']
export_list = ['export', 'exporter', 'exporting', 'Export', 'Exporter', 'Exporting']
import_list = ['import', 'importer', 'importing', 'Import', 'Importer', 'Importing']

oil = ['oil', 'Oil', 'petroleum', 'Petroleum']
coal = ['coal', 'Coal']
nuclear = ['nuclear' ,'Nuclear']
solar = ['solar', 'Solar', 'PV', 'photovoltaic']
wind = ['wind', 'Wind']



def build_url(year, base):
    return base.format(year)

#call
urls = [build_url(year, base_url) for year in years] 



#called in main: if downloaded = False
def get_pdf(url, path):
    response = requests.get(url)
    filename = url[-11:]
    #cite https://stackoverflow.com/questions/7983820/get-the-last-4-characters-of-a-string
    with open(os.path.join(path, filename), 'wb') as ofile:
        ofile.write(response.content)


#called in main
def read_pdf(url, path):
    filename = url[-11:] 

    with open(os.path.join(path, filename), 'rb') as ifile:
        pdf = PyPDF2.PdfFileReader(ifile)

        print('Number of pages:', pdf.numPages)

        pages = []
        for p in range(pdf.numPages):
            page = pdf.getPage(p)
            text = page.extractText()
            text = text.replace(r'\n', '') #remove \n 
            text = text.replace(r'Ł', '') #remove Ł 
            pages.append(text)
    return pages

#convert the data to spacy tokens
# called in export_import and in energy_direction 
def tokenize(pages, page_num):
    text = pages[page_num]
    doc = nlp(text)
    return doc

#set up the df: make an empty df, set up colums, set index to be meaningful 
#called in main
def empty_df():
    df = pd.DataFrame(columns=["energy type", "price", "emissions", "production", "export/import"])
    df["energy type"]= ["coal", "nuclear", "wind", "solar", "oil"]
    df.set_index(["energy type"], inplace = True) 
    #cite: https://thispointer.com/pandas-how-to-create-an-empty-dataframe-and-append-rows-columns-to-it-in-python/
    #cite https://stackoverflow.com/questions/38542419/could-pandas-use-column-as-index
    return df


#deal with negations
#called in econ_activity
def test_negation (token, negation = False):
    anc = list(token.ancestors) 
    anc_children = [list(a.children) for a in anc]
    for token in anc:
        if token.dep_ == 'neg':
            #print('neg')
            negation = True
        #else:
            #print(token.dep_)
    for token_list in anc_children:
        for token in token_list:
            if token.dep_ == 'neg':
                #print('neg')
                negation = True
            #else:
                #print(token.dep_)
    return negation


#called in count_instances
def energy_direction(pages, page_num, energy_type, production_direction, econ_list):

    doc = tokenize(pages, page_num)

    energy_mentions = [t for t in doc if t.text in energy_type]
    #energy_mentions

    energy_ancestors = [list(w.ancestors) for w in energy_mentions]
    #energy_direction_children = [[]]
    energy_direction = [[a for a in ancestors if a.text in production_direction] for ancestors in energy_ancestors]
    energy_direction_children = [[list(w.children) for w in child] for child in energy_direction]
    
    for ancestor_list in energy_ancestors: #nich solution for cost of solar (may work for other 'continuing' mentions)
        for ancestor in ancestor_list:
            #print(ancestor)
            if ancestor.text in econ_list:
                #econ_mention = ancestor
                econ_ancestors = list(ancestor.ancestors)
                for t in econ_ancestors:
                    if t.text == 'continue':
                        continue_chidren = list(t.children)
                        for child in continue_chidren:
                            if child.text in production_direction:
                                #print('in the solar loop') #debug
                                energy_direction_children.append([[ancestor]])

    return energy_direction_children


#called in count_instances
def econ_activity(energy_up_children,energy_down_children, econ_list):

    up_count = 0
    down_count = 0

    for ancestor_list in energy_up_children:
        #print(token_list) #bebug
        for token_list in ancestor_list:
            for ancestor in token_list:
                negation = test_negation(ancestor)
                #print(ancestor) #debug
                if ancestor.text in econ_list and not negation:
                    #print('found up')
                    up_count += 1

    for ancestor_list in energy_down_children:
        #print(token_list) #debug
        for token_list in ancestor_list:
            for ancestor in token_list:
                negation = test_negation(ancestor)
                #print(ancestor) #debug
                if ancestor.text in econ_list and not negation:
                    #print('found down')
                    down_count += 1
       
    return([up_count, down_count])


#called in count_instances
def exprot_import(pages, page_num, energy_type):
    export_counter = 0
    import_counter = 0
    doc = tokenize(pages, page_num)
    energy_mentions = [t for t in doc if t.text in energy_type]
    #print(energy_mentions) #debug
    energy_ancestors = [list(w.ancestors) for w in energy_mentions]
    for token_list in energy_ancestors:
        for ancestor in token_list:
            #print(ancestor.text) debug
            if ancestor.text in export_list:
                #print('found export')
                export_counter += 1
            elif ancestor.text in import_list:
                #print('found import')
                import_counter += 1
            else:
                #print('nothing found')
                pass
    return [export_counter,import_counter]



#called in call
def count_instances(pages, page_list, energy_type, expimp = False, econ_list = []):
    '''
    takes the list of relevant pages (list of numbers), the list of words used for the energy type
    output is the new totals list, reflecting count of up and down indications
    if expimp is set to True then output will indicate count of export and import indications
    '''
    totals_list = [0,0]
    if expimp:
        for page_num in page_list:
            temp_list = exprot_import(pages, page_num, energy_type)
            totals_list = [sum(x) for x in zip(totals_list, temp_list)]
            #cite: https://stackoverflow.com/questions/18713321/element-wise-addition-of-2-lists
    else:    
        for page_num in page_list:
            energy_up_children = energy_direction(pages, page_num, energy_type, production_up, econ_list)
            energy_down_children = energy_direction(pages, page_num, energy_type, production_down, econ_list)
            temp_list = econ_activity(energy_up_children, energy_down_children, econ_list)
            totals_list = [sum(x) for x in zip(totals_list, temp_list)]
    return(totals_list)


#calld in call
def fill_df(df, totals_list, row_name, col_name, label_1='up', label_2='down', label_3='unclear'):
    '''
    takes a list for totals_list: created by one of the evaluating function
    takes a string for row_name: must match the row name
    takes a string for col_name: must match the col name
    fills in that cell with up,down or unclear
    '''
    if totals_list[0] > totals_list[1]:
        df[col_name][row_name] = label_1
    elif totals_list[0] < totals_list[1]:
        df[col_name][row_name] = label_2
    elif totals_list[0] == totals_list[1] == 0:
        pass 
    else:
        df[col_name][row_name] == label_3

#export the df 
#called in main
def export_df(df, filename):
    df.to_csv(filename)

#called in main
def call(df, energy, energy_string, pages, page_list):
    energy_expimp = count_instances(pages, page_list, energy, expimp = True)
    energy_production = count_instances(pages, page_list, energy, econ_list = production_list)
    energy_price = count_instances(pages, page_list, energy, econ_list = price_list) 
    energy_emissions = count_instances(pages, page_list, energy, econ_list = emissions_list)
    
    fill_df(df, energy_expimp, energy_string, 'export/import', 'export', 'import', 'unclear')
    fill_df(df, energy_production, energy_string, 'production')
    fill_df(df, energy_price, energy_string, 'price')
    fill_df(df, energy_emissions, energy_string, 'emissions')


def main():
    if not downloaded:
        for url in urls:
            get_pdf(url, path)
    
    pages18 = read_pdf(urls[0],path)
    pages19 = read_pdf(urls[1],path)

    #working
    df19 = empty_df()
    df18 = empty_df()
    
    
    call(df18, coal, 'coal', pages18, pages_2018)
    call(df18, nuclear, 'nuclear',pages18, pages_2018)
    call(df18, wind, 'wind', pages18, pages_2018)
    call(df18, solar, 'solar',pages18, pages_2018)
    call(df18, oil, 'oil', pages18,pages_2018)

    
    call(df19, coal, 'coal', pages19, pages_2019)
    call(df19, nuclear, 'nuclear', pages19, pages_2019)
    call(df19, wind, 'wind', pages19, pages_2019)
    call(df19, solar, 'solar',pages19, pages_2019)
    call(df19, oil, 'oil', pages19, pages_2019)
    

    export_df(df19, '2019.csv')
    export_df(df18, '2018.csv')

    print(' ')
    print('2019 Energy df')
    print(df19)

    print(' ')
    print('2018 Energy df')
    print(df18)

main()

