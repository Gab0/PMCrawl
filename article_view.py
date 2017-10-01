#!/bin/python

import webbrowser
import sys
import optparse
import os
import re
import collections

from Bio import Entrez
import xmltodict

from ArticleEngine import evaluateArticles, serialRead, backgroundRenderingRead
from entrez import pubmedSearch, pubmedFetchArticles, searchSNPs
from snpedia import searchSnpedia

import warnings # SUPRESS ALL WARNINGS; BAD IDEA;
warnings.filterwarnings("ignore")

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from multiprocessing import Process, Pipe
parser = optparse.OptionParser()
parser.add_option('-n', '--snp', dest='SNP', default='')
parser.add_option('-S','--search', dest='Search', action='store_true', default=False)
parser.add_option('-m','--pubmed', dest='PubmedSearch', default='')
parser.add_option('-p', '--snpedia', dest='snpedia', help='Search for articles on snpedia')

parser.add_option('-i', '--info', dest='Info', default='', help='Print citation info only;')

parser.add_option('--refreshList', dest='RefresList', action='store_true', default=False)

parser.add_option('-r', '--recent', dest='Recent', default=None, type="int")
parser.add_option('-R', '--relevance', dest='Relevance', default=None, type="int")

parser.add_option('-a', '--async', dest='ASYNC', action='store_true',
                  default=False, help='Run in async mode.')
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
    
    ArticleBank = pubmedFetchArticles(ArticleIDs) if ArticleIDs else []
    
    return ArticleBank

splitTerm = lambda TERM: TERM.split(' ')

if __name__ == '__main__':
    options, args = parser.parse_args()

    ArticleBank = []
    if options.SNP:
        for GeneName in splitTerm(options.SNP):
            ArticleBank += getArticleBank(searchGene_dbSNPArticles, GeneName)
    if options.PubmedSearch:
        ArticleBank += getArticleBank(pubmedSearch, options.PubmedSearch)
    if options.snpedia:
        ArticleBank += getArticleBank(searchSnpedia, options.snpedia)

    if options.Info:
        ArticleInfo = getArticleBank(pubmedSearch, options.Info)
        ArticleInfo = evaluateArticles(ArticleInfo,options)[0]
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
            serialRead(ArticleBank)
    elif not options.Info:
        print("No articles found.")
