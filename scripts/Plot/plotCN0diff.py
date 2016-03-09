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


def suplabel(axis, label, label_prop=None, labelpad=3, ha='center', va='center'):
    '''
    Add super ylabel or xlabel to the figure
    Similar to matplotlib.suptitle
        axis       - string: "x" or "y"
        label      - string
        label_prop - keyword dictionary for Text
        labelpad   - padding from the axis (default: 5)
        ha         - horizontal alignment (default: "center")
        va         - vertical alignment (default: "center")
    '''
    fig = pylab.gcf()
    xmin = []
    ymin = []
    for ax in fig.axes:
        xmin.append(ax.get_position().xmin)
        ymin.append(ax.get_position().ymin)
    xmin, ymin = min(xmin), min(ymin)
    dpi = fig.dpi
    if axis.lower() == "y":
        rotation = 90.
        x = xmin-float(labelpad)/dpi
        y = 0.5
    elif axis.lower() == 'x':
        rotation = 0.
        x = 0.5
        y = ymin - float(labelpad)/dpi
    else:
        raise Exception("Unexpected axis: x or y")
    if label_prop is None:
        label_prop = dict()
    pylab.text(x, y, label, rotation=rotation,
               transform=fig.transFigure,
               ha=ha, va=va,
               **label_prop)


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


def plotCN0diff(listSVIDs, listST, spanUTC, CN0meas, dateStr, verbose=False):
    '''
    plotCN0 plots the CN0 values for SVs per signalType observed
    Parameters:
        listSVIDs is list of SVIDs we have data for
        listST is list of signaltypes
        spanUTC is the UTC representation of spanElevation
        CN0meas contains observed CN0 for all SVs and all signalTypes
    '''
    # plt.style.use('ggplot')
    # plt.style.use('BEGPIOS')

    # first plot all SVs per signalType
    # get unique list of signaltypes to determine the number of plots we have to make
    uniqSTs = list(set(listST))
    # print('uniqSTs = %s' % uniqSTs)

    # loop over the signalTypes
    for i, uniqSTi in enumerate(uniqSTs):
        plt.figure(i)
        ax = plt.gca()
        ax.set_color_cycle(['purple', 'black', 'green', 'cyan', 'violet'])
        # create label for identify SV and plot its CN0 variation for this signalType
        satLabel = []
        for j, STj in enumerate(listST):
            if STj == uniqSTi:
                satLabel.append(mSSN.svPRN(listSVIDs[j])[1] + str(mSSN.svPRN(listSVIDs[j])[2]))
                plt.plot(spanUTC, CN0meas[j], linestyle='-', linewidth=0.5, alpha=0.75, label=satLabel[-1])
                ax.set_ylim(-10, 10)
        print('i = %d  len = %d' % (i, np.size(uniqSTs)))

        # plot annotation
        plt.title('Signaltype: %s' % mSSN.GNSSSignals[uniqSTi]['name'], fontsize='x-large')
        plt.xlabel('Time of ' + dateStr)
        plt.ylabel('C/N0 diff')
        # adjust the X-axis to represent readable time
        ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M:%S'))
        plt.xlim(spanUTC[0], spanUTC[-1])
        # annotate for copyright
        plt.text(0, -0.125, r'$\copyright$ Alain Muls (alain.muls@rma.ac.be)', horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes, alpha=0.5, fontsize='x-small')
        # Shrink current axis's height by x% on the bottom
        box = ax.get_position()
        # print('box.x0     = %f' % box.x0)
        # print('box.y0     = %f' % box.y0)
        # print('box.width  = %f' % box.width)
        # print('box.height = %f' % box.height)

        # ax = plt.subplot(111)
        ax.set_position([box.x0, box.y0 + box.height * 0.3,
                         box.width, box.height * 0.7])
        box = ax.get_position()
        # print('after\nbox.x0     = %f' % box.x0)
        # print('box.y0     = %f' % box.y0)
        # print('box.width  = %f' % box.width)
        # print('box.height = %f' % box.height)

        # plot legend
        plt.legend(bbox_to_anchor=(box.x0 + box.width*0.2, -0.15, box.width*0.6, 0.15), loc='lower center', ncol=np.size(satLabel), fontsize='xx-small')
        llines = plt.gca().get_legend().get_lines()  # all the lines.Line2D instance in the legend
        plt.setp(llines, linewidth=4)      # the legend linewidth
        # ggplot2.rstyle(ax)

        fig = plt.gcf()
        if verbose:
            print('\nfigname = %s -- %s' % (STj, mSSN.GNSSSignals[uniqSTi]['name']))
        fig.savefig('%s-CN0.png' % (mSSN.GNSSSignals[uniqSTi]['name']), dpi=fig.dpi)

        if i != len(uniqSTs) - 1:
            if verbose:
                plt.show(block=False)
        else:
            if verbose:
                plt.show()
    plt.close()