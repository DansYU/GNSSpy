#!/usr/bin/env python

import sys
import os
import numpy as np
import argparse
import matplotlib.pyplot as plt

from SSN import sbf2stf
from SSN import ssnConstants as mSSN
from Plot import plotLockTime

_author__ = 'amuls'


# exit codes
E_SUCCESS = 0
E_FILE_NOT_EXIST = 1
E_NOT_IN_PATH = 2
E_UNKNOWN_OPTION = 3
E_TIME_PASSED = 4
E_WRONG_OPTION = 5
E_SIGNALTYPE_MISMATCH = 6
E_DIR_NOT_EXIST = 7
E_FAILURE = 99

# # get startup path
# ospath = sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), "subfolder"))
# print(sys.argv[0], ospath)


# treat the arguments passed
def treatCmdOpts(argv):
    """
    treatCmdOpts treats the command line arguments using
    """
    helpTxt = os.path.basename(__file__) + ' investigates the lock times between signals for each SV '

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)
    parser.add_argument('-f', '--file', help='Name of SBF file', required=True)
    parser.add_argument('-d', '--dir', help='Directory of SBF file (defaults to .)', required=False, default='.')
    parser.add_argument('-o', '--overwrite', help='overwrite intermediate files (default False)', action='store_true', required=False)
    parser.add_argument('-v', '--verbose', help='displays interactive graphs and increase output verbosity (default False)', action='store_true', required=False)
    args = parser.parse_args()

    # show values
    print('SBFFile: %s' % args.file)
    print('dir = %s' % args.dir)
    print('verbose: %s' % args.verbose)
    print('overwrite: %s' % args.overwrite)

    return args.file, args.dir, args.overwrite, args.verbose


# main starts here
if __name__ == "__main__":
    np.set_printoptions(formatter={'float': '{: 0.3f}'.format})

    # treat the command line options
    nameSBF, dirSBF, overwrite, verbose = treatCmdOpts(sys.argv)

    # change to the directory dirSBF if it exists
    workDir = os.getcwd()
    if dirSBF is not '.':
        workDir = os.path.normpath(os.path.join(workDir, dirSBF))

    # print('workDir = %s' % workDir)
    if not os.path.exists(workDir):
        sys.stderr.write('Directory %s does not exists. Exiting.\n' % workDir)
        sys.exit(E_DIR_NOT_EXIST)
    else:
        if os.chdir(workDir) is False:
            sys.exit('Problem changing to directory %s. Exiting.\n' % workDir)

    # print('curDir = %s' % os.getcwd())
    # print('SBF = %s' % os.path.isfile(nameSBF))

    # check whether the SBF datafile exists
    if not os.path.isfile(nameSBF):
        sys.stderr.write('SBF datafile %s does not exists. Exiting.\n' % nameSBF)
        sys.exit(E_FILE_NOT_EXIST)

    # execute the conversion sbf2stf needed
    SBF2STFOPTS = ['MeasEpoch_2', 'MeasExtra_1']     # options for conversion, ORDER IMPORTANT!!
    sbf2stfConverted = sbf2stf.runSBF2STF(nameSBF, SBF2STFOPTS, overwrite, verbose)

    # print('SBF2STFOPTS = %s' % SBF2STFOPTS)
    for option in SBF2STFOPTS:
        # print('option = %s - %d' % (option, SBF2STFOPTS.index(option)))
        if option == 'MeasEpoch_2':
            # read the MeasEpoch data into a numpy array
            dataMeas = sbf2stf.readMeasEpoch(sbf2stfConverted[SBF2STFOPTS.index(option)], verbose)
        elif option == 'MeasExtra_1':
            # read the MeasExtra data into numpy array
            dataExtra = sbf2stf.readMeasExtra(sbf2stfConverted[SBF2STFOPTS.index(option)], verbose)
        else:
            print('  wrong option %s given.' % option)
            sys.exit(E_WRONG_OPTION)

    # check whether the same signaltypes are on corresponsing lines after sorting
    if not sbf2stf.verifySignalTypeOrder(dataMeas['MEAS_SIGNALTYPE'], dataExtra['EXTRA_SIGNALTYPE'], dataMeas['MEAS_TOW'], verbose):
        sys.exit(E_SIGNALTYPE_MISMATCH)

    # correct the smoothed PR Code and work with the raw PR
    dataMeas['MEAS_CODE'] = sbf2stf.removeSmoothing(dataMeas['MEAS_CODE'], dataExtra['EXTRA_SMOOTHINGCORR'], dataExtra['EXTRA_MPCORR'])
    # print('dataMeas['MEAS_CODE'] = %s\n' % dataMeas['MEAS_CODE'])

    # find list of SVIDs observed
    SVIDs = sbf2stf.observedSatellites(dataMeas['MEAS_SVID'], verbose)

    for SVID in SVIDs:
        print('=' * 50)
        gnssSyst, gnssSystShort, gnssPRN = mSSN.svPRN(SVID)
        print('SVID = %d - %s - %s%d' % (SVID, gnssSyst, gnssSystShort, gnssPRN))

        indexSVID = sbf2stf.indicesSatellite(SVID, dataMeas['MEAS_SVID'], verbose)
        dataMeasSVID = dataMeas[indexSVID]
        print("indexSVID = %s" % indexSVID)

        # store temporaray results ONLY for inspection
        nameDataMeasSVID = str(SVID) + '.csv'
        print('nameDataMeasSVID = %s' % nameDataMeasSVID)
        print('dataMeasSVID = %s' % dataMeasSVID)
        np.savetxt(nameDataMeasSVID, dataMeasSVID, fmt='%i,%.1f,%i,%i,%i,%i,%i,%.2f,%.2f,%.2f,%.2f,%i,%i,%i')

        signalTypesSVID = sbf2stf.observedSignalTypes(dataMeasSVID['MEAS_SIGNALTYPE'], verbose)
        print('signalTypesSVID = %s' % signalTypesSVID)

        # print("len dataMeas['MEAS_CODE'] %d" % len(dataMeas['MEAS_CODE']))
        # print("len dataMeasSVID['MEAS_CODE'] %d" % len(dataMeasSVID['MEAS_CODE']))
        # print dataMeasSVID['MEAS_SVID']

        indexSignalType = []
        dataMeasSVIDSignalType = []
        lliIndicators = []
        lliTOWs = []
        firstTOW = []

        for index, signalType in enumerate(signalTypesSVID):
            print('-' * 25)
            print("signalType = %s  index=%d - name = %s\n" % (signalType, index, mSSN.GNSSSignals[signalType]['name']))

            indexSignalType.extend(np.array(sbf2stf.indicesSignalType(signalType, dataMeasSVID['MEAS_SIGNALTYPE'], verbose)))

            print('type indexSignalType = %s' % type(indexSignalType))
            print('type indexSignalType[index] = %s' % type(indexSignalType[index]))
            print('indexSignalType = %s' % indexSignalType)
            print("indexSignalType[index] = %s (len = %d)" % (indexSignalType[index], len(indexSignalType[index])))
            print("indexSignalType[index][2] = %s\n" % indexSignalType[index][2])

            # set the data for 1 SV and 1 ST
            dataMeasSVIDSignalType.append(dataMeasSVID[indexSignalType[index]])

            print("dataMeasSVIDSignalType[index]['MEAS_LOCKTIME'] = %s (len = %d)" % (dataMeasSVIDSignalType[index]['MEAS_LOCKTIME'], len(dataMeasSVIDSignalType[index]['MEAS_LOCKTIME'])))
            print("dataMeasSVIDSignalType[index]['MEAS_LOCKTIME'][2] = %s\n" % dataMeasSVIDSignalType[index]['MEAS_LOCKTIME'][2])
            print("dataMeasSVIDSignalType[index][2] = %s\n" % dataMeasSVIDSignalType[index][2])
            print("dataMeasSVIDSignalType[index] = %s\n" % dataMeasSVIDSignalType[index])

            # # store temporaray results ONLY for inspection
            nameDataMeasSVIDSignalType = '%s-%s%d-%s.csv' % (gnssSyst, gnssSystShort, gnssPRN, mSSN.GNSSSignals[signalType]['name'])
            np.savetxt(nameDataMeasSVIDSignalType, dataMeasSVIDSignalType[index], fmt='%i,%.1f,%i,%i,%i,%i,%i,%.2f,%.2f,%.2f,%.2f,%i,%i,%i')

            # find loss of lock for SVID and SignalType
            lliIndicators.extend(np.array(sbf2stf.findLossOfLock(dataMeasSVIDSignalType[index]['MEAS_LOCKTIME'], verbose)))

            print('type lliIndicators = %s' % type(lliIndicators))
            print('type lliIndicators[index] = %s' % type(lliIndicators[index]))
            print("lliIndicators[index] = %s (%d)" % (lliIndicators[index], len(lliIndicators[index])))
            lliTOWs.append(dataMeasSVIDSignalType[index][lliIndicators[index]]['MEAS_TOW'])
            print('lliTOWs[%d] = %s (%d)' % (index, lliTOWs[index], len(lliTOWs[index])))

            # keep track of first observation TOW for this signaltype and SVID
            firstTOW.append(dataMeasSVIDSignalType[index]['MEAS_TOW'][0])
            print('firstTOW[%d] = %s' % (index, firstTOW[index]))

        #  combine the TOWs arrays corresponding to
        # (a) start of obs file on both frequencies
        # (b) LLI of both frequencies
        # (c) sort it
        # to find out how long the Loss of Lock lasts, only if both signaltypes are present!!
        if np.size(signalTypesSVID) == 2:
            lliTOWComb = np.unique(np.sort(np.concatenate(([firstTOW[0], firstTOW[1]], lliTOWs[0], lliTOWs[1]), axis=0)))
            print('lliTOWComb = %s (%d)' % (lliTOWComb, np.size(lliTOWComb)))
            print('type(lliTOWComb) = %s' % type(lliTOWComb))

            # gather the info about the Loss of Locks for this SVID
            indexTOWComb = []
            dataAtLLI = []
            for index, signalType in enumerate(signalTypesSVID):
                indexTOWComb.append(np.searchsorted(dataMeasSVIDSignalType[index]['MEAS_TOW'], lliTOWComb))
                print('indexTOWComb[%d] = %s (%d)' % (index, indexTOWComb[index], np.size(indexTOWComb[index])))
                dataAtLLI.append(dataMeasSVIDSignalType[index][indexTOWComb[index]])
                print('dataAtLLI[%d] = %s (%d)' % (index, dataAtLLI[index], np.size(dataAtLLI[index])))

        # plot the locktimes for this SVID for all SignalTypes
        plotLockTime.plotLockTime(SVID, signalTypesSVID, dataMeasSVIDSignalType, lliIndicators, lliTOWs, verbose)
        print('-' * 25)

        if verbose:
            plt.show()

    sys.exit(99)
