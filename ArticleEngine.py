#!/bin/python

from entrez import getArticleInfo
import collections
import textwrap
import webbrowser
from multiprocessing import Process, Queue
import sys

def limitTextWidth(Words, Span=72):
    return textwrap.fill(Words, Span, subsequent_indent='  ')

def showAbstract(AbstractList):

    AbstractList += ["\nEND OF ABSTRACT;\n"]

    for A in AbstractList:
        if type(A) == list:
            print(A)
        print(limitTextWidth(A))
        print()
        q=input()

def serialRead(ArticleBank, COMM=None):
    baseURL = 'https://www.ncbi.nlm.nih.gov/pubmed/?term='
    Finish = False
    A = -1
    while A < len(ArticleBank):
        A = 0 if A < 0 else A
        if (COMM and A==len(ArticleBank)-1) or \
           (COMM and not ArticleBank):
            print("Loading more Articles...")
            ArticleBank += COMM.recv()
            
        UID = ArticleBank[A]['uid']
        YEAR = ArticleBank[A]['year']
        REFCOUNT = ArticleBank[A]['refcount']
        URL = baseURL + UID

        VIEW = "%s\t\t\t\t%i/%i\n" % (UID, A+1, len(ArticleBank)) +\
               "\t\t%i\t\t\trefs: %s\n" % (YEAR, REFCOUNT) +\
               "%s\n" % limitTextWidth(ArticleBank[A]['title'])
        
        print(VIEW)
        if Finish:
            continue
        k=input()
        if 'v' in k:
            print("Opening article in browser;")
            webbrowser.open(URL)
        if 'n' in k:
            print("Opening article in browser - new tab;")
            webbrowser.open_new_tab(URL)
        if 'e' in k:
            Finish = True
        if 'a' in k:
            showAbstract(ArticleBank[A]['abstract'])
        if 'b' in k:
            A -= 2

        A+=1
        
def backgroundRenderingRead(ArticleList, options, PIPE):
    DIVISOR = 10
    for k in range(0, len(ArticleList), DIVISOR):
        BLOCK = evaluateArticles(ArticleList[ k:k+DIVISOR ], options, Verbose=False)
        PIPE.send(BLOCK)
        
                   
def parseAbstract(Abstract):
    #print("DEBUG Abstract is a %s.\n" % type(Abstract))


    if type(Abstract == str):
        Abstract = [Abstract]
    else:
        try:
            Abstract = [ Abstract[x] for x in Abstract.keys() ]
        except:
            pass
        
    if type(Abstract[0]) == list:
        Abstract = Abstract[0]
        try:
            Abstract = [ Entry['#text'] for Entry in Abstract ]
        except:
            print(Abstract)
    
    return Abstract


def evaluateArticles(RawArticles, options, Verbose=True):
    ArticleBank=[]
    ArticleQuantity = len(RawArticles)
    N=0
    for Article in RawArticles:
        IDBase = Article['PubmedData']['ArticleIdList']
        ENTRY = IDBase[0]
        UID = str(ENTRY)
        try:
            ABSTRACT = Article['MedlineCitation']['Article']['Abstract']['AbstractText']
        except:
            print("Failed to read Abstract.")
            ABSTRACT = []
            pass

        try:
            ArticleData = getArticleInfo(UID)
        except:
            print(sys.exc_info()[0])
            raise
            continue

        ArticleData['abstract'] = ABSTRACT
                
        N+=1
        if Verbose:
            print("%.2f%%" % (N/ArticleQuantity*100))
        
        if options.Recent and ArticleData['year'] < options.Recent:
            continue
        if options.Relevance and ArticleData['refcount'] < options.Relevance:
            continue


        ArticleBank.append(ArticleData)

    return ArticleBank
