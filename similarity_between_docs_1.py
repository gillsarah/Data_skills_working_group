import PyPDF2 #pip install PyPDF2
import requests
import os
import spacy
import pandas as pd
import re 

nlp = spacy.load("en_core_web_sm") #English

path = '/Users/Sarah/Documents/GitHub/assignment-3-sarah_gill'
os.chdir(os.path.expanduser(path)) #needed for mac

downloaded = True

base_url = 'https://www.eia.gov/outlooks/aeo/pdf/aeo{}.pdf'

def build_url(year, base):
    return base.format(year)

#call
urls = [build_url(year, base_url) for year in years] 

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


def tokenize(pages, page_num):
    text = pages[page_num]
    doc = nlp(text)
    return doc


pages18 = read_pdf(urls[0],path)
pages19 = read_pdf(urls[1],path)

page18 = tokenize(pages18, 1)
page19 = tokenize(pages19, 1)

sents18 = list(page18.sents)
sents19 = list(page19.sents)

sents = []
for sent in sents18:
    print(sent)
    sents.append(sent.text + "*")

sents1 = []
for sent in sents19:
    sents.append(sent.text + "*")
difference(sents, sents1)

'''
class difflib.SequenceMatcher(isjunk=None, a='', b='', autojunk=True):
    SequenceMatcher(None, page18, page19).ratio()
 '''   

def difference(s1, s2):
    results = {'changed':[], 'unchanged': []}
    for sent in s1:
        if sent in s2:
            results['unchanged'].append(sent)
        else:
            results['changed'].append(sent)
    return results

difference(sents18, sents19)

t1 = 'Hello how are you. \n I am good.'
t2 = 'Hello how are you. \n I am not good.'

print(t1)
def differences(t1, t2):
    t1_split = t1.split('\n')
    t2_split = t2.split('\n')
    results = {'changed':[], 'unchanged': []}
    for para in t1_split:
        if para in t2_split:
            results['unchanged'].append(para)
        else:
            results['changed'].append(para)
    return results


differences(t1, t2)
