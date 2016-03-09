#!/usr/bin/env python

import sys
import subprocess
import time
import os
import numpy as np
from SSN import location
from SSN import ssnConstants as mSSN


# exit codes
E_SUCCESS = 0
E_FILE_NOT_EXIST = 1
E_NOT_IN_PATH = 2
E_UNKNOWN_OPTION = 3
E_TIME_PASSED = 4
E_FAILURE = 99
E_DOP_INVALID = 10
E_NRSVS_INVALID = 11


def runCmd(cmd, optCmd, verbose=False):
    """
    Run an external command and wait until it finishes (or max time set by TIME2WAIT)

    Parameters:
      cmd           the command to execute
      optCmd        the options passed to cmd

    Returns
        on completion, returns the stdout output of program
        on error, informs the error and exits
    """
    # some constants used
    TIME2WAIT = 300
    NROFDOTS = 10

    # start the subprocess and use timing to failstop it
    cmdFull = [cmd] + optCmd
    t_nought = time.time()
    p = subprocess.Popen(cmdFull, shell=False,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    # Wait for date to terminate. Get returncode
    seconds_passed = 0
    while(p.poll() is None and seconds_passed < TIME2WAIT):
        # We can do other things here while we wait
        time.sleep(1.)
        seconds_passed = time.time() - t_nought
        if verbose:
            dots = (('.' * (((int)(seconds_passed - 1) % NROFDOTS) + 1)) + (' ' * NROFDOTS))
            sys.stdout.write('  Converting SBF data %s\r' % dots)
            sys.stdout.flush()

    if verbose:
        sys.stdout.write('\n')

    # check the condition at end of execution
    if (seconds_passed >= TIME2WAIT):
        sys.stderr.write('  maximal processing time passed. %s exits.\n' % cmd)
        sys.exit(E_TIME_PASSED)
    else:
        (results, errors) = p.communicate()
        # sys.stdout.write("\nCommand output : \n", results)
        # print("error : ", errors)
        if errors == '':
            return results
        else:
            sys.stderr.write("  execution of %s failed with errors %s. %s exits.\n" %
                             (cmdFull, errors, cmd))
            sys.exit(E_FAILURE)


def runSBF2STF(sbfFileName, optSBF2STF, overwrite, verbose=False):
    """
    run the sbf2stf conversion and return the files created

    Parameters:
        sbfFileName: name of SBF file to convert with sbf2stf
        optSBF2STF: list of options given for sbf2stf

    Returns:
        nameConverted: list of names of output files created
    """
    # check whether program SBF2STF is on PATH
    SBF2STF = location.whereis('sbf2stf')                     # convert SBF to ASCII data
    if SBF2STF is None:
        sys.exit(E_NOT_IN_PATH)

    # make a private copy of the options optSBF2STF passed
    privateOptSBF2STF = list(optSBF2STF)

    if verbose:
        sys.stdout.write('Executing %s on %s\n' % (SBF2STF, sbfFileName))

    # create the vars containing the names of the files created
    nameConverted = []
    nameConvertedExists = []
    for option in privateOptSBF2STF:
        nameConverted.append(sbfFileName + '_' + option + '.stf')
        nameConvertedExists.append(False)

    # convert SBF file according to the options passed, check whether the converted files exist
    count = 0
    if not overwrite:
        for name in nameConverted:
            if os.path.isfile(name):
                nameConvertedExists[count] = True
            count += 1
        count = len(nameConvertedExists)
        for convertedExists in reversed(nameConvertedExists):
            # sys.stdout.write(privateOptSBF2STF[count-1])
            if convertedExists is True:
                privateOptSBF2STF.pop(count - 1)
            count -= 1

    nameConvertedReUse = []
    nameConvertedCreate = []
    if verbose:
        for i in range(len(nameConvertedExists)):
            if nameConvertedExists[i] is True:
                nameConvertedReUse.append(nameConverted[i])
            else:
                nameConvertedCreate.append(nameConverted[i])
        if overwrite:
            sys.stdout.write('  Creating files: %s\n' % nameConvertedCreate)
        else:
            sys.stdout.write('  Re-using files: %s\n' % nameConvertedReUse)

    # Perform SBF conversion if needed
    if False in nameConvertedExists:
        # create options used for SBF2STF conversion
        cmdOpts = ['-f', sbfFileName]
        for option in privateOptSBF2STF:
            cmdOpts += ['-m', option]               # add all conversion options
        cmdOpts += ['-t', ]                         # create header line
        # cmdOpts += ['-r', ]                         # raw data, not translated
        # cmdOpts += ['--precision', '3']             # 3 decimals
        # cmdOpts += ['-v']                           # verbose
        # cmdOpts += ['--unsugaredMeasEpoch']
        if verbose:
            sys.stdout.write('  Options: %s\n' % cmdOpts)
        # execute the SBF2STF
        runCmd(SBF2STF, cmdOpts, verbose)

    if verbose:
        sys.stdout.write('  SBF2STF conversion done. Returning files %s\n' % nameConverted)

    return nameConverted


def readDOPEpoch(stfMeasEpochFName, verbose=False):
    """
    reads the sbf2stf converted DOP cvs file and stores it into dataMeas numpy darray

    Parameters:
        stfMeasEpochFName: name of DOP_2 file created by sbf2stf

    Returns:
        DOP: contains the DOP afterbirthr sorting for TOW
    """
    if verbose:
        sys.stdout.write('    Reading DOP_2 data\n')

    DOPData = np.genfromtxt(stfMeasEpochFName, delimiter=",", skip_header=2, dtype=mSSN.colFmtDOP, names=mSSN.colNamesDOP)  # , filling_values=np.nan

    return DOPData


def readGEODPosEpoch(stfMeasEpochFName, verbose=False):
    """
    reads the sbf2stf converted Geodetic_2 cvs file and stores it into dataMeas numpy darray

    Parameters:
        stfMeasEpochFName: name of Geodetic_2 file created by sbf2stf

    Returns:
        dataMeas: contains the dataMeas after sorting for TOW
    """
    if verbose:
        sys.stdout.write('    Reading Geodetic_2 data\n')

    GEODPosData = np.genfromtxt(stfMeasEpochFName, delimiter=",", skip_header=2, dtype=mSSN.colFmtPosGeod, names=mSSN.colNamesPosGeod)

    print("GEODPosData = %s (#%d)" % (GEODPosData, len(GEODPosData)))

    return GEODPosData


def readMeasEpoch(stfMeasEpochFName, verbose=False):
    """
    reads the sbf2stf converted MeasEpoch cvs file and stores it into dataMeas numpy darray

    Parameters:
        stfMeasEpochFName: name of MeasEpoch_2 file created by sbf2stf

    Returns:
        dataMeas: contains the dataMeas after sorting for TOW, CHANNEL and SIGNALTYPE
    """
    if verbose:
        sys.stdout.write('    Reading and sorting MeasEpoch_2 data\n')

    measData = np.genfromtxt(stfMeasEpochFName, delimiter=",", skip_header=2, dtype=mSSN.colFmtMeasEpoch, names=mSSN.colNamesMeasEpoch)

    # sort the measData array according to TOW, CHANNEL, SIGNALTYPE
    sortIndexMeas = np.lexsort((measData['MEAS_SIGNALTYPE'], measData['MEAS_CHANNEL'], measData['MEAS_TOW']))
    dataMeasSorted = measData[sortIndexMeas]

    return dataMeasSorted


def readMeasExtra(stfMeasExtraName, verbose=False):
    """
    reads the sbf2stf converted MeasExtra cvs file and stores it into dataMeas numpy darray

    Parameters:
        stfMeasExtraFName: name of MeasExtra_1 file created by sbf2stf

    Returns:
        dataExtra: contains the dataMeas after sorting for TOW, CHANNEL and SIGNALTYPE
    """
    # colNames = ['EXTRA_WNC', 'EXTRA_TOW', 'EXTRA_CHANNEL', 'EXTRA_ANTENNA', 'EXTRA_SIGNALTYPE', 'EXTRA_LOCKTIME', 'EXTRA_CODEVARIANCE', 'EXTRA_CARRIERVARIANCE', 'EXTRA_DOPPLERVARIANCE', 'EXTRA_MPCORR', 'EXTRA_SMOOTHINGCORR', 'EXTRA_CUMMLOSSCONT']
    # colFmt = '%d,%f,%d,%d,%d,%d,%f,%f,%f,%d,%d,%d'
    if verbose:
        sys.stdout.write('    Reading and sorting MeasExtra_1 data\n')

    dataExtra = np.genfromtxt(stfMeasExtraName, delimiter=",", skip_header=2, dtype=mSSN.colFmtMeasExtra, names=mSSN.colNamesMeasExtra)

    # sort the dataExtra array according to TOW, CHANNEL, SIGNALTYPE
    sortIndexExtra = np.lexsort((dataExtra['EXTRA_SIGNALTYPE'], dataExtra['EXTRA_CHANNEL'], dataExtra['EXTRA_TOW']))
    dataExtraSorted = dataExtra[sortIndexExtra]

    return dataExtraSorted


def readSatVisibility(stfSatVisibilityName, verbose=False):
    """
    reads the sbf2stf converted SatVisibility cvs file and stores it into dataVisibility numpy darray

    Parameters:
        stfSatVisibilityName: name of SatVisibility_1 file created by sbf2stf

    Returns:
        dataVisibility: contains the dataVisibility after sorting for Wnc and TOW
    """
    if verbose:
        sys.stdout.write('    Reading and sorting SatVisibility_1 data\n')

    dataVisibility = np.genfromtxt(stfSatVisibilityName, delimiter=",", skip_header=2, dtype=mSSN.colFmtSatVisibility, names=mSSN.colNamesSatVisibility)

    # sort the dataVisibility array according to Wnc and TOW
    # sortIndexVisibility = np.lexsort((dataVisibility['VISIBILITY_WNC'], dataVisibility['VISIBILITY_TOW']))
    # dataVisibilitySorted = dataVisibility[sortIndexVisibility]

    return dataVisibility


def readJammingFile(JamFileName):
    """
    reads the jamming text comma delimited file and stores it into a numpy darray

    Parameters:
        JamFileName: name of file

    Returns:
        dataJamming: contains the Jamming values, start and end time.
    """
    dataJamming = np.genfromtxt(JamFileName, delimiter=",", skip_header=1, dtype=mSSN.colFmtJammingFile, names=mSSN.colNamesJammingFile)

    return dataJamming


def readChannelStatus(stfChannelStatusName, verbose=False):
    """
    reads the sbf2stf converted CHannelStatus cvs file and stores it into numpy darray

    Parameters:
        stfChannelStatusName: name of DOP_2 file created by sbf2stf

    Returns:
        chanStatus: contains the channel status
    """
    if verbose:
        sys.stdout.write('    Reading ChannelStatus_1 data\n')

    chanStatus = np.genfromtxt(stfChannelStatusName, delimiter=",", skip_header=2, dtype=mSSN.colFmtChannelStatus, names=mSSN.colNamesChannelStatus)

    return chanStatus


def removeSmoothing(code, smoothingCorr, mpCorr):
    """
    removes the code smoothing and multi-path correction applied by the Rx firmware

    Parameters:
        code: the smoothed pseudo-range
        smoothingCorr: smoothing correction applied
        mpCorr: multi-path correction

    Returns:
        rawCode: the raw measured pseudo distance
    """
    rawPR = code + (smoothingCorr + mpCorr) / 1000.0

    return rawPR


def verifySignalTypeOrder(measSignalType, extraSignalType, measTOW, verbose=False):
    """
    Basic check on the signaltypes whether they are aligned after sorting dataMeas and dataExtra

    Parameters:
        measSignalType: contains the signalType column form MeasEpoch_2
        extraSignalType: contains the signalType column form MeasExtra_1
        measTOW: contains the TOW from the MeasEpoch_2

    Returns:
        True if all OK, else False
    """
    if verbose:
        sys.stdout.write('    Checking SignalType order\n')

    if len(measSignalType) == len(extraSignalType):
        deltaSignalType = measSignalType - extraSignalType
        missValue = max(abs(deltaSignalType))
        if missValue != 0:  # or min(deltaSignalType) != 0
            # search index from where the error occurs
            firstIndex = np.nonzero(deltaSignalType == missValue)[0][0]
            # firstIndex = deltaSignalType.index(filter(lambda x: x != 0, deltaSignalType)[0])
            sys.stderr.write('    Mismatch of SignalType at TOW %d: dataMeas[SIGNALTYPE] = %d, dataExtra[SIGNALTYPE] = %d\n' % (measTOW[firstIndex], measSignalType[firstIndex], extraSignalType[firstIndex]))
            return False
        else:
            return True
    else:
        sys.stderr.write('    sizes of MeasEpoch (#%d) and MeasExtra (#%d) do not correspond\n' % (len(measSignalType), len(extraSignalType)))
        return False


def observedSatellites(colSVIDs, verbose=False):
    """
    Creates an index of observed satellites

    Parameters:
        colSVIDs: contains the SVIDs

    Returns:
        Ordered list of observed SVIDs
    """
    if verbose:
        sys.stdout.write('    Extracting list of observed satellites: ')

    listSVIDs = sorted(list(set(colSVIDs)))

    if verbose:
        for index, SVPRN in enumerate(listSVIDs):
            gnssSyst, gnssSystShort, gnssPRN = mSSN.svPRN(SVPRN)
            sys.stdout.write('%s%d (%d)' % (gnssSystShort, gnssPRN, SVPRN))
            if index < len(listSVIDs) - 1:
                sys.stdout.write(', ')
        sys.stdout.write('\n')

    return listSVIDs


def observedSignalTypes(measSignalTypes, verbose=False):
    """
    Creates an index of signal types

    Parameters:
        measSignalTypes: contains the SignalTypes

    Returns:
        Ordered list of observed signal types
    """
    if verbose:
        sys.stdout.write('      Extracting list of observed signal types: ')

    listSignalTypes = sorted(list(set(measSignalTypes)))

    if verbose:
        for index, signalType in enumerate(listSignalTypes):
            sys.stdout.write('%s (%d)' % (mSSN.GNSSSignals[signalType]['name'], signalType))
            if index < len(listSignalTypes) - 1:
                sys.stdout.write(', ')
        sys.stdout.write('\n')
        # sys.stdout.write('%s\n' % listSignalTypes)
    return listSignalTypes


def indicesSatellite(SVID, dataSVIDs, verbose=False):
    """
    returns the indices that contain data for a specific satellite

    Parameters:
        SVID: PRN of SV to search for
        dataSVIDs: data for SVID

    Returns:
        index array signalling the wanted SVID
    """
    # print('SVID = %s' % SVID)
    # print('dataSVIDs = %s' % dataSVIDs)
    if verbose:
        sys.stdout.write('    Extracting data for SVID %d\n' % SVID)

    return np.where(dataSVIDs == SVID)


def indicesSignalType(signalType, measSignalType, verbose=False):
    """
    returns the indices that contain the measurements of a specific observation type

    Parameters:
        signalType: code corresponsing to the signal typexanted
        measSignalType: signalTypes observed in MeasEpoch_2

    Returns:
        array containing the indices
    """
    if verbose:
        sys.stdout.write('        Getting data for SignalType %s\n' % signalType)

    # print('measSignalType = %s' % measSignalType)
    # print('type measSignalType = %s' % type(measSignalType))
    # print('type np.shere = %s' % type(np.where(measSignalType == signalType)))
    # print('type np.shere = %s' % type(np.array(np.where(measSignalType == signalType))))

    return np.where(measSignalType == signalType)


def findValidElevation(elevData, verbose=False):
    """
    findValidElevation searches for valid values for elevation angle
    Parameters:
        elevData columns with logged elevation data
    returns:
        indices which indicate valid elevation data
    """
    if verbose:
        sys.stdout.write('    Extracting valid elevation data\n')

    return np.where(elevData != -1)


def findValidDOP(pdopData, verbose=False):
    """
    findValidDOP seraches for the valid values for PDOP

    Parameters:
        pdopData column with PDOP data

    Returns:
        indices which indicate valid DOP data
    """
    if verbose:
        sys.stdout.write('    Extracting valid PDOP data\n')

    validDOPIndices = np.where(pdopData != 65535)
    if verbose:
        print('validDOPIndices = %s (#%d)' % (validDOPIndices, np.size(validDOPIndices)))

    if (np.size(validDOPIndices) == 0):
        sys.stderr.write('       No xDOP entries found. Program exits.\n')
        sys.exit(E_DOP_INVALID)

    return validDOPIndices


def findNrSVs(nrSVsData, verbose=False):
    """
    findNrSVs searches for nrSVs > 0

    Parameters:
        nrSVsData is column array containing observed number of SVs

    Returns:
        indices which indicate positive nr of SVs
    """
    if verbose:
        sys.stdout.write('      Extracting number of observed satellites.\n')

    validNrSVsIndices = np.where(nrSVsData != 255)
    if verbose:
        print('validNrSVsIndices = %s (#%d)' % (validNrSVsIndices, np.size(validNrSVsIndices)))

    if (np.size(validNrSVsIndices) == 0):
        sys.stderr.write('       No SVs found. Program exits.\n')
        sys.exit(E_NRSVS_INVALID)

    return validNrSVsIndices


def findLossOfLock(measLockTime, verbose=False):
    """
    returns the indices where a loss of lock occured

    Parameters:
        measLockTime is the locktime for a specific SVID and specific SignalType

    Returns:
        array containing the indices where a loss of lock occured
    """
    if verbose:
        sys.stdout.write('  Looking for Loss of Lock\n')

    # calculate the difference between subsequent lockTimes and find the loss of lock
    diffLockTime = np.diff(np.int64(measLockTime))

    # # for intermediate results only
    # print('measLockTime = %s (%d)' % (measLockTime, np.size(measLockTime)))
    # print('diffLockTime = %s (%d)' % (diffLockTime, np.size(diffLockTime)))
    # print('type diffLockTime = %s' % type(diffLockTime))

    # # for i in range(np.size(diffLockTime)):
    # #     # if diffLockTime[i] == 0:
    # #     print('DIFFLOCKTIME[%d] = %s' % (i, diffLockTime[i]))

    # indicesLossOfLock = np.where(diffLockTime < 0)

    # print('indicesLossOfLock = %s' % indicesLossOfLock)
    # # EOF intermediate results

    return np.where(diffLockTime < 0)


def findNanValues(data):
    """
    findNanValues looks where the data is NaN
    """
    # if verbose:
    #     sys.stdout.write('  Looking for NaN index\n')
    print('data = %s (#%d)' % (data, len(data)))

    return np.where(~np.isnan(data))


def findSidePeaks(SVID, signalTypes, dataMeasSVID, verbose=False):
    """
    findSidePeaks finds the side peak correlation by differencing the code measurements on E1A and E6
    Parameters:
        SVID: identifies the satellite
        signalTypes: the signals observed for that satellite (ordered list!! so 16 (L1A) before 18 (E6A))
        dataMeasSVID: the data observed for that satellite
    Returns:
        iTOW: the TOWs for which both signals are present
        dPR: the difference between the E1A and E6A Pseudo Range measurements
        sidePeakIndex: the index at which a jump in dPR is detected (exluding the first value)
        jumpDPR: the difference between dPR at detected side peak and its previous value (thus jump in dPR detected)
        jumpDPRNear97Indices: indices in jumpDPR identifying the elements nearest to 9.7 integer multiple
    """
    print('-' * 50)
    if verbose:
        sys.stdout.write('  Looking for Side Peaks\n')

    gnssSyst, gnssSystShort, gnssPRN = mSSN.svPRN(SVID)

    # define limits for delta PR for detecting 'possible' and 'probable' sidePeak indicators
    dPRlimit = 4.0  # meter
    jumpMargin = 0.05  # 5 percent margin on multiple of 9.7 m

    # deterimine the intersection and get the indices on both signal types for that intersection
    indexTOWIntersect = []
    iMeas = []  # intersection on TOW between the signaltypes for this SVID
    # get the TOW that are present for bith SignalTypes
    iTOW = np.intersect1d(dataMeasSVID[0]['MEAS_TOW'], dataMeasSVID[1]['MEAS_TOW'])
    # print('iTOW %s ()' % (iTOW, len(iTOW)))

    for index, dataSVIDMeas in enumerate(dataMeasSVID):
        mask = np.in1d(dataSVIDMeas['MEAS_TOW'], iTOW)
        indexTOWIntersect.append(np.argwhere(mask).flatten())
        # create intersection views on data
        iMeas.append(dataSVIDMeas[indexTOWIntersect[index]])

        print('indexTOWIntersect[%d] = %s (#%d)' % (index, indexTOWIntersect[index], len(indexTOWIntersect[index])))
        print('iMeas[%d][MEAS_TOW] = %s (#%d)\n' % (index, iMeas[index]['MEAS_TOW'], len(iMeas[index]['MEAS_CODE'])))

        # # save for debugging purposes
        # fileName = 'meas%s%d-st%d.csv' % (gnssSystShort, gnssPRN, signalTypes[index])
        # np.savetxt(fileName, iMeas[index], fmt=mSSN.colFmtMeasEpoch)

    # determine difference between observed CODE measurements at each intersecting TOW
    dPR = iMeas[0]['MEAS_CODE'] - iMeas[1]['MEAS_CODE']
    print('dPR = %s (#%d)' % (dPR, len(dPR)))

    # look for side-peak indicators when dPR > dPRlimit
    sidePeakIndex = np.where(np.fabs(np.ediff1d(np.concatenate((np.array([0]), dPR)))) > dPRlimit)[0]
    print('sidePeakIndex = %s (#%d)\n' % (sidePeakIndex, len(sidePeakIndex)))
    sidePeakIndex = []
    sidePeakIndex = np.where(np.fabs(np.ediff1d(dPR[0:])) > dPRlimit)[0] + 1  # add 1 since we ignore the first value for ediff1d
    print('sidePeakIndex = %s (#%d)\n' % (sidePeakIndex, len(sidePeakIndex)))

    print(np.ediff1d(np.concatenate((np.array([0]), dPR))))
    print(np.ediff1d(dPR[0:]))
    print('sidePeakIndex = %s (#%d)\n' % (sidePeakIndex, len(sidePeakIndex)))

    # create array for the TOW/dPR based on the  index indicators for sidePeaks
    sidePeakTOWs = dataMeasSVID[0][indexTOWIntersect[0]]['MEAS_TOW'][sidePeakIndex]
    sidePeakDPR = dPR[sidePeakIndex]
    print('sidePeakTOWs = %s (#%d)' % (sidePeakTOWs, len(sidePeakTOWs)))
    print('sidePeakDPR = %s (#%d)\n' % (sidePeakDPR, len(sidePeakDPR)))

    # calculate the difference between the detected sidePeak dPR and the previous observed value of dPR
    prevIndex = sidePeakIndex - 1
    jumpDPR = dPR[sidePeakIndex] - dPR[prevIndex]
    print('jumpDPR = %s (#%d)' % (jumpDPR, len(jumpDPR)))
    print('jumpDPR = %s (#%d)' % ((abs(jumpDPR) / 9.7), len(jumpDPR)))
    print('jumpDPR = %s (#%d)' % (np.rint((abs(jumpDPR) / 9.7)), len(jumpDPR)))

    jumpDPRNear97 = abs((abs(jumpDPR) / 9.7) - np.rint((abs(jumpDPR) / 9.7)))
    jumpDPRNear97Indices = np.where(jumpDPRNear97 < jumpMargin)[0]
    print('jumpDPRNear97 = %s (#%d)' % (jumpDPRNear97Indices, len(jumpDPRNear97Indices)))

    jumpDPRNear1465 = abs((abs(jumpDPR) / 14.65) - np.rint((abs(jumpDPR) / 14.65)))
    jumpDPRNear1465Indices = np.where(jumpDPRNear1465 < jumpMargin)[0]
    print('jumpDPRNear1465 = %s (#%d)' % (jumpDPRNear1465Indices, len(jumpDPRNear1465Indices)))

    print('-' * 50)

    return iTOW, dPR, sidePeakTOWs, sidePeakDPR, jumpDPR, jumpDPRNear97Indices, jumpDPRNear1465Indices
