#!/usr/bin/env python

import pylab
import matplotlib.pyplot as plt
import matplotlib.dates as md
import plotConstants as mPlt
import ssnConstants
import gpstime

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

def plotRange(SVID, signalTypes, georange, pseudorange, Last):
    """
    plot Geometrical range vs Pseudorange per satellite and signaltype

    """
    # plt.style.use('BEGPIOS')
    plt.style.use('ggplot')
    plt.figure(1)

    plt.suptitle('Geometrical range vs Pseudorange as function of satellite and signaltype', fontsize=20)

    subPlots = []
    for index, signalType in enumerate(signalTypes):
        subPlots.append(plt.subplot(len(signalTypes), 1, index+1))
        # utcgeo = []
        # print "time geo:", pseudorange[index][0]
        print len(georange[index][1])
        print len(pseudorange[index][1])
        DIFF = []
        for counter in range(0, len(georange[index][1])):
            DIFF.append(georange[index][1][counter]-pseudorange[index][1][counter]/1000)
        plt.plot(georange[index][0], DIFF,
                 label='geo - pr ' + str(ssnConstants.svPRN(SVID)[1]) + str(ssnConstants.svPRN(SVID)[2]))

        # plt.plot(georange[index][0], georange[index][1],
        #          label='delta range ' + str(ssnConstants.svPRN(SVID)[1]) + str(ssnConstants.svPRN(SVID)[2]))
        # plt.plot(pseudorange[index][0], pseudorange[index][1]/1000,
        #          label='pseudorange of: ' + str(ssnConstants.svPRN(SVID)[1]) + str(ssnConstants.svPRN(SVID)[2]))

        # for count in range(0, len(dataMeasSVID[index])):
        #     utc.append(gpstime.UTCFromWT(float(georange[index]['MEAS_WNC'][count]), float(dataMeasSVID[index]['MEAS_TOW'][count])))
        #     # utc.append(str(gpstime.UTCFromWT(float(weeknr[count]), float(tow[count])).time()))

    if Last == 1:
        # mPlt.annotateText(r'$\copyright$ Alain Muls (alain.muls@rma.ac.be)', subPlots[index], 0, -0.22, 'left')
        # mPlt.annotateText(r'$\copyright$ Frederic Snyers (fredericsn@gmail.com)', subPlots[index], 1, -0.22, 'right')
        mPlt.text(0, -0.125, r'$\copyright$ Alain Muls (alain.muls@rma.ac.be)', horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes, alpha=0.5, fontsize='x-small')
        mPlt.text(1, -0.125, r'$\copyright$ Frederic Snyers (fredericsn@gmail.com)', horizontalalignment='right', verticalalignment='bottom', transform=ax.transAxes, alpha=0.5, fontsize='x-small')

        leg = plt.legend(shadow=True, bbox_to_anchor=(1.01, 1), loc=3)
        dateString = georange[index][0][0].strftime("%d/%m/%Y")
        plt.xlabel('Time [hh:mm:ss] of ' + dateString)
        suplabel('y', 'geo - pseudo (km)')
        # plt.ylabel('geo - pseudo (km)')
        plt.show()
