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


text = pages[10] 
doc = nlp(text) 
sents = list(doc.sents)
sents[5]

for i, token in enumerate(sents[5]):
    print(i, token)

#noun_to_adj(doc, 'petroleum')  
token = sents[5][14]
token
temp = list(token.ancestors) 
for token in temp:
    print(token, token.pos_)

child1 = list(token.children)
for token in child1: 
    print(token, token.pos_)

'''
pages[10], sents[5]
coal
Noun -> Noun -> 'drops' v
coal.ancestor-> generation.ancestor -> 'drops' 

pages[10], sents[4]
coal
Noun-> Noun -> 'decline' v
coal.ancestor -> Generation.child -> 'decline' 

Noun -> Noun -> Verb -> 'decline'
nucear.ancestor -> Generation.ancestor -> expected.child -> 'decline'
'''
0 In
1 the
2 Reference
3 case
4 ,
5 from
6 a
7 28
8 %
9 share
10 in
11 2018
12 ,
13 coal
14 generation
15 drops
16 to
17 17
18 %
19 of
20 total
21 generation
22 by
23 2050
24 .