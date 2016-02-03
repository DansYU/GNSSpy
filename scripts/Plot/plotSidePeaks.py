#!/usr/bin/env python

import matplotlib.pyplot as plt
import plotConstants as mPlt
import matplotlib.dates as md
from SSN import ssnConstants as mSSN
from GNSS import gpstime


def plotSidePeaks(SVID, signalTypesSVID, WkNr, iTOW, deltaPR, sidePeaksTOW, sidePeakDPR, jumpDPRNear97Indices, jumpDPRNear1465Indices, lliTOWs, strDate, verbose):
    """
    plotSidePeaks plots the difference between the code measurements on L1A (reference) and E6A and indicates where a possible side peak is noticed

    Parameters:
        SVID: SSN SVID of satellite
        signalTypesSVID; the signal types for this SVID
        WkNt: week number
        iTOW: common TOWs where both code measurements are available
        deltaPR: difference between PR on L1A and E61
        sidePeaksTOW: list of TOWs which could be indicators of SidePeaks
        sidePeakDPR: delta PR at these TOWs
        jumpDPRNear97Indices: indices in sidePeaksTOW, sidePeakDPR which are closest to integer multipe of 9.7m
        jumpDPRNear1465Indices: indices in sidePeaksTOW, sidePeakDPR which are closest to integer multipe of 14.65m
        lliTOWs: TOW that indicate a loss of lock per signal type
        strDate: observation date
        verbose: ok
    """
    print '-' * 50

    # get info for GNSS satellite
    gnssSyst, gnssSystShort, gnssPRN = mSSN.svPRN(SVID)
    SVIDColor = mPlt.getSVIDColor(SVID)

    # create the plot window
    # plt.style.use('BEGPIOS')
    plt.style.use('ggplot')

    plt.figure(2)
    subPlot = plt.subplot(1, 1, 1)
    # titles and axis-labels
    plt.title('Side Peak Indicator for %s PRN %d (%d)' % (gnssSyst, gnssPRN, SVID))  # , fontsize='18'
    plt.ylabel(r'$\Delta$ PR (%s - %s)' % (mSSN.GNSSSignals[16]['name'], mSSN.GNSSSignals[18]['name']))
    plt.xlabel('Time [hh:mm] (' + strDate + ')')

    # plot the deltaPRs vs iTOW
    print 'iTOW = %s (%d)' % (iTOW, len(iTOW))
    print 'deltaPR = %s (%d)' % (deltaPR, len(deltaPR))

    # plot the indicators for the sidepeaks after conversion to utc
    utc2 = []  # used for all possible detections
    utc3 = []  # used for those that are multiple of 9.7m
    utc4 = []  # used for those that are multiple of 14.65m
    for count in range(0, len(sidePeaksTOW)):
        utc2.append(gpstime.UTCFromWT(float(WkNr), float(sidePeaksTOW[count])))
        if count in jumpDPRNear97Indices:
            utc3.append(utc2[-1])
        if count in jumpDPRNear1465Indices:
            utc4.append(utc2[-1])

    plt.plot(utc2, sidePeakDPR, color='orange', linestyle='', markersize=7, marker='o', markeredgecolor='orange', markerfacecolor=None)
    print 'utc2 = %s (#%d)' % (utc2, len(utc2))
    print 'sidePeakDPR = %s (#%d)' % (sidePeakDPR, len(sidePeakDPR))
    print 'jumpDPRNear97Indices = %s (#%d)' % (jumpDPRNear97Indices, len(jumpDPRNear97Indices))
    print 'sidePeakDPR = %s (#%d)' % (sidePeakDPR[jumpDPRNear97Indices], len(sidePeakDPR[jumpDPRNear97Indices]))
    print 'utc3 = %s (#%d)' % (utc3, len(utc3))

    plt.plot(utc3, sidePeakDPR[jumpDPRNear97Indices], color='red', linestyle='', markersize=7, marker='o', markeredgecolor='red', markerfacecolor=None)
    plt.plot(utc4, sidePeakDPR[jumpDPRNear1465Indices], color='blue', linestyle='', markersize=7, marker='o', markeredgecolor='blue', markerfacecolor=None)

    # annotate to signal number of detections and number of integer multiple of 9.7m
    annotateTxt = 'Side Peaks on E1A: %d' % len(utc3)
    subPlot.text(0.95, 0.95, annotateTxt, verticalalignment='bottom', horizontalalignment='right', transform=subPlot.transAxes, color='red', fontsize=12)

    # annotate to signal number of detections and number of integer multiple of 14.65m
    annotateTxt = 'Side Peaks on E6A: %d' % len(utc4)
    subPlot.text(0.95, 0.92, annotateTxt, verticalalignment='bottom', horizontalalignment='right', transform=subPlot.transAxes, color='blue', fontsize=12)

    annotateTxt = 'Other: %d' % (len(utc2) - len(utc3) - len(utc4))
    subPlot.text(0.95, 0.89, annotateTxt, verticalalignment='bottom', horizontalalignment='right', transform=subPlot.transAxes, color='orange', fontsize=12)

    # transform WkNr, TOW to UTC time
    utc = []
    for i in range(0, len(iTOW)):
        utc.append(gpstime.UTCFromWT(float(WkNr), float(iTOW[i])))

    # plot the deltaPR vs UTC time
    plt.plot(utc, deltaPR, color=SVIDColor, linestyle='-', linewidth=0.5, marker='.', markersize=3.5)  # , linestyle='', marker='.', markersize=1)

    for i, lliTOWsST in enumerate(lliTOWs):
        print 'lliTOWs[%d] = %s' % (i, lliTOWsST)
        utc2 = []
        sigTypeColor = mPlt.getSignalTypeColor(signalTypesSVID[i])
        # annotate the plot
        annotateTxt = mSSN.GNSSSignals[signalTypesSVID[i]]['name'] + ' LLI'
        subPlot.text(0.02, 0.95 - i * 0.0375, annotateTxt, verticalalignment='bottom', horizontalalignment='left', transform=subPlot.transAxes, color=sigTypeColor, fontsize=12)
        # drax vertical line for the LLI indicators
        for j, lliTOWST in enumerate(lliTOWsST):
            utc2.append(gpstime.UTCFromWT(float(WkNr), lliTOWST))
            # print 'lliTOWs[%d] = %s utc = %s' % (j, lliTOWST, utc2[j])
            # draw a vertical line in the color of the signal type
            plt.axvline(utc2[j], color=sigTypeColor)

    print 'sidePeaksTOW = %s (%d)' % (sidePeaksTOW, len(sidePeaksTOW))
    # print 'utc2 = %s (%d)' % (utc2, len(utc2))

    # plt.plot(sidePeaksTOW, 0.5, color='red', linestyle='', markersize=7, marker=mPlt.mFilledMarkers[SVID % len(mPlt.mFilledMarkers)])

    # adjust the axes to represent hh:mm:ss
    ax = plt.gca()
    xfmt = md.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)

    # adjust range for Y axis
    axes = plt.gca()
    axes.set_ylim(mPlt.adjustYAxisLimits(axes))
    axes.set_xlim(mPlt.adjustXAxisLimits(axes))

    plt.text(0, -0.125, r'$\copyright$ Alain Muls (alain.muls@rma.ac.be)', horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes, alpha=0.5, fontsize='x-small')
    plt.text(1, -0.125, r'$\copyright$ Frederic Snyers (fredericsn@gmail.com)', horizontalalignment='right', verticalalignment='bottom', transform=ax.transAxes, alpha=0.5, fontsize='x-small')

    fig = plt.gcf()
    # fig.set_size_inches(12*2.5, 9*2.5)
    fig.savefig('%s-%s%d-sidepeak.png' % (gnssSyst, gnssSystShort, gnssPRN), dpi=fig.dpi)

    if verbose:
        plt.show()

    # close the figure
    plt.close()
    print '-' * 50
