#!/usr/bin/env python


import sys
import os
import SP3ordinate
import getopt
import sbf2stf
import numpy as np
from scipy import cos, sin, sqrt
import time
import ssnConstants as mSSN
import gpstime
from Plot import plotRange


# exit codes
E_SUCCESS = 0
E_FILE_NOT_EXIST = 1
E_NOT_IN_PATH = 2
E_UNKNOWN_OPTION = 3
E_TIME_PASSED = 4
E_WRONG_OPTION = 5
E_SIGNALTYPE_MISMATCH = 6
E_FAILURE = 99

# global used vars
nameSBF = ''
overwrite = False
verbose = True

start = time.time()
# get startup path
ospath = sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), "subfolder"))
print sys.argv[0], ospath


# print usage of script
def usage():
    """
    prints the usage of the script
    """
    sys.stderr.write('sbf2Meas.py -f|--file=SBF-data-file -o|--overwrite -v|--verbose -h|--help\n')
    sys.stderr.write('where: -f|--file : specify filename of SBF data to convert\n')
    sys.stderr.write('       -o|--overwrite : overwrite converted files (default not)\n')
    sys.stderr.write('       -v|--verbose : enable verbosity\n')
    sys.stderr.write('       -h|--help : print this help message\n')


# treat the arguments passed
def treatCmdOpts(argv):
    """
    Treats the command line options

    Parameters:
      argv          the options (without argv[0]

    Sets the global variables according to the CLI args
    """

    global nameSBF
    global overwrite
    global verbose

    try:
        opts, args = getopt.getopt(argv, "hof:",
                                   ["file=", "overwrite", "help"])
    except getopt.GetoptError:
        usage()
        sys.exit(E_UNKNOWN_OPTION)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(E_SUCCESS)
        elif opt in ("-f", "--file"):
            nameSBF = arg
        elif opt in ("-o", "--overwrite"):
            overwrite = True
        elif opt in ("-v", "--verbose"):
            verbose = True


def format_timedelta(td):
    minutes, seconds = divmod(td.seconds + td.days * 86400, 60)
    # hours, minutes = divmod(minutes, 60)
    return float('{:02d}.{:02d}'.format(minutes, seconds))


def interpolate(COEF, TIME, Time):
    # Function will Interpolate the satellite position (which lagranges polynomial coefficients are calculated in COEF)
    # At the moment of Time.
    # There is need of the TIME array (array of observations) to determine which polynomial model has to be chosen.

    # Find the index where Time is the closest to the SP3 time
    XOUT = []
    YOUT = []
    ZOUT = []
    TIME2 = []
    for count in range(0, len(TIME)):
        TIME2.append(float(TIME[count].strftime("%s.%f")))
    # print TIME2
    TIME2 = np.asarray(TIME2)
    for counter in range(0, len(Time)):
        # DIFF = []
        DIFF = (np.abs(TIME2 - np.asarray(float(Time[counter].strftime("%s.%f"))))).argmin()
        # for count in range(0, len(TIME)):
        #   DIFF.append(np.abs(format_timedelta(TIME[count] - Time[counter])).argmin())
        #   DIFF = np.array(DIFF)
        #   DIFF = np.absolute(DIFF)

        # index = np.where(DIFF == DIFF.min()) # absolute index van closest hit.
        index = DIFF
        # print index
        T4 = index+4
        t = format_timedelta((Time[counter]-TIME[T4]))/(15.)
        # XOUT.append(np.polyval(np.flipud(COEF[index][:, 0]), t))
        # YOUT.append(np.polyval(np.flipud(COEF[index][:, 1]), t))
        # ZOUT.append(np.polyval(np.flipud(COEF[index][:, 2]), t))

        # This is faster:
        XOUT.append([COEF[index][0, 0]*t**0 + COEF[index][1, 0]*t**1 + COEF[index][2, 0]*t**2 + COEF[index][3, 0]*t**3 +
                    COEF[index][4, 0]*t**4 + COEF[index][5, 0]*t**5 + COEF[index][6, 0]*t**6 + COEF[index][7, 0]*t**7 +
                    COEF[index][8, 0]*t**8])

        YOUT.append([COEF[index][0, 1]*t**0 + COEF[index][1, 1]*t**1 + COEF[index][2, 1]*t**2 + COEF[index][3, 1]*t**3 +
                    COEF[index][4, 1]*t**4 + COEF[index][5, 1]*t**5 + COEF[index][6, 1]*t**6 + COEF[index][7, 1]*t**7 +
                    COEF[index][8, 1]*t**8])

        ZOUT.append([COEF[index][0, 2]*t**0 + COEF[index][1, 2]*t**1 + COEF[index][2, 2]*t**2 + COEF[index][3, 2]*t**3 +
                    COEF[index][4, 2]*t**4 + COEF[index][5, 2]*t**5 + COEF[index][6, 2]*t**6 + COEF[index][7, 2]*t**7 +
                    COEF[index][8, 2]*t**8])
    return [Time, XOUT, YOUT, ZOUT]
    # index = index[0][0]
    # print index
    # print DIFF
    # T4 = index + 4
    # T4 = index+4
    # index = index+1
    # index = index
    # print "Time:", Time
    # print "Time:", format_timedelta(Time-TIME[T4])
    # # print "delta ", format_timedelta((Time-TIME[T4]))
    # print COEF[index][4, 0]
    # t = format_timedelta((Time-TIME[T4]))/(15.)
    # t = -4
    # print t

    # # EVALUATE
    # XOUT = np.polyval(np.flipud(COEF[index][:, 0]), t)
    # YOUT = np.polyval(np.flipud(COEF[index][:, 1]), t)
    # ZOUT = np.polyval(np.flipud(COEF[index][:, 2]), t)

    # BACKUP
    # XOUT = [COEF[index][0, 0]*t**0 + COEF[index][1, 0]*t**1 + COEF[index][2, 0]*t**2 + COEF[index][3, 0]*t**3
    #         + COEF[index][4, 0]*t**4 + COEF[index][5, 0]*t**5 + COEF[index][6, 0]*t**6 + COEF[index][7, 0]*t**7
    #         + COEF[index][8, 0]*t**8]

    # YOUT = [COEF[index][0, 1]*t**0 + COEF[index][1, 1]*t**1 + COEF[index][2, 1]*t**2 + COEF[index][3, 1]*t**3
    #         + COEF[index][4, 1]*t**4 + COEF[index][5, 1]*t**5 + COEF[index][6, 1]*t**6 + COEF[index][7, 1]*t**7
    #         + COEF[index][8, 1]*t**8]

    # ZOUT = [COEF[index][0, 2]*t**0 + COEF[index][1, 2]*t**1 + COEF[index][2, 2]*t**2 + COEF[index][3, 2]*t**3
    #         + COEF[index][4, 2]*t**4 + COEF[index][5, 2]*t**5 + COEF[index][6, 2]*t**6 + COEF[index][7, 2]*t**7
    #         + COEF[index][8, 2]*t**8]
    # print "len X", len(XOUT)


def coord2range(COORDX, COORDY, COORDZ):
    lon = 0.08226562731
    lat = 0.88779580846
    alt = 114.56200
    # lon = 0.0860754828642  # rad
    # lat = 0.900026776971  # rad
    # alt = 28.0311583525  # meter
    X, Y, Z = geodetic2ecef(lat, lon, alt)
    georange = []
    for count in range(0, len(COORDX)):
        georange.append(sqrt((COORDX[count]-X)**2 + (COORDY[count]-Y)**2 + (COORDZ[count]-Z)**2))
    return georange


def geodetic2ecef(lat, lon, alt):
    # Constants defined by the World Geodetic System 1984 (WGS84)
    a = 6378.137
    b = 6356.7523142
    esq = 6.69437999014 * 0.001
    e1sq = 6.73949674228 * 0.001

    """Convert geodetic coordinates to ECEF."""
    xi = sqrt(1 - esq * sin(lat)*sin(lat))
    x = (a / xi + alt) * cos(lat) * cos(lon)
    y = (a / xi + alt) * cos(lat) * sin(lon)
    z = (a / xi * (1 - esq) + alt) * sin(lat)
    return x, y, z

if __name__ == "__main__":
    treatCmdOpts(sys.argv[1:])
    # check whether the SBF datafile exists
    if not os.path.isfile(nameSBF):
        sys.stderr.write('SBF datafile %s does not exists. Exiting.\n' % nameSBF)
        sys.exit(E_FILE_NOT_EXIST)

    # execute the conversion sbf2stf needed
    SBF2STFOPTS = ['MeasEpoch_2', 'MeasExtra_1']     # options for conversion, ORDER IMPORTANT!!
    sbf2stfConverted = sbf2stf.runSBF2STF(nameSBF, SBF2STFOPTS, overwrite, verbose)

    # print 'SBF2STFOPTS = %s' % SBF2STFOPTS
    for option in SBF2STFOPTS:
        # print 'option = %s - %d' % (option, SBF2STFOPTS.index(option))
        if option == 'MeasEpoch_2':
            # read the MeasEpoch data into a numpy array
            dataMeas = sbf2stf.readMeasEpoch(sbf2stfConverted[SBF2STFOPTS.index(option)], verbose)
        elif option == 'MeasExtra_1':
            # read the MeasExtra data into numpy array
            dataExtra = sbf2stf.readMeasExtra(sbf2stfConverted[SBF2STFOPTS.index(option)], verbose)
        else:
            print '  wrong option %s given.' % option
            sys.exit(E_WRONG_OPTION)

    # check whether the same signaltypes are on corresponsing lines after sorting
    if not sbf2stf.verifySignalTypeOrder(dataMeas['MEAS_SIGNALTYPE'], dataExtra['EXTRA_SIGNALTYPE'], dataMeas['MEAS_TOW'], verbose):
        sys.exit(E_SIGNALTYPE_MISMATCH)

    dataMeas['MEAS_CODE'] = sbf2stf.removeSmoothing(dataMeas['MEAS_CODE'], dataExtra['EXTRA_SMOOTHINGCORR'], dataExtra['EXTRA_MPCORR'])
    # print 'rawPR = %s\n' % dataMeas['MEAS_CODE']

    # find list of SVIDs observed
    SVIDs = sbf2stf.observedSatellites(dataMeas['MEAS_SVID'], verbose)

    signalTypes = sbf2stf.observedSignalTypes(dataMeas['MEAS_SIGNALTYPE'], verbose)
    # print "signalTypes %s" % signalTypes
    indexSignalType = []
    dataMeasSignalType = []

    for SVID in SVIDs:
        WEEK = dataMeas['MEAS_WNC'][0]
        DAY = gpstime.DOWFromWT(dataMeas['MEAS_TOW'][0])
        # print WEEK, DAY
        gnssSyst, gnssSystShort, gnssPRN = mSSN.svPRN(SVID)
        PRN = gnssSystShort + str(gnssPRN)
        COEF, sat, TIME = SP3ordinate.getlagrange(PRN, WEEK, DAY)
        georange = []
        pseudorange = []
        indexSVID = sbf2stf.indicesSatellite(SVID, dataMeas['MEAS_SVID'], verbose)
        dataMeasSVID = dataMeas[indexSVID]
        signalTypesSVID = sbf2stf.observedSignalTypes(dataMeasSVID['MEAS_SIGNALTYPE'], verbose)
        for index, signalType in enumerate(signalTypes):
            timeSVID = []
            indexSignalType = sbf2stf.indicesSignalType(signalType, dataMeasSVID['MEAS_SIGNALTYPE'], verbose)
            dataMeasSVIDSignalType = dataMeasSVID[indexSignalType]
            for count in range(0, len(dataMeasSVIDSignalType)):
                timeSVID.append(gpstime.UTCFromWT(float(dataMeasSVIDSignalType['MEAS_WNC'][count]), float(dataMeasSVIDSignalType['MEAS_TOW'][count])))
            # COORD = []
            print "Interpolating Values"
            # for count in range(0, len(timeSVID)):
            #   COORD.append(interpolate(COEF, TIME, timeSVID[count]))
            COORD = interpolate(COEF, TIME, timeSVID)
            georange.append([COORD[0], coord2range(COORD[1], COORD[2], COORD[3])])
            # print "COORD %s", COORD[0]
            pseudorange.append([timeSVID, dataMeasSVIDSignalType['MEAS_CODE']])
        if SVID == SVIDs[-1]:
            Last = 1
        else:
            Last = 0
        plotRange.plotRange(SVID, signalTypes, georange, pseudorange, Last)
    end = time.time()
    print "TIME: ", end-start
    # print "georange %s" % georange
    # Time = datetime.datetime(2015, 4, 20, 15, 0, 0)
    # # test: Time = datetime.datetime(2015, 4, 20, 15, 0, 0)
    # OUT = interpolate(COEF, TIME, Time)

    # print OUT
# result: print "-14636.606871 -18632.262465 -17744.662250"
