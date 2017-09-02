#!/bin/python
import os
import csv
from ftplib import FTP

list_file = {'package': 'oa_comm_use_file_list.csv',
             'standalone': 'oa_non_comm_use_pdf.csv'}

HOST = 'ftp.ncbi.nlm.nih.gov'

def checkFileList(CONN, list_file):
    W = os.path.isfile(list_file)

    if not W:
        URL = 'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_file_list.csv'
        print("Downloading file list [%s]..." % list_file)
        cmd = 'RETR pub/pmc/%s' % list_file
        CONN.retrbinary(cmd, blocksize=8192, callback=open(list_file, 'wb').write)

    else:
        print("File list Found!")
        

def save(data):
    Q=open("PDF.pdf", 'wb')
    Q.write(data)
    

def retrieveArticle(ID, list_file):

    ID = str(ID)
    ID = 'PMC'+ID if not 'PMC' in ID else ID
    file_list = open(list_file, 'r')
    FileList=csv.reader(file_list)
    ROW = 'NOT FOUND!'
    for row in FileList:
        if ID in row:
            ROW = row
            print(ROW)


    print(ROW)
    base_addr = 'pub/pmc/'
    ADDR = base_addr + ROW[0]

    cmd = 'RETR %s' % ADDR
    CONN.retrbinary(cmd, blocksize=8192, callback=open(ADDR.split('/')[-1], 'wb').write)


CONN=FTP(HOST)
CONN.login()
file_list = list_file['standalone']
checkFileList(CONN, file_list)
retrieveArticle(4516033, file_list)
