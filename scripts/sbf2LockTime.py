#!/usr/bin/env python

import sys
import os
import numpy as np
import argparse

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
# print sys.argv[0], ospath


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

    # # show values
    # print ('SBFFile: %s' % args.file)
    # print ('dir = %s' % args.dir)
    # print ('verbose: %s' % args.verbose)
    # print ('overwrite: %s' % args.overwrite)

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

    # print ('workDir = %s' % workDir)
    if not os.path.exists(workDir):
        sys.stderr.write('Directory %s does not exists. Exiting.\n' % workDir)
        sys.exit(E_DIR_NOT_EXIST)
    else:
        if os.chdir(workDir) is False:
            sys.exit('Problem changing to directory %s. Exiting.\n' % workDir)

    # print ('curDir = %s' % os.getcwd())
    # print ('SBF = %s' % os.path.isfile(nameSBF))

    # check whether the SBF datafile exists
    if not os.path.isfile(nameSBF):
        sys.stderr.write('SBF datafile %s does not exists. Exiting.\n' % nameSBF)
        sys.exit(E_FILE_NOT_EXIST)
