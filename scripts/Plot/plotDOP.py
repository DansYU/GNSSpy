#!/usr/bin:env python

from math import ceil
import numpy as np
import matplotlib.pyplot as plt


def plotNrSVsXDOP(dataXDOP, maxDOP, verbose=False):
    '''
    plotNrSVsXDOP plots the observed/used number of SVs and the corresponding xDOP parameters

    Parameters:
        dataXDOP: numpy array that comes from reading the DOP_2 sbf2stf results file and with valid NrSVs detected
        maxDOP: the maximum xDOP value to display
    '''
    # plt.style.use('ggplot')
    plt.style.use('BEGPIOS')
    plt.figure(1)
    plt.title('xDOP values', fontsize='x-large')

    # loop through the DOP columns in the data file
    listXDOP = ('DOP_PDOP', 'DOP_VDOP', 'DOP_HDOP', 'DOP_TDOP')

    # define the colors
    colors = iter(plt.cm.rainbow(np.linspace(0, 1, len(listXDOP))))

    for i, xDOP in enumerate(listXDOP):
        # clean the xDOP data column by eliminating all data == 65535
        indicesOK = np.where(dataXDOP[xDOP] != 65535 and np.where(dataXDOP[xDOP] != np.nan))
        dataXDOPvalid = dataXDOP[xDOP][indicesOK]
        maxXDOP = int(ceil(max(dataXDOPvalid)))
        print('max(dataXDOPvalid) = %f - ceil = %f' % (max(dataXDOPvalid), maxXDOP))
        plt.plot(dataXDOP['DOP_TOW'][indicesOK], dataXDOPvalid, color=next(colors), marker='.', markersize=1, linestyle='None')

    ax = plt.gca()
    ax.set_ylim(0, min(maxDOP, maxXDOP))
    plt.show()
