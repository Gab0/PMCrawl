from wikitools import wiki, category, page, api
import re
import optparse
site = wiki.Wiki("http://bots.snpedia.com/api.php")                  # open snpedia
snps = category.Category(site, "Is_a_snp")
snpedia = []



def searchSnpedia(keywords):
    params = {'action': 'query',
              'list': 'search',
              'srlimit': 5000,
              'srwhat': 'text',
              'srsearch': keywords,
              'meta':'siteinfo',
              'siprop':'general'
}

    request = api.APIRequest(site, params)
    request = request.queryGen()
    for W in request:
        List = W['query']['search']

    ArticleIdBank = []
    print("Found %i SNP pages" % len(List))
    for w in range(len(List)):
        print(w)
        spage=page.Page(site, List[w]['title'])
        text=spage.getWikiText()
        links=spage.getLinks()
        
        if len(text) > 1:
            PageArticleIds =[] 
            for S in [r'{{PMID\|', r'{{PMC\|']:
                Data = list(re.finditer(S, text))
                L = [ m.end() for m in Data ]
                PageArticleIds += [text[ x:x+re.search(r"[^0-9]", text[x:]).span()[0] ] for x in L]
                #PageArticleIds += [text[ x:x+8] for x in L]
            print(PageArticleIds)
            ArticleIdBank += [x for x in PageArticleIds if x not in ArticleIdBank]

    return ArticleIdBank
