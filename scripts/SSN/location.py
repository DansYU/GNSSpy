#!/usr/bin/env python

# location searchs in PATH for existence of program
import sys                      # import module sysimport os
from sys import platform
import os                       # getting to the OS

E_SUCCESS = 0
E_NOT_IN_PATH = 1


def whereis(program):
    """
    Search whether a program is in the $PATH

    Parameters:
        program         program to serach for in the $PATH

    Returns
        if program found, returns the full path to it
        else None returned
    """
    # print 'program = ' + program
    # print 'PATH = '
    # print os.environ.get('PATH').split(':')

    # if platform == "linux" or platform == "linux2":
    #     print('linux')
    # elif platform == "darwin":
    #     print('MAC OS X')
    # elif platform == "win32":
    #     print('Windows')
    if platform == "win32":
        filename, file_extension = os.path.splitext(program)
        # print('%s   %s' % (filename, file_extension))
        if file_extension != '.exe' or file_extension != '.com':
            program = program + '.exe'

    for path in os.environ.get('PATH', '').split(os.pathsep):
        exeProgram = os.path.join(path, program)
        if os.path.exists(exeProgram) and not os.path.isdir(exeProgram) and os.access(exeProgram, os.X_OK):
            # print 'found path = ' + path
            return exeProgram
    # not found, so display this
    user_paths = os.environ['PATH'].split(os.pathsep)
    sys.stderr.write('program %s not found in PATH %s' % (program, user_paths))
    return None


# main starts here
if __name__ == '__main__':
    # print 'in location'
    location = whereis('sbf2stf')
    if location is not None:
        print(location)
        sys.exit(E_SUCCESS)
    else:
        sys.exit(E_NOT_IN_PATH)
