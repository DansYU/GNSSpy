#!/usr/bin/env python
import sys
import os
import numpy as np
import argparse
import matplotlib.dates as md

from SSN import sbf2stf
from Plot import plotCN0
from GNSS import gpstime
from SSN import ssnConstants as mSSN
from scipy import stats as st

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


def treatCmdOpts(argv):
    """
    Treats the command line options

    Parameters:
      argv

    Sets the global variables according to the CLI args
    """
    helpTxt = os.path.basename(__file__) + ' detects if a data file is jammed'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)
    parser.add_argument('-f', '--file', help='Name of SBF file', required=True)
    parser.add_argument('-d', '--dir', help='Directory of SBF file (defaults to .)', required=False, default='.')
    parser.add_argument('-o', '--overwrite', help='overwrite intermediate files (default False)', action='store_true', required=False)
    parser.add_argument('-j', '--jamming', help='setting the config file for jamming periods', required=False, default='.')
    parser.add_argument('-v', '--verbose', help='displays interactive graphs and increase output verbosity (default False)', action='store_true', required=False)
    args = parser.parse_args()

    return args.file, args.dir, args.overwrite, args.jamming, args.verbose


def createFullTimeSpan(towMeas):
    """
    createFullTimeSpan creates an array of TOW and UTC that covers the full observation period for all detected satellites
    Parameters:
        towMeas: TOWs of all observed measurements
    Returns:
        spanTOW, spanUTC: values that span the observation period
    """
    TOWMax = -1
    TOWMin = gpstime.secsInWeek + 1

    for i, TOWi in enumerate(towMeas):
        TOWMax = max(TOWMax, TOWi[-1])
        TOWMin = min(TOWMin, TOWi[0])

    spanTOW = np.arange(TOWMin, TOWMax + 1.)
    print('spanTOW = %f => %f (%d)' % (spanTOW[0], spanTOW[-1], np.size(spanTOW)))
    # and convert to UTC
    spanUTC = plotCN0.TOW2UTC(WkNr, spanTOW)
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


def fillDataGaps(spanTOW, TOW, CN0):
    """
    fillDataGaps fills in the datagaps in the CN0 data to match the whole observation time span for simultaneously plotting the CN0 of all SVs for 1 signaltype
    Parameters:
        spanTOW = full span of the observation period
        TOW = observation span for this SV and signalType
        CN0 = observed value
    Returns:
        spanCN0 contains the CN0 values but with NaN on TOWs where no data is available
    """
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


def normVarDet(elevMean):
    """
    normVarDet chooses the normal variation value corresponding to the mean elevation of the satellite
    Parameters:
        elevMean = mean of elevation the satellite traversed
    Returns:
        var = normal variation
    """
    if elevMean <= 10:
        var = 3
    elif 10 <= elevMean <= 20:
        var = 3
    elif 20 <= elevMean <= 30:
        var = 1.5
    elif 30 <= elevMean <= 40:
        var = 1.5
    elif 40 <= elevMean <= 50:
        var = 1.25
    elif 50 <= elevMean <= 60:
        var = 1.25
    elif 60 <= elevMean <= 70:
        var = 1
    elif 70 <= elevMean <= 80:
        var = 0.75
    elif 80 <= elevMean <= 90:
        var = 0.75
    return var

if __name__ == "__main__":
    # treat command line options
    nameSBF, dirSBF, overwrite, jamming, verbose = treatCmdOpts(sys.argv)

    # change to the directory dirSBF if it exists
    workDir = os.getcwd()
    if dirSBF is not '.':
        workDir = os.path.normpath(os.path.join(workDir, dirSBF))

    if not os.path.exists(workDir):
        sys.stderr.write('Directory %s does not exists. Exiting.\n' % workDir)
        sys.exit(E_DIR_NOT_EXIST)
    else:
        os.chdir(workDir)

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

    # preparing jamming file
    JammingValues = []
    JammingStartTime = []
    JammingEndTime = []
    if jamming is not '.':
        dataJamming = sbf2stf.readJammingFile(jamming)
        for i in dataJamming['JAMMING_VALUE']:
            JammingValues.append(i)
        for i in dataJamming['START_TIME']:
            JammingStartTime.append(gpstime.UTCFromString(2015, 12, 3, i))
            print(JammingStartTime)
        for i in dataJamming['END_TIME']:
            JammingEndTime.append(gpstime.UTCFromString(2015, 12, 3, i))

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
    measTOW = []  # TOWs with measurements
    measTOWElev = []
    measCN0 = []  # CNO values @ measTOW
    measCN0Elev = []
    STlist = []  # list of signaltypes traversed
    SVIDlist = []  # list of SVIDs traversed
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

    # adjust the measCNO arrays to fill with NaN as to fit the TOWall array
    measCN0span = []

    for i in range(len(measCN0)):
        measCN0span.append(fillDataGaps(TOWspan, measTOW[i], measCN0[i]))
    for i in range(len(measCN0)):
        print('measCN0span[%d] = %s (%d)' % (i, measCN0span[i], len(measCN0span[i])))

    # first 9 values of CN0 for each satellite and signaltype
    # for i in range(len(measCN0span)):
    #     gnssSystCN0, gnssSystShortCN0, gnssPRNCN0 = mSSN.svPRN(SVIDlist[i])
    #     print('Satellite %s%s signaltype %s' % (gnssSystShortCN0, gnssPRNCN0, mSSN.GNSSSignals[STlist[i]]['name']))
    #     print('CNO=%s' % (list(measCN0span[i][0:9])))

    # for i in range(len(measCN0span)):
    #     stdev = np.std(measCN0span[i][0:99], dtype=np.float64)
    #     mean = np.mean(measCN0span[i][0:99])
    #     prec = st.norm.cdf(measCN0span[i][100], loc=mean, scale=stdev)
    #     print(mean, prec, measCN0span[i][100])

    # calculating the mean elevation for each satellite and signal type
    meanElev = []
    for i in SVIDlistElev:
        ELEVATIONVisibility = extractELEVATION(i, dataVisibility, verbose)
        mean = np.mean(ELEVATIONVisibility)
        meanElev.append(mean)

    # Determine the unjammed starting period
    start_span = []
    norm_var_span = []
    for i in range(len(measCN0span)):
        start = []
        start.append(measCN0span[i][0])
        # Setting normal variation
        norm_var = normVarDet(meanElev[i])
        norm_var_span.append(norm_var)
        for j in range(len(measCN0span[i]))[1:]:
            if measCN0span[i][j] > measCN0span[i][j - 1] - norm_var:
                start.append(measCN0span[i][j])
            else:
                break
        start_span.append(start)

    measCN0spanNaN = measCN0span
    for k in range(len(measCN0spanNaN)):
        for l in range(len(measCN0spanNaN[k])):
            if np.isnan(measCN0spanNaN[k][l]):
                measCN0spanNaN[k][l] = 0

    # creating the list of events for every signal type and satellite
    jamming_pos_span = []
    for i in range(len(measCN0span)):
        checker = 0
        start_mean = np.mean(start_span[i])
        jamming_pos = []
        for j in range(len(measCN0span[i]))[len(start_span[i]):]:
                if (measCN0span[i][j] < start_mean - norm_var_span[i]):
                    if checker == 0:
                        start_mean = measCN0span[i][j - 1]
                        jamming_pos.append(j)
                    checker = 1
                else:
                    if checker == 1:
                        jamming_pos.append(j)
                    checker = 0
        jamming_pos_span.append(jamming_pos)

    L1signal = ['GPS_L1-CA', 'GPS_L1-P(Y)', 'GAL_L1A', 'GAL_L1BC']
    for i in range(len(jamming_pos_span)):
        gnssSystCN0, gnssSystShortCN0, gnssPRNCN0 = mSSN.svPRN(SVIDlist[i])
        if mSSN.GNSSSignals[STlist[i]]['name'] in L1signal:
            print('Satellite %s%s signaltype %s threshold %f' % (gnssSystShortCN0, gnssPRNCN0, mSSN.GNSSSignals[STlist[i]]['name'], norm_var_span[i]))
            for j in range(len(jamming_pos_span[i])):
                if j % 2 == 0:
                    print('Jamming started at %s, C/No value = %s' % (UTCspan[jamming_pos_span[i][j]], measCN0span[i][jamming_pos_span[i][j]]))
                if j % 2 == 1:
                    print('Jamming stopped at %s, C/No value = %s' % (UTCspan[jamming_pos_span[i][j]], measCN0span[i][jamming_pos_span[i][j]]))

    # # deleting previous jammed period
    # for i in range(len(jamming_pos_span)):
    #     if len(jamming_pos_span[i]) > 3:
    #         if int((JammingStartTime[0] - UTCspan[jamming_pos_span[i][0]]).total_seconds()) > 15:
    #             del(jamming_pos_span[i][0:2])

    # breaking the times captured in start and stop
    jamming_pos_start = []
    jamming_pos_stop = []
    for i in range(len(jamming_pos_span)):
        pair = []
        unpair = []
        for j in range(len(jamming_pos_span[i])):
            if j % 2 == 0:
                pair.append(jamming_pos_span[i][j])
            else:
                unpair.append(jamming_pos_span[i][j])
        jamming_pos_start.append(pair)
        jamming_pos_stop.append(unpair)

    # printing L1 signals starting and stopping detected times
    # L1signal = ['GPS_L1-CA', 'GAL_L1A', 'GAL_L1BC']
    # for i in range(len(jamming_pos_start)):
    #     gnssSystCN0, gnssSystShortCN0, gnssPRNCN0 = mSSN.svPRN(SVIDlist[i])
    #     if mSSN.GNSSSignals[STlist[i]]['name'] in L1signal:
    #         print('Satellite %s%s signaltype %s threshold %f' % (gnssSystShortCN0, gnssPRNCN0, mSSN.GNSSSignals[STlist[i]]['name'], norm_var_span[i]))
    #         for j in range(len(jamming_pos_start[i])):
    #             print('Jamming started at => %s' % (UTCspan[jamming_pos_start[i][j]]), measCN0span[i][jamming_pos_start[i][j]])

    # for i in range(len(jamming_pos_stop)):
    #     gnssSystCN0, gnssSystShortCN0, gnssPRNCN0 = mSSN.svPRN(SVIDlist[i])
    #     if mSSN.GNSSSignals[STlist[i]]['name'] in L1signal:
    #         print('Satellite %s%s signaltype %s threshold %f' % (gnssSystShortCN0, gnssPRNCN0, mSSN.GNSSSignals[STlist[i]]['name'], norm_var_span[i]))
    #         for j in range(len(jamming_pos_stop[i])):
    #             print('Jamming stopped at => %s' % (UTCspan[jamming_pos_stop[i][j]]), measCN0span[i][jamming_pos_stop[i][j]])

    # printing unjammed periods span and info
    # for i in range(len(start_span)):
    #     gnssSystCN0, gnssSystShortCN0, gnssPRNCN0 = mSSN.svPRN(SVIDlist[i])
    #     if mSSN.GNSSSignals[STlist[i]]['name'] in L1signal:
    #         print('Satellite %s%s signaltype %s threshold %f' % (gnssSystShortCN0, gnssPRNCN0, mSSN.GNSSSignals[STlist[i]]['name'], norm_var_span[i]))
    #         print(len(start_span[i]), 'UTCspan = %s => %s' % (UTCspan[0], UTCspan[len(start_span[i])]))
    #         print(np.mean(start_span[i]), measCN0span[i][len(start_span[i]) - 1], measCN0span[i][len(start_span[i])])
    sys.exit(E_SUCCESS)