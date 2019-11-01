'note, weird symbals on page 10, be sure to check'

import PyPDF2 #pip install PyPDF2
import requests
import os
import spacy
import pandas as pd
import re 

nlp = spacy.load("en_core_web_sm")

url = 'https://www.eia.gov/outlooks/aeo/pdf/aeo2019.pdf'
# url = 'https://www.eia.gov/outlooks/aeo/pdf/aeo2018.pdf'

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
sentance = sents[5]
sentance
for i, token in enumerate(sentance):
    print(i, token)

#noun_to_adj(doc, 'petroleum')  
token = sentance[15]
token
temp = list(token.ancestors) 
for t in temp:
    print(t, t.pos_)

child1 = list(token.children)
for t in child1: 
    print(t, t.pos_)


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
coal
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

page_num = 10
energy_type = ['nuclear' ,'Nuclear']#['coal', 'Coal']


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
            #print(ancestor)
             #print(ancestor.text)
            if ancestor.text in production_up:
                print('found up')
                up_count += 1
            elif ancestor.text in production_down:
                print('found down')
                down_count += 1
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
print([up_count, down_count])

#wrong 



page_num = 10
energy_type =  ['wind', "Wind"] #['solar', 'Solar', "PV"]#['coal', 'Coal'] #['nuclear' ,'Nuclear']#
production_up = ['increase','increases', 'increasing','growth']
production_down = ['decreases','decreased', 'decline','declines','drops']


text = pages[page_num]
doc = nlp(text)

energy_mentions = [t for t in doc if t.text in energy_type]
energy_mentions

energy_ancestors = [list(w.ancestors) for w in energy_mentions]
print('energy_ancestors')
print(energy_ancestors)

energy_up = [[a for a in ancestors if a.text in production_up] for ancestors in energy_ancestors]
energy_up

energy_down = [[a for a in ancestors if a.text in production_down] for ancestors in energy_ancestors]
energy_down

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
            if ancestor.text in production_list:
                print('found up')
                up_count += 1

for ancestor_list in energy_down_children:
    #print(token_list)
    for token_list in ancestor_list:
        for ancestor in token_list:
            #print(ancestor)
             #print(ancestor.text)
            if ancestor.text in production_list:
                print('found down')
                down_count += 1
print([up_count, down_count])
