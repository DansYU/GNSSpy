#!/usr/bin/env python

import sys
import os
import numpy as np
import argparse

from SSN import sbf2stf
from Plot import plotCN0diff
from GNSS import gpstime
from SSN import ssnConstants as mSSN
__author__ = 'AAlex'


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
# print sys.argv[0], ospath


def treatCmdOpts(argv):
    """
    Treats the command line options

    Parameters:
      argv          the options (without argv[0]

    Sets the global variables according to the CLI args
    """
    helpTxt = os.path.basename(__file__) + ' plots the Carrier-to-Noise variation for PRS data'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)
    parser.add_argument('-f','--file', help='Name of SBF file', required=True)
    parser.add_argument('-d', '--dir', help='Directory of SBF file (defaults to .)', required=False, default='.')
    parser.add_argument('-o','--overwrite', help='overwrite intermediate files (default False)', action='store_true', required=False)
    parser.add_argument('-v', '--verbose', help='displays interactive graphs and increase output verbosity (default False)', action='store_true', required=False)
    args = parser.parse_args()

    # # show values
    # print ('SBFFile: %s' % args.file)
    # print ('dir = %s' % args.dir)
    # print ('verbose: %s' % args.verbose)
    # print ('overwrite: %s' % args.overwrite)

    return args.file, args.dir, args.overwrite, args.verbose


def createFullTimeSpan(towMeas):
    '''
    createFullTimeSpan creates an array of TOW and UTC that covers the full observation period for all detected satellites
    Parameters:
        towMeas: TOWs of all observed measurements
    Returns:
        spanTOW, spanUTC: values that span the observation period
    '''
    TOWMax = -1
    TOWMin = gpstime.secsInWeek + 1

    for i, TOWi in enumerate(towMeas):
        TOWMax = max(TOWMax, TOWi[-1])
        TOWMin = min(TOWMin, TOWi[0])

    spanTOW = np.arange(TOWMin, TOWMax + 1.)
    print('spanTOW = %f => %f (%d)' % (spanTOW[0], spanTOW[-1], np.size(spanTOW)))
    # and convert to UTC
    spanUTC = plotCN0diff.TOW2UTC(WkNr, spanTOW)
    print('spanUTC = %s => %s (%d)' % (spanUTC[0], spanUTC[-1], np.size(spanUTC)))

    return spanTOW, spanUTC


def extractTOWandCN0(SVprn, measData, TOWmeas, CN0meas, verbose=False):
    """
    extractTOWandCN0 axtracts for a SV the TOW and CN0 values observed per signaltype
    Parameters:
        SVprn: the ID for this SV
        measData: the measurement data from MEAS_EPOCH
        TOWmeas: array of lists that contains the TOW for this PRN and per signalType
        CN0meas: idem for CN0
    Returns:
        the signal types for this SVprn
    """
    if verbose:
        print('  Processing SVID = %d' % SVprn)

    # find indices with data for this SVID
    # print('SVprn = %s' % SVprn)
    indexSVprn = sbf2stf.indicesSatellite(SVprn, measData['MEAS_SVID'], verbose)
    # print('indexSVprn = %s' % indexSVprn)
    dataMeasSVprn = measData[indexSVprn]
    # print('dataMeasSVprn = %s' % dataMeasSVprn)

    # find indices that correspond to the signalTypes for this SVprn
    signalTypesSVprn = sbf2stf.observedSignalTypes(dataMeasSVprn['MEAS_SIGNALTYPE'], verbose)

    indexSignalType = []

    for index, signalType in enumerate(signalTypesSVprn):
        if verbose:
            print('      Treating signalType = %s (index=%d)' % (signalType, index))

        # get the observation time span and observed CN0 for this SVprn and SignalType
        indexSignalType.extend(np.array(sbf2stf.indicesSignalType(signalType, dataMeasSVprn['MEAS_SIGNALTYPE'], verbose)))
        TOWmeas.append(dataMeasSVprn[indexSignalType[index]]['MEAS_TOW'])
        CN0meas.append(dataMeasSVprn[indexSignalType[index]]['MEAS_CN0'])

        # # print last added values
        if True:
            print('TOWmeas[%d] = %d => %d (%d)' % (len(TOWmeas), TOWmeas[-1][0], TOWmeas[-1][-1], np.size(TOWmeas[-1])))
            print('CN0meas[%d] = %f => %s (%d)' % (len(CN0meas), CN0meas[-1][0], CN0meas[-1][-1], np.size(CN0meas[-1])))

    return signalTypesSVprn


def fillDataGaps(spanTOW, TOW, CN0):
    '''
    fillDataGaps fills in the datagaps in the CN0 data to match the whole observation time span for simultaneously plotting the CN0 of all SVs for 1 signaltype
    Parameters:
        spanTOW = full span of the observation period
        TOW = observation span for this SV and signalType
        CN0 = observed value
    Returns:
        spanCN0 contains the CN0 values but with NaN on TOWs where no data is available
    '''
    # search for the indices that match between spanTOW and TOW
    matchIndices = np.searchsorted(spanTOW, TOW)
    print('matchIndices = %s (%d)' % (matchIndices, len(matchIndices)))

    # create the CN0 that spans full dataset
    spanCN0 = np.zeros(np.size(spanTOW))
    spanCN0.fill(np.nan)

    for i, iMatch in enumerate(matchIndices):
        spanCN0[iMatch] = CN0[i]

    # test
    print('CN0 = %s (%d)' % (CN0, len(CN0)))
    print('spanCN0 = %s (%d)' % (spanCN0, len(spanCN0)))

    return spanCN0


def extractELEVATION(SVprn, dataVisibility, verbose=False):
    """
    extractELEVATION Extracts for a SV the elevation values observed
    Parameters:
        SVprn: the ID for this SV
        dataVisibility: the measurement data from SatVisibility_1
    Returns:
        the elevation for this SVprn
    """
    indexSVprnVis = sbf2stf.indicesSatellite(SVprn, dataVisibility['VISIBILITY_SVID'], verbose)
    dataVisibilitySVprn = dataVisibility[indexSVprnVis]['VISIBILITY_ELEVATION']
    # print(SVprn)
    # print(dataVisibilitySVprn)
    # sys.exit(0)

    return dataVisibilitySVprn


if __name__ == "__main__":
    # treat command line options
    nameSBF, dirSBF, overwrite, verbose = treatCmdOpts(sys.argv)

    # change to the directory dirSBF if it exists
    workDir = os.getcwd()
    if dirSBF is not '.':
        workDir = os.path.normpath(os.path.join(workDir, dirSBF))

    # print ('workDir = %s' % workDir)
    if not os.path.exists(workDir):
        sys.stderr.write('Directory %s does not exists. Exiting.\n' % workDir)
        sys.exit(E_DIR_NOT_EXIST)
    else:
        os.chdir(workDir)

    # print ('curDir = %s' % os.getcwd())
    # print ('SBF = %s' % os.path.isfile(nameSBF))

    # check whether the SBF datafile exists
    if not os.path.isfile(nameSBF):
        sys.stderr.write('SBF datafile %s does not exists. Exiting.\n' % nameSBF)
        sys.exit(E_FILE_NOT_EXIST)

    # execute the conversion sbf2stf needed
    SBF2STFOPTS = ['MeasEpoch_2', 'MeasExtra_1', 'SatVisibility_1']     # options for conversion, ORDER IMPORTANT!!
    sbf2stfConverted = sbf2stf.runSBF2STF(nameSBF, SBF2STFOPTS, overwrite, verbose)
    print('SBF2STFOPTS = %s' % SBF2STFOPTS)

    # check the blocks for errors like 1.INF
    for i in sbf2stfConverted:
        f = open(i, 'r')
        filedata = f.read()
        f.close()
        newdata = filedata.replace('1.#INF', '').replace('-1.#IND', '')
        f = open(i, 'w')
        f.write(newdata)
        f.close()

    # extracts data in numpy array
    for option in SBF2STFOPTS:
        # print('option = %s - %d' % (option, SBF2STFOPTS.index(option)))
        if option == 'MeasEpoch_2':
            # read the MeasEpoch data into a numpy array
            dataMeas = sbf2stf.readMeasEpoch(sbf2stfConverted[SBF2STFOPTS.index(option)], verbose)
        elif option == 'MeasExtra_1':
            # read the MeasExtra data into numpy array
            dataExtra = sbf2stf.readMeasExtra(sbf2stfConverted[SBF2STFOPTS.index(option)], verbose)
        elif option == 'SatVisibility_1':
            #  read the SatVisibility data into a numpy array
            dataVisibility = sbf2stf.readSatVisibility(sbf2stfConverted[SBF2STFOPTS.index(option)], verbose)
        else:
            print('  wrong option %s given.' % option)
            sys.exit(E_WRONG_OPTION)

    # check whether the same signaltypes are on corresponsing lines after sorting
    if not sbf2stf.verifySignalTypeOrder(dataMeas['MEAS_SIGNALTYPE'], dataExtra['EXTRA_SIGNALTYPE'], dataMeas['MEAS_TOW'], verbose):
        sys.exit(E_SIGNALTYPE_MISMATCH)

    # determine current weeknumber and subsequent date from SBF data
    WkNr = int(dataMeas['MEAS_WNC'][0])
    dateString = gpstime.UTCFromWT(WkNr, float(dataMeas['MEAS_TOW'][0])).strftime("%d/%m/%Y")
    if verbose:
        print('WkNr = %d - dateString = %s' % (WkNr, dateString))

    # correct the smoothed PR Code and work with the raw PR
    dataMeas['MEAS_CODE'] = sbf2stf.removeSmoothing(dataMeas['MEAS_CODE'], dataExtra['EXTRA_SMOOTHINGCORR'], dataExtra['EXTRA_MPCORR'])
    # print('rawPR = %s\n' % dataMeas['MEAS_CODE'])

    # find list of SVIDs from MeasEpoch and SatVisibility blocks and SignalTypes observed
    SVIDs = sbf2stf.observedSatellites(dataMeas['MEAS_SVID'], verbose)
    SVIDsVis = sbf2stf.observedSatellites(dataVisibility['VISIBILITY_SVID'], verbose)
    signalTypes = sbf2stf.observedSignalTypes(dataMeas['MEAS_SIGNALTYPE'], verbose)

    # storing data in arrays per SV and per signalType
    indexSignalType = []
    dataMeasSignalType = []
    measTOW = []  # TOWs with measurements
    measTOWElev = []
    measCN0 = []  # CNO diff @ measTOW
    measCN0Elev = []
    STlist = []  # list of signaltypes traversed
    SVIDlist = []  # list of SVIDs traversed for CN0
    SVIDlistElev = []  # list of SVIDs traversed for Elev
    ELEVATIONVisibility = []  # list of Elevation  traversed

    # extract first TOW and CN0 arrays for all SVs and signaltypes
    for SVID in SVIDs:
        signalTypesSVID = extractTOWandCN0(SVID, dataMeas, measTOW, measCN0, verbose)
        for i, signalType in enumerate(signalTypesSVID):
            STlist.append(signalType)
            SVIDlist.append(SVID)

    # preparing list of elevation to corespond with the CN0 list
    for SVID in SVIDsVis:
        signalTypesSVID = extractTOWandCN0(SVID, dataMeas, measTOWElev, measCN0Elev, verbose)
        for i, signalType in enumerate(signalTypesSVID):
            SVIDlistElev.append(SVID)
    for i in range(len(SVIDlist)):
        if not SVIDlist[i] == SVIDlistElev[i]:
            SVIDlistElev.insert(i, SVIDlist[i])

    # create the TOW array covering the whole tie range
    TOWspan, UTCspan = createFullTimeSpan(measTOW)
    print('TOWspan = %f => %f (%d)' % (TOWspan[0], TOWspan[-1], np.size(TOWspan)))
    print('UTCspan = %s => %s (%d)' % (UTCspan[0], UTCspan[-1], np.size(UTCspan)))

    # for all the CN0 data per Signaltype and SVID => add NaN for missing data
    # for index, signalType in enumerate(signalTypesSVID):
    print('\nmeasTOW = %d - %d - %d' % (len(measTOW), len(measTOW[0]), len(measTOW[-1])))
    for i, measTOWi in enumerate(measTOW):
        print('measTOW[%d] = %f - %f' % (i, measTOWi[0], measTOWi[-1]))
    for i, measCN0i in enumerate(measCN0):
        print('measCN0[%d] = %f - %f' % (i, measCN0i[0], measCN0i[-1]))

    for i, SVID in enumerate(SVIDlist):
        print('Observed SV %d - SignalType = %d' % (SVID, STlist[i]))

    # adjust the measCNO arrays to fill with NaN as to fit the TOWall array for plotting
    measCN0span = []
    for i in range(len(measCN0)):
        measCN0span.append(fillDataGaps(TOWspan, measTOW[i], measCN0[i]))

    for i in range(len(measCN0)):
        print('measCN0span[%d] = %s (%d)' % (i, measCN0span[i], len(measCN0span[i])))

    # creates the lists of CN0 diff
    measCN0diff = []
    for i in range(len(measCN0span)):
        measCN0diff.append(np.diff(measCN0span[i]))

    # adjust the length of time span to fit the CN0 diff
    UTCspan.remove(UTCspan[0])
    # create the plots for each signaltype
    plotCN0diff.plotCN0diff(SVIDlist, STlist, UTCspan, measCN0diff, dateString, verbose)
    # calculating the mean elevation for each signal type
    meanElev = []
    for i in SVIDlistElev:
        ELEVATIONVisibility = extractELEVATION(i, dataVisibility, verbose)
        mean = np.mean(ELEVATIONVisibility)
        meanElev.append(mean)
    # determine the maximum difference of CN0
    for i in range(len(measCN0diff)):
        gnssSystCN0, gnssSystShortCN0, gnssPRNCN0 = mSSN.svPRN(SVIDlist[i])
        print('Satellite %d signaltype %s has %s maximum var. at the elev. of %s ' % (gnssPRNCN0, mSSN.GNSSSignals[STlist[i]]['name'], np.nanmin(measCN0diff[i]), meanElev[i]))
    sys.exit(E_SUCCESS)