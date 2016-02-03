#!/usr/bin/env python

import ftplib
import os
import socket

HOST = 'ftp.rma.ac.be'
DIRFTP = '/outgoing/amuls'
RFILE = 'taal.sty'
SIZEBUF = 512
ftp = ""


# connect to the FTP server
def serverConnect():
    print 'in serverConnect'
    try:
        global ftp
        ftp = ftplib.FTP(HOST)
    except (socket.error, socket.gaierror, ftplib.error_perm), e:
        print "error = %s" % e
        print 'ERROR: cannot reach "%s"' % HOST
        return
    print '*** Connected to host "%s"' % HOST


# login to the server
def ftpLogin():
    print 'in ftpLogin'
    try:
        global ftp
        ftp.login()
    except ftplib.error_perm:
        print 'ERROR: cannot login anonymously'
        ftp.quit()
        return
    print '*** Logged in as "anonymous"'


# change directory
def ftpCD():
    print 'in ftpCD'
    try:
        ftp.cwd(DIRFTP)
    except ftplib.error_perm:
        print 'ERROR: cannot CD to "%s"' % DIRFTP
        ftp.quit()
        return
    print '*** Changed to "%s" folder' % DIRFTP


# download a file
def grabFile():
    print 'in grabFile'

    localfile = open(RFILE, 'wb')

    try:
        ftp.retrbinary('RETR ' + RFILE, localfile.write, SIZEBUF)
    except ftplib.error_perm:
        print 'ERROR: cannot read file "%s"' % RFILE
        os.unlink(RFILE)
    else:
        print '*** Downloaded "%s" to CWD' % RFILE
    localfile.close()


# upload a file
def placeFile():
    print 'in placeFile'
    filename = 'exampleFile.txt'
    ftp.storbinary('STOR '+filename, open(filename, 'rb'))
    ftp.quit()


# main starts here
if __name__ == "__main__":
    serverConnect()
    ftpLogin()
    ftpCD()
    grabFile()
    ftp.quit()
