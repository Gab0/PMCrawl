#!/bin/python

import optparse
print("uaehaeuh")
parser = optparse.OptionParser()
parser.add_option('-n', '--snp', dest='SNP', default='')
parser.add_option('-S','--search', dest='Search', action='store_true', default=False)
parser.add_option('-m','--pubmed', dest='PubmedSearch', default='')
parser.add_option('-p', '--snpedia', dest='snpedia', help='Search for articles on snpedia', default='')

parser.add_option('-i', '--info', dest='Info', default='', help='Print citation info only;')

parser.add_option('--refreshList', dest='RefresList', action='store_true', default=False)

parser.add_option('-r', '--recent', dest='Recent', default=None, type="int")
parser.add_option('-R', '--relevance', dest='Relevance', default=None, type="int")
parser.add_option('-F', '--filter', dest='Filter', default='')
parser.add_option('-a', '--async', dest='ASYNC', action='store_true',
                  default=False, help='Run in async mode.')
parser.add_option('-l', dest='ShowList', action='store_true', default=False, help='show list of results as csv PMIDs')

options, args = parser.parse_args()
