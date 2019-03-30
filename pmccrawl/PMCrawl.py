#!/bin/python
import sys


import os
from .ArticleEngine import evaluateArticles, serialRead, backgroundRenderingRead
from .entrez import pubmedSearch, pubmedFetchArticles, searchSNPs
# from snpedia import searchSnpedia
from .Options import options, args

from multiprocessing import Pipe, Process
import warnings # SUPRESS ALL WARNINGS; BAD IDEA;
warnings.filterwarnings("ignore")

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
    print("Found %i articles " % len(ArticleIDs) + \
          "including these polymorphisms on pubmed.")

    return ArticleIDs


def getArticleBank(searchFunction, keyword):
    ArticleIDs = searchFunction(keyword)
    if options.ShowList:
        print(', '.join(ArticleIDs))
    ArticleBank = pubmedFetchArticles(ArticleIDs) if ArticleIDs else []

    return ArticleBank


def getListFromBank(ArticleBank, attributeName):

    doiList = [a[attributeName]
               for a in ArticleBank
               if a[attributeName]]

    return doiList


def runSearch():
    #print(options)
    ArticleBank = []

    if options.SNP:
        for GeneName in options.SNP.split(' '):
            ArticleBank += getArticleBank(searchGene_dbSNPArticles, GeneName)
    elif options.snpedia:
        ArticleBank += getArticleBank(searchSnpedia, options.snpedia)

    else:
        if not options.PubmedSearch:
            # following subterfuge is questionable.
            if len(sys.argv) > 1:
                options.PubmedSearch = sys.argv[1]
            else:
                exit("No query provided.")
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
        # USELESS?
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

            # BUILD LISTS FROM SEARCH RESULTS;
            if options.makeDoiList:
                print("Writing DOI list.")
                doiList = getListFromBank(ArticleBank, "DOI")
                with open('doilist.txt', 'w') as outputFile:
                    outputFile.write('\n'.join(doiList))

            if options.makePMCIDList:
                pmidpath = "pmcidlist.txt"
                print("Writing PMID list to %s" % os.path.abspath(pmidpath))
                pmcidList = getListFromBank(ArticleBank, "PMC")
                with open(pmidpath, 'w') as outputFile:
                    outputFile.write('\n'.join(pmcidList))

            if options.saveAbstractBatch:
                def normalizeAbstract(abstract):
                    if type(abstract) == list:
                        abstract = '\n'.join(abstract)
                    return abstract
                abstractBatch = [normalizeAbstract(a['abstract'])
                                 for a in ArticleBank if a['abstract']]

                with open('abstractBatch.txt', 'w') as outputFile:
                    outputFile.write('\n\n'.join(abstractBatch))

            if options.blacklist:
                blacklist = open(options.blacklist).read().split('\n')

                bArticleBank = [a for a in ArticleBank
                                if a['uid'] not in blacklist]
                nb_blacklisted = len(ArticleBank) - len(bArticleBank)
                ArticleBank = bArticleBank
                print("Blacklist blocks %i articles." % nb_blacklisted)

            serialRead(ArticleBank)

    elif not options.Info:
        print("No articles found.")
