#!/usr/bin/env python

import matplotlib.pyplot as plt
import plotConstants as mPlt
import matplotlib.dates as md
from SSN import ssnConstants as mSSN
from GNSS import gpstime


def plotLockTime(SVID, signalTypes, dataMeasSVID, lliIndices, lliTOWs, verbose):
    """
    plotLockTime creates a plot of the locktime and indicates loss of locks

    Parameters:
        SVID: satellite ID
        signalTypes: signal types to represent
        dataMeasSVID: data from MeasEpoch_2 but for one SVs
        indexLossOfLock: indices for the occurance of loss of lock
        verbose: display interactive plot
    """

    # print '\nplotLockTime' + '-' * 25
    gnssSyst, gnssSystShort, gnssPRN = mSSN.svPRN(SVID)

    for i, signalType in enumerate(signalTypes):
        print 'PLT: signalType[%d] = %s' % (i, signalType)
        print 'PLT: TOW = %s (%d)' % (dataMeasSVID[i]['MEAS_TOW'], len(dataMeasSVID[i]['MEAS_TOW']))
        print 'PLT: lockTimes = %s (%d)\n' % (dataMeasSVID[i]['MEAS_LOCKTIME'], len(dataMeasSVID[i]['MEAS_LOCKTIME']))
        print "PLT: indexLossOfLock[%d] = %s (Nr = %d)" % (i, lliIndices[i], len(lliIndices[i]))
        # myData2 = dataMeasSVID[i][lliIndices[i]]
        # print "PLT: myData2 = %s (len = %d)" % (myData2['MEAS_TOW'], len(myData2['MEAS_TOW']))
        # print "PLT: idemand = %s (len = %d)\n" % (dataMeasSVID[i][lliIndices[i]]['MEAS_TOW'], len(dataMeasSVID[i][lliIndices[i]]['MEAS_TOW']))

    # create the plot window
    # plt.style.use('BEGPIOS')
    plt.style.use('ggplot')
    plt.figure(1)
    subPlot = plt.subplot(1, 1, 1)
    # titles and axis-labels
    dateString = gpstime.UTCFromWT(float(dataMeasSVID[0]['MEAS_WNC'][0]), float(dataMeasSVID[0]['MEAS_TOW'][0])).strftime("%d/%m/%Y")
    plt.title('Lock Times for %s PRN %d (%d)' % (gnssSyst, gnssPRN, SVID))  # , fontsize='18'
    plt.ylabel('Lock Time [s]')
    plt.xlabel('Time [hh:mm] (' + dateString + ')')

    for index, signalType in enumerate(signalTypes):
        # lockTime = dataMeasSVID[index]['MEAS_LOCKTIME']
        # print "index = %d  lockTime.size = %d" % (index, len(lockTime))
        sigTypeColor = mPlt.getSignalTypeColor(signalType)

        utc = []
        for count in range(0, len(dataMeasSVID[index])):
            utc.append(gpstime.UTCFromWT(float(dataMeasSVID[index]['MEAS_WNC'][count]), float(dataMeasSVID[index]['MEAS_TOW'][count])))

        plt.plot(utc, dataMeasSVID[index]['MEAS_LOCKTIME'], color=sigTypeColor, linestyle='', markersize=0.75, marker='.')

        utc2 = []
        for count2 in range(0, len(dataMeasSVID[index][lliIndices[index]])):
            utc2.append(gpstime.UTCFromWT(float(dataMeasSVID[index][lliIndices[index]]['MEAS_WNC'][count2]), float(dataMeasSVID[index][lliIndices[index]]['MEAS_TOW'][count2])))
        plt.plot(utc2, dataMeasSVID[index][lliIndices[index]]['MEAS_LOCKTIME'], color=sigTypeColor, linestyle='', markersize=7, marker=mPlt.mFilledMarkers[signalType % len(mPlt.mFilledMarkers)])

        # annotate the plot
        annotateTxt = mSSN.GNSSSignals[signalType]['name'] + str(': %d LLI' % len(lliIndices[index]))
        subPlot.text(0.02, 0.95 - index * 0.0375, annotateTxt, verticalalignment='bottom', horizontalalignment='left', transform=subPlot.transAxes, color=sigTypeColor, fontsize=12)

    # make x-axis a hh:mm:ss
    ax = plt.gca()
    xfmt = md.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)

    # adjust range for Y axis
    axes = plt.gca()
    axes.set_ylim(mPlt.adjustYAxisLimits(axes))
    axes.set_xlim(mPlt.adjustXAxisLimits(axes))

    plt.text(0, -0.125, r'$\copyright$ Alain Muls (alain.muls@rma.ac.be)', horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes, alpha=0.5, fontsize='x-small')
    plt.text(1, -0.125, r'$\copyright$ Frederic Snyers (fredericsn@gmail.com)', horizontalalignment='right', verticalalignment='bottom', transform=ax.transAxes, alpha=0.5, fontsize='x-small')
    # mPlt.annotateText(r'$\copyright$ Alain Muls (alain.muls@rma.ac.be)', subPlot, 0, -0.12, 'left', fontsize='x-small')
    # mPlt.annotateText(r'$\copyright$ Frederic Snyers (fredericsn@gmail.com)', subPlot, 1, -0.12, 'right', fontsize='x-small')

    fig = plt.gcf()
    # fig.set_size_inches(12*2.5, 9*2.5)
    fig.savefig('%s-%s%d-locktime.png' % (gnssSyst, gnssSystShort, gnssPRN), dpi=fig.dpi)

    if verbose:
        plt.show(block=False)  # block=False)

    # close the figure
    # plt.close()
