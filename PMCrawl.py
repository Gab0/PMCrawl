#!/bin/python

import webbrowser
import sys
import os
import re
import collections

from Bio import Entrez
import xmltodict

from ArticleEngine import evaluateArticles, serialRead, backgroundRenderingRead
from entrez import pubmedSearch, pubmedFetchArticles, searchSNPs
#from snpedia import searchSnpedia
from Options import options, args

import warnings # SUPRESS ALL WARNINGS; BAD IDEA;
warnings.filterwarnings("ignore")

# why?
# os.chdir(os.path.dirname(os.path.realpath(__file__)))

from multiprocessing import Process, Pipe

'''
Firefox options to properly open links in current tab:
## about:config ##
browser.link.open_newwindow=1
browser.link.open_newwindow.restriction=0
'''


def searchGene_dbSNPArticles(GeneName):
    Query = "%s AND human[Organism]" % GeneName
    print("Searching for <%s> @ dbSNP." % Query)
    RSIDs = searchSNPs(Query)
    if not RSIDs:
        print("Polymorphism list not found.")
        return None
    print("Found %i polymorphisms for %s." % (len(RSIDs), GeneName))
    SearchTerm = ' OR '.join(RSIDs)

    ArticleIDs = pubmedSearch(SearchTerm)
    if not ArticleIDs:
        print("Polymorphism list results zero on pubmed search.")
        return []
    print("Found %i articles " % len(ArticleIDs) +\
    "including these polymorphisms on pubmed.")

    return ArticleIDs


def getArticleBank(searchFunction, keyword):
    ArticleIDs = searchFunction(keyword)
    if options.ShowList:
        print(', '.join(ArticleIDs))
    ArticleBank = pubmedFetchArticles(ArticleIDs) if ArticleIDs else []
    
    return ArticleBank

splitTerm = lambda TERM: TERM.split(' ')

if __name__ == '__main__':
    #print(options)
    ArticleBank = []

    if options.SNP:
        for GeneName in splitTerm(options.SNP):
            ArticleBank += getArticleBank(searchGene_dbSNPArticles, GeneName)
    elif options.snpedia:
        ArticleBank += getArticleBank(searchSnpedia, options.snpedia)

    else:
        if not options.PubmedSearch:
            # following subterfuge is questionable.
            options.PubmedSearch = sys.argv[1]
        ArticleBank += getArticleBank(pubmedSearch, options.PubmedSearch)

    if options.Info:
        ArticleInfo = getArticleBank(pubmedSearch, options.Info)
        ArticleInfo = evaluateArticles(ArticleInfo, options)[0]
        print("%s\n%s\n%s %s [%s]" % (ArticleInfo['authors'],
                                      ArticleInfo['title'],
                                      ArticleInfo['journal'],
                                      ArticleInfo['year'],
                                      ArticleInfo['uid']))

    if ArticleBank:
        if options.ASYNC:
            send, receive = Pipe()
            S = Process(target=backgroundRenderingRead,
                        args=(ArticleBank, options, send))
            S.start()
            print("Starting async serial read on %i articles." % len(ArticleBank))
            serialRead([], COMM=receive)
        else:
            print("Starting serial read on %i articles." % len(ArticleBank))
            ArticleBank = evaluateArticles(ArticleBank, options)
            if options.makeDoiList:
                doiList = [a['DOI'] for a in ArticleBank if a['DOI']]
                print("Writing DOI list.")
                with open('doilist.txt', 'w') as outputFile:
                    outputFile.write('\n'.join(doiList))

            if options.saveAbstractBatch:
                def normalizeAbstract(abstract):
                    if type(abstract) == list:
                        abstract = '\n'.join(abstract)
                    return abstract
                abstractBatch = [normalizeAbstract(a['abstract']) for a in ArticleBank if a['abstract']]

                with open('abstractBatch.txt', 'w') as outputFile:
                    outputFile.write('\n\n'.join(abstractBatch))
            serialRead(ArticleBank)

    elif not options.Info:
        print("No articles found.")
