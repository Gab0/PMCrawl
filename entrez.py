 #!/bin/python
from Bio import Entrez
from urllib.error import HTTPError
import xmltodict
Entrez.email = "gabriel_scf@hotmail.com"
def parsedEntrezSearch(**kwargs):

    RESULT = Entrez.esearch(**kwargs)
    RESULT = Entrez.read(RESULT)
    try:
        ResultList = RESULT['IdList']
    except:
        print(ResultList)
        raise
        return []
    
    
    if ResultList:
        return ResultList
    return []

def getArticleInfo(UID):
    INFO = Entrez.esummary(db='pubmed', id=UID)
    INFO = Entrez.read(INFO)[0]

    ArticleData = {'title': INFO['Title'],
                   'uid': INFO['Id'],
                   'abstract': '',
                   'year': int(INFO['SO'][:4]),
                   'refcount': INFO['PmcRefCount']
                   }
    
    return ArticleData

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
