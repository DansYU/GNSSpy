#!/usr/bin/env python

import sys
import os
import ftplib
import socket
from subprocess import call

def getSP3(GPS_WEEK, GPS_DATE):
    # Defining variables en directories
    home = os.path.expanduser("~")
    IGSURL = 'cddis.gsfc.nasa.gov'
    # GPS_WEEK = 1841
    # GPS_DATE = 18411
    MGEX = 'gnss/products/mgex/' + str(GPS_WEEK) + '/'
    FILE = 'com' + str(GPS_DATE) + '.sp3.Z'
    DIR = home + '/GNSSpy/SSN/data/IGS/'
    DEST = DIR + FILE
    if not os.path.exists(DIR):
        os.mkdir(DIR)
    print 'MGEX', MGEX

    # Connecting to FTP
    if not os.path.exists(DEST[:-2]):
        try:
            f = ftplib.FTP(IGSURL)
            f.login()
            SUCCES = 1
        except (socket.error, socket.gaierror), e:
            print 'Failed to connect to %s' % IGSURL
            SUCCES = 0
            return
        print 'Connected to %s' % IGSURL

        # Travelling to directory
        if SUCCES == 1:
            try:
                f.cwd(MGEX)
            except ftplib.error_perm:
                print 'Could not reach %s' % MGEX
                f.quit()
                SUCCES = 0
                return
            print '%s reached' % MGEX

        # Downloading file
        if SUCCES == 1:
            try:
                f.retrbinary('RETR %s' % FILE, open(DEST, 'wb').write)
            except ftplib.error_perm:
                print 'ERROR: cannot read file "%s"' % FILE
                os.unlink(FILE)
            else:
                print 'Downloaded to %s' % DEST
            f.quit()

        # Decompressing Z file
        try:
            call(["uncompress", "-f", DEST])
        except:
            print 'Decompressing error'

        return DEST[:-2]
    else:
        print '%s already downloaded and uncompressed' % FILE
        return DEST[:-2]
