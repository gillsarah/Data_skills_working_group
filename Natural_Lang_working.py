'note, weird symbals on page 10, be sure to check'

import PyPDF2 #pip install PyPDF2
import requests
import os
import spacy
import pandas as pd
import re 

nlp = spacy.load("en_core_web_sm")

url = 'https://www.eia.gov/outlooks/aeo/pdf/aeo2019.pdf'
#url = 'https://www.eia.gov/outlooks/aeo/pdf/aeo2018.pdf'

#this is the index location of the relevant pages for each document
pages_2019 = []
pages_2018 = []


#path = r'c:\users\jeff levy\downloads\aeo2019.pdf'
path = '/Users/Sarah/Documents/GitHub/assignment-3-sarah_gill'
os.chdir(os.path.expanduser(path))


def get_pdf(url, path):
    response = requests.get(url)
    with open(os.path.join(path, 'aeo2019.pdf'), 'wb') as ofile:
        ofile.write(response.content)

#call
#get_pdf(url, path)


def read_pdf():
    pass 

with open(os.path.join(path, 'aeo2019.pdf'), 'rb') as ifile:
    pdf = PyPDF2.PdfFileReader(ifile)

    print('Number of pages:', pdf.numPages)

    pages = []
    for p in range(pdf.numPages):
        page = pdf.getPage(p)
        text = page.extractText()
        text = text.replace('\n', '') #remove \n
        pages.append(text)



def noun_to_adj(doc, noun):
    noun_tokens = [t for t in doc if t.string.strip() == noun]
    for nt in noun_tokens:
        verb_ancestors = [t for t in nt.ancestors if t.pos_ == 'VERB']
        for vt in verb_ancestors:
            adj_children = [t for t in vt.children if t.pos_ == 'ADJ']
            print('Noun:', noun, '\n--> Verb:', vt, '\n--> Adj:', adj_children)

#explore again
#maybe I need to look at noun_chunks 
text = pages[5] 
doc = nlp(text) 
list(doc.noun_chunks) 

'''
v = sents[7][7]
list(v.subtree) #that's the whole sentnace
list(v.ancestors)
list(v.children)
'''




#explore
text = pages[10] 
doc = nlp(text) 
sents = list(doc.sents)
sentance = sents[10]
sentance
for i, token in enumerate(sentance):
    print(i, token)

#noun_to_adj(doc, 'petroleum')  
token = sentance[0]
token
temp = list(token.ancestors) 
for t in temp:
    print(t, t.pos_)

child1 = list(token.children)
for t in child1: 
    print(t, t.pos_)

#ent_type is not helpful in this doc
for token in sentance:
    print(token, token.ent_type_)
#meh 
for token in sentance:
    print(token, token.dep_)


text = 'Solar Investment Tax Credits (ITC) phase down after 2024, but solar generation growth continues because the costs for solar continue to fall faster than for other sources.'
#can't make this one work: 'Assumptions of declining costs and improving performance make wind and solar increasingly competitive compared with other renewable resources in the Reference case.'
doc = nlp(text)
for i, token in enumerate(doc):
    print(i, token)

token = doc[22]
    econ_list= ['costs']
    production_direction = production_down 

    energy_mentions = [t for t in sentance if t.text in solar]
    #energy_mentions

    energy_ancestors = [list(w.ancestors) for w in energy_mentions]
    #print('energy_ancestors')
    #print(energy_ancestors)
    energy_direction_children = [[]]
    energy_direction= [[a for a in ancestors if a.text in production_direction] for ancestors in energy_ancestors]
    energy_direction_children = [[list(w.children) for w in child] for child in energy_direction]

    for ancestor_list in energy_ancestors: #nich solution for cost of solar (may work for other 'continuing' mentions)
        for ancestor in ancestor_list:
            print(ancestor)
            if ancestor.text in econ_list:
                econ_mention = ancestor
                econ_ancestors = list(ancestor.ancestors)
                for t in econ_ancestors:
                    if t.text == 'continue':
                        print('cont')
                        continue_chidren = list(t.children)
                        for child in continue_chidren:
                            if child.text in production_direction:
                                print('yup')
                                energy_direction_children.append([[ancestor]])


            elif ancestor.text in production_direction:
                print('here')
                energy_direction = list(ancestor.ancestors)
                for en in energy_direction:
                    temp_list = list(en.children)
                    energy_direction_children.append([[temp_list]])
            else:
                print('nope')
                
    energy_direction_children
    
    down_count = 0

    for ancestor_list in  energy_direction_children:
        #print(token_list)
        for token_list in ancestor_list:
            for ancestor in token_list:
                #print(ancestor)
                #print(ancestor.text)
                if ancestor.text in econ_list:
                #if ancestor.text in price_list:
                    print('found down')
                    down_count += 1
    
    totals_list = [0,0]
    temp_list = [1,0]
    totals_list = [sum(x) for x in zip(totals_list, temp_list)]
    df = empty_df()
    energy_price = totals_list
    fill_df(df, energy_price, 'solar', 'price')
    

                energy_direction= [[a for a in ancestors if a.text in production_direction] for ancestors in energy_ancestors]
                energy_direction_children = [[list(w.children) for w in child] for child in energy_direction]


'''
Noune -> Noun-> verb -> verb
solar.ancestors -> costs.ancesors-> continue.children -> fall
solar.ancestors -> continue.children -> fall.children -> faster 
continue.children -> costs

wind.ancestors -> competitive.ancestors -> make
wind.ancestors -> make.ancestors -> []

same for solar
Assumptions goes straight to make!
'''

'''
2018
Noun->noun->
solar.ancestor -> generation.ancestor -> leads.anc -> []
solar.ancestor -> leads.children -> growth.children -> the

wind.ancestor -> leads

prices
Noun -> Noun -> verb -> rise 
oil.ancestors -> prices.ancestors -> projected.children -> rise
'''


'''
Imort/expors
pages[6], sents[6]
petroleum.ancestors -> 'exporter'

pages[6], sents[7]
petrolium.ancestor -> 'importer'

pages[6], sents[10]
coal.ancestor -> 'exporter'

'''



'''
Price
page[10],sents[10]
solar.ancestor -> costs.ancestor -> continue.child -> 'fall'
'''

'''
pates[6], sents[6]
oil.ancestor -> production.ancestor -> 'increases' n and 'decreased' v

pages[6], sents[7]
oil.ancestor -> production.ancestor -> 'falling' v and 'increasing' v

pages[10], sents[10]
Noun -> Noun-> 'growth' n
solar.ancestors -> generation.ancestors -> 'growth'

pages[10], sents[9]
Noun -> Noun -> 'increase' n
wind.ancestors -> generation.ancestors -> 'increase'

pages[10], sents[6]
Noun->Noun-> 'drclines' v
nucear.ancestor -> generation.ancestor -> 'declines'

Noun-> verb -> 'generation'
nuclear.ancestor -> declines.children -> 'generation'

pages[10], sents[5]
Noun -> Noun -> 'drops' v
coal.ancestor-> generation.ancestor -> 'drops' 
Noun -> verb
coal.ancestor-> drops.children -> 'generation'

pages[10], sents[4]
Noun-> Noun -> 'decline' v
coal.ancestor -> Generation.child -> 'decline' 

Noun -> Noun -> Verb -> 'decline'
nucear.ancestor -> Generation.ancestor -> expected.child -> 'decline'
'''


#may need to remove the chart data:

#pipeline to tokenize
#when wrap in mlp
#you can customize the tokenization
#to remove sentances youll need to re-tokenize
#or get the text out, go to teh origional text
#then re-do the doc= 

#the correct way is to retokenize but using sring methods is ok

#sents is a spam
text.replace(s.text, '')


text = pages[10]
doc = nlp(text)
sents = list(doc.sents)
sents[3]

sentance0 = sents[0].text
sents[0] = sentance0.replace(sentance0, '')
sentance1 = sents[1].text
sents[1] = sentance1.replace(sentance1, '')

 
new_doc = nlp(text.replace(sents[0].text, '')
#new_doc = nlp(text.replace(sents[1].text, '')
#sents = list(new_doc.sents)
#sents[0]

page_num = 6
energy_type = ['coal', 'Coal']#['nuclear' ,'Nuclear']#


text = pages[page_num]
doc = nlp(text)

energy_mentions = [t for t in doc if t.text in energy_type]
energy_mentions

energy_ancestors = [list(w.ancestors) for w in energy_mentions]
print('energy_ancestors')
print(energy_ancestors)

energy_production = [[a for a in ancestors if a.text in production_list] for ancestors in energy_ancestors]
energy_production

energy_production_ancestors = [[list(w.ancestors) for w in ancestors] for ancestors in energy_production]
energy_production_ancestors    #[item for sublist in l for item in sublist]

energy_production_children = [[list(w.children) for w in child] for child in energy_production]
energy_production_children

production_up = ['increase','increases', 'increasing','growth']
production_down = ['decreases','decreased', 'decline','declines','drops']

up_count = 0
down_count = 0


for ancestor_list in energy_production_ancestors:
    #print(token_list)
    for token_list in ancestor_list:
        for ancestor in token_list:
            negation = test_negation(ancestor)
            print(negation)
            #print(ancestor)
            #print(ancestor.text)
            if ancestor.text in production_list and not negation:
                print('found up')
                up_count += 1
            elif ancestor.text in production_down and not negation:
                print('found down')
                down_count += 1
            elif ancestor.text = 'export' and negation:
                print('found negation')
            '''
            else:
                t = list(ancestor.ancestors)
                print(t)
                for token in t:
                    if token.text in production_up:
                        print('found up')
                        up_count += 1 
                    elif token.text in production_down:
                        print('found down')
                        down_count += 1
            '''
print([up_count, down_count])
#wrong 


text = pages[6]
doc = nlp(text)
sents = list(doc.sents)
sentance = sents[10]
sentance
for i, token in enumerate(sentance):
    print(i, token)

list(sentance[30].ancestors)

token = sentance[25] #exports
anc = list(token.ancestors) 
anc_children = [list(a.children) for a in anc]

test_negation (sentance[3])

#works!!
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


page_num = 10
energy_type =  ['solar', 'Solar', "PV"]#['coal', 'Coal'] #['nuclear' ,'Nuclear']#['wind', "Wind"] #
production_up = ['increase','increases', 'increasing','growth']
production_down = ['decreases','decreased', 'decline','declines','drops']
price_list = ['price', 'prices', 'costs']

text = pages[page_num]
doc = nlp(text)

energy_mentions = [t for t in doc if t.text in energy_type]
energy_mentions

energy_ancestors = [list(w.ancestors) for w in energy_mentions]
print('energy_ancestors')
print(energy_ancestors)

energy_up = [[a for a in ancestors if a.text in production_up] for ancestors in energy_ancestors]
energy_up

#negation
energy_up_ancestors = [[list(w.ancestors) for w in ancestor_list] for ancestor_list in energy_up]
[[a for a in ancestors if a.dep_ != 'neg'] for ancestors in energy_ancestors]


energy_down = [[a for a in ancestors if a.text in production_down] for ancestors in energy_ancestors]
energy_down

#negation
neg_list = ['fallen', 'down', 'not', "n't"]
pos_negation = len([pva for pva in pos_verb_ancestors if any([p.string.strip() in neg_list for p in pva])])
token.dep_

#energy_direction_ancestors = [[list(w.ancestors) for w in ancestors] for ancestors in energy_production]
#energy_production_ancestors    #[item for sublist in l for item in sublist]

energy_up_children = [[list(w.children) for w in child] for child in energy_up]
energy_down_children =[[list(w.children) for w in child] for child in energy_down]
energy_up_children
energy_down_children



up_count = 0
down_count = 0

for ancestor_list in energy_up_children:
    #print(token_list)
    for token_list in ancestor_list:
        for ancestor in token_list:
            #print(ancestor)
             #print(ancestor.text)
            #if ancestor.text in production_list:
            if ancestor.text in price_list:
                print('found up')
                up_count += 1

for ancestor_list in energy_down_children:
    #print(token_list)
    for token_list in ancestor_list:
        for ancestor in token_list:
            #print(ancestor)
             #print(ancestor.text)
            #if ancestor.text in production_list:
            if ancestor.text in price_list:
                print('found down')
                down_count += 1
print([up_count, down_count])



#from Prof:
def noun_to_adj(doc, noun):
    noun_tokens = [t for t in doc if t.string.strip() == noun]
    for nt in noun_tokens:
        verb_ancestors = [t for t in nt.ancestors if t.pos_ == 'VERB']
        for vt in verb_ancestors:
            adj_children = [t for t in vt.children if t.pos_ == 'ADJ']
            print('Noun:', noun, '\n--> Verb:', vt, '\n--> Adj:', adj_children)


text = pages[11] 
doc = nlp(text) 
noun_to_adj(doc, 'petroleum')  


text = r'Natural gas emissions grow at an annual rate of 0.8%, while petroleum and coal emissions decline at annual rates of 0.3% and 0.2%, respectively.'
#text = 'Petroleum emissions rise in each of the final 13 years of the projection period, when increased vehicle usage outweighs efficiency gains.'
doc = nlp(text) 
for i, token in enumerate(doc):
    print(i, token)
token = doc[3]

list(token.ancestors)
list(token.children)

'''
coal.ancestors -> emmissions.ancestor -> decline V and grow V
coal.ancestors-> decline.ancestors -> grow!
coal.ancestors -> grown.ancestors -> []

petroleum.ancestors -> decline and grow
'''

list(doc.noun_chunks)

'''
Petroeum.ancestors -> emissions.ancestors -> rise

#same as with production!
Petroeum.ancestors -> rise.children -> emissions
'''





nchunks = [nc for nc in doc.noun_chunks if 'rate' in nc.string]
nchunks

kinds_of_rates = {'production': [nc for nc in doc.noun_chunks if 'coal' in nc.string and 'production' in nc.string],
                  'fed funds':    [nc for nc in doc.noun_chunks if 'rate' in nc.string and 'federal' in nc.string],
                  'discount':     [nc for nc in doc.noun_chunks if 'rate' in nc.string and 'discount' in nc.string]}
                