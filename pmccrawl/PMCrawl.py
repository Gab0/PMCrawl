#!/bin/python
import sys


import os
from .ArticleEngine import evaluateArticles
from .ArticleEngine import serialRead, backgroundRenderingRead
from .entrez import pubmedSearch, pubmedFetchArticles, searchSNPs

# from .snpedia import searchSnpedia

from .Options import options

from multiprocessing import Pipe, Process
# SUPRESS ALL WARNINGS; BAD IDEA;
import warnings
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
    print("Found %i articles " % len(ArticleIDs) +
          "including these polymorphisms on pubmed.")

    return ArticleIDs


def getArticleBank(searchFunction, keyword):
    ArticleIDs = searchFunction(keyword)
    ArticleBank = pubmedFetchArticles(ArticleIDs) if ArticleIDs else []

    return ArticleBank


def getListFromBank(ArticleBank, attributeNames):
    doiList = []
    for a in ArticleBank:
        for attr in attributeNames:
            if a[attr]:
                doiList.append(a[attr])
                break

    return doiList


def parseQuery(options):
    if options.allKeywords:
        words = options.PubmedSearch.split(" ")
        Query = " AND ".join(words)

    else:
        Query = options.PubmedSearch

    return Query


def runSearch():
    ArticleBank = []

    if options.SNP:
        for GeneName in options.SNP.split(' '):
            ArticleBank += getArticleBank(searchGene_dbSNPArticles, GeneName)
    elif options.snpedia:
        print("DEPRECATED.")
        exit(1)
        # ArticleBank += getArticleBank(searchSnpedia, options.snpedia)

    else:
        if not options.PubmedSearch:
            # following subterfuge is questionable.
            PseudoSearch = " ".join(sys.argv[1:])
            if '-' not in PseudoSearch:
                options.PubmedSearch = PseudoSearch
            else:
                exit("No query provided.")

        PubmedQuery = parseQuery(options)
        ArticleBank += getArticleBank(pubmedSearch, PubmedQuery)

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
        # if options.ASYNC:
        if False:
            send, receive = Pipe()
            S = Process(target=backgroundRenderingRead,
                        args=(ArticleBank, options, send))
            S.start()
            print("Starting async serial read on %i articles." %
                  len(ArticleBank))
            serialRead([], COMM=receive)
        else:
            print("Starting serial read on %i articles." % len(ArticleBank))
            ArticleBank = evaluateArticles(ArticleBank, options)

            # BUILD LISTS FROM SEARCH RESULTS;
            ListIdentifiers = {
                "d": "DOI",
                "p": "PMC",
                "i": "uid"
            }

            if options.ListPath:
                Identifiers = [
                    ListIdentifiers[idt]
                    for idt in options.ListAttributes
                    if idt in ListIdentifiers.keys()
                ]
                print("Writing article identifier list: %s." %
                      "/".join(Identifiers))
                articleIdentifierList = getListFromBank(ArticleBank, Identifiers)
                with open(options.ListPath, 'w') as outputFile:
                    outputFile.write('\n'.join(articleIdentifierList))

                print("\tPMID rate: %.2f%%" %
                      (100 * len(articleIdentifierList) / len(ArticleBank)))

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

            if not options.searchAndExit:
                serialRead(ArticleBank)

    elif not options.Info:
        print("No articles found.")
