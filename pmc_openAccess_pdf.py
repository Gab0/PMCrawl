#!/bin/python
import os
import csv
from ftplib import FTP
import urllib
import xmltodict
from multiprocessing import Process


list_file = {'package': 'file_list.csv',
             'standalone': 'oa_non_comm_use_pdf.csv'}

def checkFileList(CONN, list_file):
    W = os.path.isfile(list_file)

    if not W:
        URL = 'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_file_list.csv'
        print("Downloading file list [%s]..." % list_file)
        cmd = 'RETR pub/pmc/%s' % list_file
        CONN.retrbinary(cmd, blocksize=8192, callback=open(list_file, 'wb').write)

    else:
        print("File list Found!")

def locateArticleByRequest(ID):
    URL='https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id='
    url = URL+ID

    Q=urllib.request.urlopen(url)

    R=Q.read()
    R=xmltodict.parse(R)
    
    try:
        ADDR=R['OA']['records']['record']['link']['@href']
        ADDR=ADDR.split('.gov/')[1]
    except:
        return False

    return ADDR

def locateArticleByLocalFileList(ID, PMCmode):
    ChkFileList = open(list_file[PMCmode], 'r')
    ChkFileList=csv.reader(ChkFileList)
    ROW = ''
    for row in ChkFileList:
        if ID in row:
            ROW = row

    if not ROW:
        return False

    base_addr = 'pub/pmc/'
    ADDR = base_addr + ROW[0]
    return ADDR

def download(CONN, ID, PMCmode):
    ID = str(ID)
    ID = 'PMC'+ID if not 'PMC' in ID else ID

    ADDR = locateArticleByLocalFileList(ID, PMCmode)
    ADDR2 = locateArticleByRequest(ID)

    #print(ADDR, list_file)
    #print(ADDR2)

    if ADDR:
        print('downloading...'+str(ROW))
        local_filename = ADDR.split('/')[-1]
        cmd = 'RETR %s' % ADDR
        CONN.retrbinary(cmd, blocksize=8192, callback=open(local_filename, 'wb').write)
    else:
        print('ARTICLE NOT FOUND!')
        #if PMCmode=='standalone': #try package, possible to find.
        #    download(CONN, ID, 'package')
                     
def retrieveArticle(ID, PMCmode='standalone'):
    assert(PMCmode in list_file.keys())
    HOST = 'ftp.ncbi.nlm.nih.gov'
    CONN=FTP(HOST)
    CONN.login()
    file_list = list_file[PMCmode]
    checkFileList(CONN, file_list)
    if type(ID) == list:
        procs=[]
        for _ID in ID:
            procs.append(Process(target=download, args=[CONN, _ID, PMCmode]))
    else:
        download(CONN, ID, PMCmode)


