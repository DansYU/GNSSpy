#!/usr/bin/env python
import sys
import os
import numpy as np
import argparse
import matplotlib.pyplot as plt

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
    helpTxt = os.path.basename(__file__) + 'creates plots with time values until the jamming is detected'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)
    parser.add_argument('-f', '--file', help='Name of CSV file', required=True)
    parser.add_argument('-d', '--dir', help='Directory of CSV file, defaults to current', required=False, default='.')
    args = parser.parse_args()

    return args.file, args.dir

if __name__ == "__main__":
    # treat command line options
    nameCSV, dirCSV = treatCmdOpts(sys.argv)

    # change to the directory dirCSV if it exists
    workDir = os.getcwd()
    if dirCSV is not '.':
        workDir = os.path.normpath(os.path.join(workDir, dirCSV))

    if not os.path.exists(workDir):
        sys.stderr.write('Directory %s does not exists. Exiting.\n' % workDir)
        sys.exit(E_DIR_NOT_EXIST)
    else:
        os.chdir(workDir)

    # check whether the CSV datafile exists
    if not os.path.isfile(nameCSV):
        sys.stderr.write('SBF datafile %s does not exists. Exiting.\n' % nameCSV)
        sys.exit(E_FILE_NOT_EXIST)

    # preparing CSV file
    JammingPower = []
    SvName = []
    DeltaStart = []
    DeltaStop = []
    colNamesCSV = ('POWER', 'SV_ST', 'DELTA_START', 'DELTA_STOP')

    dataCSV = np.genfromtxt(nameCSV, delimiter=",", skip_header=1, dtype=None, names=colNamesCSV)
    for i in dataCSV['POWER']:
        JammingPower.append(i)
    for i in dataCSV['SV_ST']:
        SvName.append(i)
    for i in dataCSV['DELTA_START']:
        DeltaStart.append(i)
    for i in dataCSV['DELTA_STOP']:
        DeltaStop.append(i)

    # calculating number of subplots
    count = 0
    for i in range(len(JammingPower)):
        if not JammingPower[i] == 0:
            count += 1
    CrtNrStart = -1
    CrtNrStop = 0

    SvNameUniq = list(SvName[0:(len(JammingPower) / count)])
    yCrt = []
    for _ in range(count):
        yCrt.extend(range(len(SvNameUniq)))

    # creating subplots
    fig = plt.figure(1)
    fig.suptitle('Seconds until dropping                          Seconds until recovering')
    for i in range(len(JammingPower)):
        if not JammingPower[i] == 0:
            CrtNrStart += 2
            plt.subplot(count, 2, CrtNrStart)
            ax = plt.gca()
            ax.set_xlim(0, np.amax(DeltaStart) + 0.25)
            ax.set_ylim(0, np.amax(yCrt) + 0.5)
            plt.ylabel('%s dbm' % JammingPower[i])
            plt.grid()
        plt.plot(DeltaStart[i], yCrt[i] + 0.25, 'bo')
        start, end = ax.get_ylim()
        ax.set_yticklabels(SvNameUniq)
        plt.setp(ax.get_xticklabels(), fontsize=7)
        plt.setp(ax.get_yticklabels(), fontsize=10)
        ax.yaxis.set_ticks(np.arange(start + 0.25, end, 1))
    for i in range(len(JammingPower)):
        if not JammingPower[i] == 0:
            CrtNrStop += 2
            plt.subplot(count, 2, CrtNrStop)
            ax = plt.gca()
            ax.set_xlim(0, np.amax(DeltaStop) + 0.25)
            ax.set_ylim(0, np.amax(yCrt) + 0.5)
            plt.grid()
        plt.plot(DeltaStop[i], yCrt[i] + 0.25, 'bo')
        start, end = ax.get_ylim()
        plt.setp(ax.get_xticklabels(), fontsize=7)
        ax.set_yticklabels([])
        ax.yaxis.set_ticks(np.arange(start + 0.25, end, 1))
    plt.show()
    fig.savefig(os.path.splitext(nameCSV)[0], dpi=fig.dpi)