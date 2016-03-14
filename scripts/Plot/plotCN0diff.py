#!/usr/bin/env python

import pylab
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.cm as cm
import sys

from SSN import ssnConstants as mSSN
from GNSS import gpstime
# import ggplot2


def TOW2UTC(WkNr, TOW):
    '''
    TOW2UTC transforms an list expressed in TOW to UTC list

    Parameters:
        WkNr: week number of TOW
        TOW: list of TOWs to transform

    Return:
        UTC: list of UTCs
    '''
    # transform TOW to UTC representation
    UTC = []
    for i in range(0, len(TOW)):
        UTC.append(gpstime.UTCFromWT(float(WkNr), float(TOW[i])))
    print("UTC = %s to %s" % (UTC[0], UTC[-1]))

    return UTC


def plotCN0diff(listSVIDs, listST, spanUTC, CN0measdiff, dateStr, verbose=False):
    '''
    plotCN0 plots the CN0 values for SVs per signalType observed
    Parameters:
        listSVIDs is list of SVIDs we have data for
        listST is list of signaltypes
        spanUTC is the UTC representation of spanElevation
        CN0measdiff contains observed CN0 variation for all SVs and all signalTypes
        dateStr is the respective day of observations
    '''

    # get unique list of signaltypes to determine the number of plots we have to make
    uniqSVs = list(set(listSVIDs))
    for i, uniqSVi in enumerate(uniqSVs):
            plt.figure(i)
            ax = plt.gca()

            # create label for signalType and plot its SN0 for this uniqSVi
            stLabel = []
            ax.set_color_cycle(['purple', 'black', 'green', 'cyan', 'violet'])

            for j, SVj in enumerate(listSVIDs):
                if SVj == uniqSVi:
                    stLabel.append(mSSN.GNSSSignals[listST[j]]['name'])
                    print('mSSN.GNSSSignals[listST[%d]][name] = %s' % (j, mSSN.GNSSSignals[listST[j]]['name']))
                    print('spanUTC = %s  ==>  %s' % (spanUTC[0], spanUTC[-1]))
                    print(len(spanUTC), len(CN0measdiff[j]))
                    plt.plot(spanUTC, CN0measdiff[j], linestyle='-', linewidth=0.25, alpha=0.75, label=stLabel[-1])
                    ax.set_ylim(-3, 3)
                    # plot annotation
                    gnssSyst, gnssSystShort, gnssPRN = mSSN.svPRN(SVj)
                    textSVID = gnssSystShort + str(gnssPRN)
                    print('j = %d - SV = %s,  uniqSVi = %s\n' % (i, textSVID, uniqSVi))

                    plt.title('Satellite: %s' % textSVID)
                    plt.xlabel('Time of ' + dateStr)
                    plt.ylabel('C/N0 variation')

            # adjust the X-axis to represent readable time
            ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M:%S'))
            plt.xlim(spanUTC[0], spanUTC[-1])

            # annotate for copyright
            plt.text(0, -0.125, r'$\copyright$ Alain Muls (alain.muls@rma.ac.be)', horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes, alpha=0.5, fontsize='x-small')
            plt.text(1, -0.125, r'$\copyright$ Andrei Alexandru (andrei.alex.toma@gmail.com)', horizontalalignment='right', verticalalignment='bottom', transform=ax.transAxes, alpha=0.5, fontsize='x-small')

            # Shrink current axis's height by x% on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.4,
                             box.width, box.height * 0.6])
            box = ax.get_position()

            plt.legend(bbox_to_anchor=(box.x0 + box.width*0.2, -0.15, box.width*0.6, 0.15), loc='lower center', ncol=np.size(stLabel), fontsize='xx-small')
            llines = plt.gca().get_legend().get_lines()  # all the lines.Line2D instance in the legend
            plt.setp(llines, linewidth=4)      # the legend linewidth
            plt.tight_layout(rect=(0, 0, 1, 1))

            # Shrink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax = plt.subplot(111)
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width, box.height * 0.9])
            fig = plt.gcf()
            fig.savefig('%s-%s%d-CN0.png' % (gnssSyst, gnssSystShort, gnssPRN), dpi=fig.dpi)
            if i != len(uniqSVs)-1:
                if verbose:
                    plt.show(block=False)
            else:
                if verbose:
                    plt.show()
            # close the figure
            plt.close()