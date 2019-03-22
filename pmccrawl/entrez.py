 #!/bin/python
from Bio import Entrez
from urllib.error import HTTPError
import xmltodict
import json


# modify this;
Entrez.email = "anon@hotmail.com"


def parsedEntrezSearch(**kwargs):

    RESULT = Entrez.esearch(**kwargs)
    RESULT = Entrez.read(RESULT)
    try:
        ResultList = RESULT['IdList']
    except Exception as e:
        print(ResultList)
        raise
        return []

    if ResultList:
        return ResultList
    return []


def extractOptionalFeature(Info, keyList):

    for k in keyList:
        try:
            Info = Info[k]
        except KeyError as e:
            return None

    return Info


def getArticleInfo(UIDs):
    ArticleInfos = Entrez.esummary(db='pubmed', id=",".join(UIDs))
    ArticleInfos = Entrez.read(ArticleInfos)
    # some articles got no DOI;

    batchArticleData = []
    for INFO in ArticleInfos:
        print(json.dumps(INFO, indent=2))

        ArticleData = {
            'title': INFO['Title'],
            'uid': INFO['Id'],
            'year': int(INFO['SO'][:4]),
            'refcount': INFO['PmcRefCount'],
            'journal': INFO['FullJournalName'],
            'authors': '; '.join(INFO['AuthorList']),
            'DOI': extractOptionalFeature(INFO, ["DOI"]),
            'PMC': extractOptionalFeature(INFO, ["ArticleIds", "pmc"]),
            # attributes not found on esummary;
            'abstract': [],
            'keywords': ''
            }
        batchArticleData.append(ArticleData)

    return batchArticleData


def searchSNPs(Query):
    SNP_LIST = parsedEntrezSearch(db='snp', term=Query, retmax=25000)
    if not SNP_LIST:
        return []
    RawRSIDs = Entrez.efetch(db='snp', id=SNP_LIST, rettype='xml').read()
    # dbSNP XML is different. Entrez.read() won't parse;
    P=xmltodict.parse(RawRSIDs)
    ResultList = P['ExchangeSet']['Rs']
    #print(ResultList)
    RSIDs = [ 'rs' + R['@rsId'] for R in ResultList ]
    #print(RSIDs)

    return RSIDs

def pubmedSearch(SearchTerm):
    PUBMED_IDLIST = parsedEntrezSearch(db='pubmed',
                                       term=SearchTerm, retmax=25000)

    return PUBMED_IDLIST

def pubmedFetchArticles(PUBMED_IDLIST):
    RawArticles = Entrez.efetch(db='pubmed', id=PUBMED_IDLIST,
                                retmax=25000, rettype='xml')

    RawArticles = Entrez.read(RawArticles)

    if 'PubmedArticle' in RawArticles.keys():
        RawArticles = RawArticles['PubmedArticle']
    else:
        print(RawArticles.keys())
        raise
        return None
    return RawArticles
