from requests_html import HTMLSession
import requests

from bs4 import BeautifulSoup

import os
import pathlib

import pandas as pd

from tqdm import tqdm
import openpyxl

import spacy

from spacy.matcher import Matcher
from spacy.tokens import Span 

import networkx as nx

import matplotlib.pyplot as plt

nlp = spacy.load("en_core_web_md")

script_dir = os.path.dirname(__file__) # <-- absolute dir the script is in

def check_if_in_list_of_dict(dict, value):
    """Check if given value exists in list of dictionaries """
    for elem in dict:
        if value in elem.values():
            return True
    return False

# Extracting article links
def scrapeArticlesList():
    session = HTMLSession()

    url = 'https://english.onlinekhabar.com/'

    r = session.get(url)

    r.html.render(sleep=1, scrolldown=1)

    articles = r.html.find('.ok-post-contents')

    newsList = []

    for item in articles:
        try:
            newsItem = item.find('h2', first=True)
            newsArticle = {
                'title' : newsItem.text,
                'link' : newsItem.absolute_links
            }
            if not check_if_in_list_of_dict(newsList, newsItem.text):
                newsList.append(newsArticle)
        except:
            pass

    return newsList

# Writing articles to text files
def scrapeArticleText(newsList):

    counter = 1
    rowsToWrite = []

    for news in tqdm(newsList):

        newsTitle = news['title']
        newsLink = news['link']

        formatted_newsLink = list(newsLink)[0]

        pathlib.Path(script_dir + "/Articles").mkdir(parents=True, exist_ok=True)

        rel_path = f'Articles\{counter}.txt'
        abs_file_path = os.path.join(script_dir, rel_path)

        row = [counter, newsTitle]

        with open(abs_file_path, 'w', encoding='utf-8') as f:

            r = requests.get(formatted_newsLink)
            soup = BeautifulSoup(r.content, 'html.parser')
            
            title = soup.find("title").text.strip()

            articleDiv = ["post-content-wrap"]
            article = soup.find("div", {"class" : articleDiv})
            text = "\n".join([p.text.strip() for p in article.find_all("p")])
            
            f.write(title + "\n")
            f.write(text)

        rowsToWrite.append(row)  

        counter += 1

    return rowsToWrite

# Create Article Index Excel File
def writeToExcelFile(rowsToWrite):
    
    columns = ['File Name', 'Article Title']

    result_df = pd.DataFrame(rowsToWrite, columns = columns)

    rel_path = "Articles\Article Index.xlsx"
    abs_file_path = os.path.join(script_dir, rel_path)
    
    path = abs_file_path

    result_df.to_excel(path, index = False)

def get_entities_relation(sent):
    ## chunk 1
    ent1 = ""
    ent2 = ""

    prv_tok_dep = ""    # dependency tag of previous token in the sentence
    prv_tok_text = ""   # previous token in the sentence

    prefix = ""
    modifier = ""

    #############################################################
    
    doc = nlp(sent)

    for tok in nlp(sent):
 
        ## chunk 2
        # if token is a punctuation mark then move on to the next token
        if tok.dep_ != "punct":
        # check: token is a compound word or not
            if tok.dep_ == "compound":
                prefix = tok.text
                # if the previous word was also a 'compound' then add the current word to it
                if prv_tok_dep == "compound":
                    prefix = prv_tok_text + " "+ tok.text
            
            # check: token is a modifier or not
            if tok.dep_.endswith("mod") == True:
                modifier = tok.text
                # if the previous word was also a 'compound' then add the current word to it
                if prv_tok_dep == "compound":
                    modifier = prv_tok_text + " "+ tok.text
        
        ## chunk 3
        if tok.dep_.find("subj") == True and tok.pos_ == "PROPN":
            str1 = [modifier, prefix, tok.text]
            ent1 = ' '.join(filter(None, str1))
            prefix = ""
            modifier = ""
            prv_tok_dep = ""
            prv_tok_text = ""      

        ## chunk 4
        if tok.dep_.find("obj") == True:
            str2 = [modifier, prefix, tok.text]
            ent2 = ' '.join(filter(None, str2))
            prefix = ""
            modifier = ""
            prv_tok_dep = ""
            prv_tok_text = ""   
            
        ## chunk 5  
        # update variables
        prv_tok_dep = tok.dep_
        prv_tok_text = tok.text
    #############################################################

        # Matcher class object 
        matcher = Matcher(nlp.vocab)

        #define the pattern 
        pattern = [{'DEP':'ROOT'}, 
                    {'DEP':'prep','OP':"?"},
                    {'DEP':'agent','OP':"?"},  
                    {'POS':'ADJ','OP':"?"}] 

        matcher.add("Relation", [pattern]) 

        matches = matcher(doc)
        k = len(matches) - 1

        span = doc[matches[k][1]:matches[k][2]] 

    relation = span.text

    entity_relation = [ent1.strip(), ent2.strip(), relation]
    
    check_empty = '' in entity_relation

    if check_empty:
        pass
    else:
        return entity_relation

# Text processing
def textProcessing(numOfItems):

    entity_relation_list = []

    for i in tqdm(range(1, numOfItems + 1)):
    #for i in tqdm(range(1, len(rowsToWrite)+1):
        fileName = str(i) + ".txt"


        rel_path = 'Articles\\' + fileName
        abs_file_path = os.path.join(script_dir, rel_path)
        with open(abs_file_path, 'r', encoding='utf-8') as f:
            text = f.read()

            doc = nlp(text)

            for sent in doc.sents:
                entity_relation = get_entities_relation(sent.text)
            
                if entity_relation == None:
                    pass
                else:
                    entity_relation_list.append(entity_relation)

    return entity_relation_list

def createGraph(entity_relation_list):
    # extract subject
    source = [i[0] for i in entity_relation_list]

    # extract object
    target = [i[1] for i in entity_relation_list]

    relations = [i[2] for i in entity_relation_list]

    kg_df = pd.DataFrame({'source':source, 'target':target, 'edge':relations})

    # create a directed-graph from a dataframe
    G = nx.from_pandas_edgelist(kg_df, "source", "target", 
                            edge_attr=True, create_using=nx.MultiDiGraph())

    plt.figure(figsize=(12,12))

    pos = nx.spring_layout(G)

    e_labels = {(kg_df.source[i], kg_df.target[i]): kg_df.edge[i]
            for i in range(len(kg_df['edge']))}

    nx.draw_networkx_edge_labels(G, pos, edge_labels= e_labels)
    nx.draw(G, pos = pos,with_labels=True)

    nx.draw(G, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos = pos)

    plt.show()

    return G

# Write graph file

def writeGraph(G):
    import pickle

    with open('graph.gpickle', 'wb') as f:
        pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)


print("Initiating web scraping")
newsList = scrapeArticlesList()

print("Saving articles")
rowsToWrite = scrapeArticleText(newsList)

print("Creating article index file")
writeToExcelFile(rowsToWrite)

print("Starting text processing")
entity_relation_list = textProcessing(len(newsList))

print("Creating graph")
G = createGraph(entity_relation_list)

print("Saving graph")
writeGraph(G)