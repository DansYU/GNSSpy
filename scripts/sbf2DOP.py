#!/usr/bin/env python

import sys
import os
import numpy as np
import argparse
from matplotlib.pyplot import show

from SSN import sbf2stf
from GNSS import gpstime
from Plot import plotDOP

__author__ = 'amuls'


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
    helpTxt = os.path.basename(__file__) + ' plots the DOP values from PRS data'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)
    parser.add_argument('-f','--file', help='Name of SBF file',required=True)
    parser.add_argument('-d', '--dir', help='Directory of SBF file (defaults to .)', required=False, default='.')
    parser.add_argument('-m', '--maxdop', help='Maximum DOP value to display (default 10)', type=int, required=False, default=20)
    parser.add_argument('-o','--overwrite', help='overwrite intermediate files (default False)', action='store_true', required=False)
    parser.add_argument('-v', '--verbose', help='displays interactive graphs and increase output verbosity (default False)', action='store_true', required=False)
    args = parser.parse_args()

    # # show values
    # print('SBFFile: %s' % args.file)
    # print('dir = %s' % args.dir)
    # print('verbose: %s' % args.verbose)
    # print('overwrite: %s' % args.overwrite)

    return args.file, args.dir, args.overwrite, args.verbose, args.maxdop


if __name__ == "__main__":
    # treat command line options
    nameSBF, dirSBF, overwrite, verbose, maxdop = treatCmdOpts(sys.argv)

    # change to the directory dirSBF if it exists
    workDir = os.getcwd()
    if dirSBF is not '.':
        workDir = os.path.normpath(os.path.join(workDir, dirSBF))

    # print('workDir = %s' % workDir)
    if not os.path.exists(workDir):
        sys.stderr.write('Directory %s does not exists. Exiting.\n' % workDir)
        sys.exit(E_DIR_NOT_EXIST)
    else:
        os.chdir(workDir)

    # print('curDir = %s' % os.getcwd())
    # print('nameSBF = %s' % nameSBF)
    # print('SBF = %s' % os.path.isfile(nameSBF))
    # print('maxdop = %d' % maxdop)

    # check whether the SBF datafile exists
    if not os.path.isfile(nameSBF):
        sys.stderr.write('SBF datafile %s does not exists. Exiting.\n' % nameSBF)
        sys.exit(E_FILE_NOT_EXIST)

    # # execute the conversion sbf2stf needed
    SBF2STFOPTS = ['DOP_2']     # options for conversion, ORDER IMPORTANT!!
    sbf2stfConverted = sbf2stf.runSBF2STF(nameSBF, SBF2STFOPTS, overwrite, verbose)

    for option in SBF2STFOPTS:
        # print('option = %s - %d' % (option, SBF2STFOPTS.index(option)))
        if option == 'DOP_2':
            # read the MeasEpoch data into a numpy array
            dataDOP = sbf2stf.readDOPEpoch(sbf2stfConverted[SBF2STFOPTS.index(option)], verbose)
        else:
            print('  wrong option %s given.' % option)
            sys.exit(E_WRONG_OPTION)

    # determine current weeknumber and subsequent date from SBF data
    WkNr = int(dataDOP['DOP_WNC'][0])
    dateString = gpstime.UTCFromWT(WkNr, float(dataDOP['DOP_TOW'][0])).strftime("%d/%m/%Y")
    if verbose:
        print('WkNr = %d - dateString = %s' % (WkNr, dateString))

    # create subset with only valid DOP values by checking wheteher NrSVs is strict positive
    indexValid = sbf2stf.findNrSVs(dataDOP['DOP_NrSV'], verbose)
    # indexValid = sbf2stf.findValidDOP(dataDOP['DOP_PDOP'], verbose)
    dataDOPValid = dataDOP[indexValid]
    print('dataDOPValid = %s' % dataDOPValid)
    print('dataDOPValid[0] = %s' % dataDOPValid[0])
    print('dataDOPValid[-] = %s' % dataDOPValid[-1])


    # create the xDOP/NrSVs plot
    plotDOP.plotNrSVsXDOP(dataDOPValid, maxdop)