#!/bin/python

import optparse

parser = optparse.OptionParser()

# search source selection options;
parser.add_option('-n', '--snp', dest='SNP', default='')
parser.add_option('-S','--search', dest='Search', action='store_true', default=False)
parser.add_option('-m','--pubmed', dest='PubmedSearch', default='')
parser.add_option('-p', '--snpedia', dest='snpedia', help='Search for articles on snpedia', default='')



parser.add_option('--refreshList', dest='RefresList', action='store_true', default=False)

parser.add_option('-r', '--recent', dest='Recent', default=None, type="int")
parser.add_option('-R', '--relevance', dest='Relevance', default=None, type="int")
parser.add_option('-F', '--filter', dest='Filter', default='')
#parser.add_option('-a', '--async', dest='ASYNC', action='store_true',
#                  default=False, help='Run in async mode.')

# Output List Options;
parser.add_option('-l', dest='ListPath',
                  default="",
                  help="Selects the path to save the article list, enabling the article list writing.")

parser.add_option(
    '--la',
    dest='ListAttributes',
    default="p",
    help='Order of article attributes to be written in list.\n' +
    'This is a string of chars, if the first is missing' +
    ' it writes the second and so on. Set: <pdi> -> PMC, DOI, ID'
)


parser.add_option('-A', dest='saveAbstractBatch', action='store_true',
                  default=False, help='Save abstracts of all results on text file.')

parser.add_option("-b", dest='blacklist', default='')


# behavior options;
parser.add_option("-e", dest='searchAndExit', action='store_true')
parser.add_option('-i', '--info', dest='Info', default='', help='Print citation info only;')


# query options;
parser.add_option("--all", dest='allKeywords', action='store_true',
                  default=False,
                  help="Search all words, as in 'a AND b AND c'")
options, args = parser.parse_args()
