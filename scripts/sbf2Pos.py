#!/usr/bin/env python

import sys
import getopt
import os
from pyproj import Proj
from SSN import sbf2stf
from Plot import plotPos

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

# get startup path
ospath = sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), "subfolder"))
print sys.argv[0], ospath


# print usage of script
def usage():
    """
    prints the usage of the script
    """
    sys.stderr.write('plotPos.py -f|--file=SBF-data-file -o|--overwrite -v|--verbose -h|--help\n')
    sys.stderr.write('where: -f|--file : specify filename of SBF data to convert\n')
    sys.stderr.write('       -o|--overwrite : overwrite converted files (default not)\n')
    sys.stderr.write('       -v|--verbose : enable verbosity\n')
    sys.stderr.write('       -h|--help : print this help message\n')


# treat the arguments passed
def treatCmdOpts(argv):
    """
    Treats the command line options

    Parameters:
      argv          the options (without argv[0])

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


if __name__ == "__main__":
    # print sys.argv
    treatCmdOpts(sys.argv[1:])                       # treat cmdline parameters

    # check whether the SBF datafile exists
    if not os.path.isfile(nameSBF):
        sys.stderr.write('SBF datafile %s does not exists. Exiting.\n' % nameSBF)
        sys.exit(E_FILE_NOT_EXIST)

    # execute the conversion sbf2stf needed
    SBF2STFOPTS = ['PVTGeodetic_2', 'DOP_2']     # options for conversion, ORDER IMPORTANT!!
    sbf2stfConverted = sbf2stf.runSBF2STF(nameSBF, SBF2STFOPTS, overwrite, verbose)
    # nameDataMeasSVID = 'testpos' + '.csv'
    # np.savetxt(nameDataMeasSVID, sbf2stfConverted)
    print "sbf2stfConverted = %s" % sbf2stfConverted
    # print 'SBF2STFOPTS = %s' % SBF2STFOPTS
    for option in SBF2STFOPTS:
        # print 'option = %s - %d' % (option, SBF2STFOPTS.index(option))
        if option == 'PVTGeodetic_2':
            # read the MeasEpoch data into a numpy array
            dataPOS = sbf2stf.readGEODPosEpoch(sbf2stfConverted[SBF2STFOPTS.index(option)], verbose)

            print 'dataPOS = %s (%d)' % (dataPOS, len(dataPOS))
            print "dataPOS['GEOD_TOW'] = %s (%d)\n" % (dataPOS['GEOD_TOW'], len(dataPOS['GEOD_TOW']))

        elif option == 'DOP_2':
            # read the MeasExtra data into numpy array
            dataDOP = sbf2stf.readDOPEpoch(sbf2stfConverted[SBF2STFOPTS.index(option)], verbose)

            print 'dataDOP = %s (%d)' % (dataDOP, len(dataDOP))
            print "dataDOP['DOP_TOW'] = %s (%d)\n" % (dataDOP['DOP_TOW'], len(dataDOP['DOP_TOW']))

        else:
            print '  wrong option %s given.' % option
            sys.exit(E_WRONG_OPTION)

    index = sbf2stf.findNanValues(dataPOS['GEOD_Latitude'])
    print "index: ", index[0][:]
    if len(index) < 0:
        print "NO POSITION CALCULATED"
    else:
        dataGEODPOSValid = dataPOS[index]
        dataDOPValid = dataDOP[index]
        myProj = Proj("+proj=utm +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
        print "TYPE", type(dataGEODPOSValid)
        east, north = myProj(rad2deg(dataGEODPOSValid['GEOD_Longitude']), rad2deg(dataGEODPOSValid['GEOD_Latitude']))
        # print "MEAN LONG", np.mean(dataGEODPOSValid['GEOD_Longitude'])
        # print "MEAN LAT", np.mean(dataGEODPOSValid['GEOD_Latitude'])
        # print "MEAN HEIGHT", np.mean(dataGEODPOSValid['GEOD_Height'])
        dataGEODPOSValid['GEOD_Longitude'] = east
        dataGEODPOSValid['GEOD_Latitude'] = north
        plotPos.plotGEOD(dataGEODPOSValid, dataDOPValid)

    # check whether the same signaltypes are on corresponsing lines after sorting
    # if not sbf2stf.verifySignalTypeOrder(dataMeas['MEAS_SIGNALTYPE'], dataExtra['EXTRA_SIGNALTYPE'], dataMeas['MEAS_TOW'], verbose):
    #     sys.exit(E_SIGNALTYPE_MISMATCH)
    # DOP

    # colNames = ['WNC', 'TOW', 'MODE', '2D/3D', 'Error', 'NrSV', 'Latitude', 'Longitude',
    #             'Height', 'Vn', 'Ve', 'Vu', 'ClockBias', 'ClockDrift', 'ReferenceID', 'MeanCorrAge',
    #             'NrBases', 'Undulation', 'COG', 'Datum', 'TimeSystem', 'SignalInfo', 'WACorrInfo',
    #             'AlertFlag', 'AutoBase']
    # colFmt = '%d,%f,%d,%d,%d,%d,%f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d,%f,%f,%d,%d,%d,%d,%d,%d'
    # dtypeFmt = 'u2,f8,u1,u1,u1,u1,f8,f8,f8,f8,f8,f8,f8,f8,u2,u2,u2,f4,f4,u1,u1,u4,u1,u1,u1'
