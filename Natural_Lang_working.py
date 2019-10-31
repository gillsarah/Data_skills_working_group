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

#explore
text = pages[6] 
doc = nlp(text) 
sents = list(doc.sents)
sentance = sents[7]
sentance
for i, token in enumerate(sentance):
    print(i, token)

#noun_to_adj(doc, 'petroleum')  
token = sentance[40]
token
temp = list(token.ancestors) 
for t in temp:
    print(t, t.pos_)

child1 = list(token.children)
for t in child1: 
    print(t, t.pos_)


'''


pages[10], sents[10]
Noun -> Noun-> 'growth' n
solar.ancestors -> generation.ancestors -> 'growth'

pages[10], sents[9]
Noun -> Noun -> 'increase' n
wind.ancestors -> generation.ancestors -> 'increase'

pages[10], sents[6]
Noun->Noun-> 'drclines' v
nucear.ancestor -> generation.ancestor -> 'declines'

pages[10], sents[5]
coal
Noun -> Noun -> 'drops' v
coal.ancestor-> generation.ancestor -> 'drops' 

pages[10], sents[4]

Noun-> Noun -> 'decline' v
coal.ancestor -> Generation.child -> 'decline' 

Noun -> Noun -> Verb -> 'decline'
nucear.ancestor -> Generation.ancestor -> expected.child -> 'decline'
'''

0 ŁSolar
1 Investment
2 Tax
3 Credits
4 (
5 ITC
6 )
7 phase
8 down
9 after
10 2024
11 ,
12 but
13 solar
14 generation
15 growth
16 continues
17 because
18 the
19 costs
20 for
21 solar
22 continue
23 to
24 fall
25 faster
26 than
27 for
28 other
29 sources
30 .
