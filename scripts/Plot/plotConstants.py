#!/usr/bin/env python

from matplotlib.lines import Line2D
from matplotlib import colors
import numpy as np
import six


mFilledMarkers = []
for m in Line2D.filled_markers:
    try:
        if len(m) == 1 and m != ' ':
            mFilledMarkers.append(m)
    except TypeError:
        pass

mMarkers = []
for m in Line2D.markers:
    try:
        if len(m) == 1 and m != ' ':
            mMarkers.append(m)
    except TypeError:
        pass

colors_ = list(six.iteritems(colors.cnames))
# Transform to hex color values.
hex_ = [color[1] for color in colors_]
# Get the rgb equivalent.
rgbColors = [colors.hex2color(color) for color in hex_]


def adjustYAxisLimits(axes, factor=0.05):
    """
    adjust the lower/upper limit of the Y axis by factor and uses unit for the ticks

    Parameters:
        axes: the axes of the plot
        factor: expresses in percentages what to add at top/bottom of Y axis

    Returns:
        yNewLimit: the new limits for the Y axis
    """
    # range for axis
    yCurLimit = axes.get_ylim()
    # print 'yCurLimit = %f, %f' % (yCurLimit[0], yCurLimit[1])

    # new limit
    yNewLimit = (yCurLimit[0] + yCurLimit[1])/2 + np.array((-0.5, 0.5)) * (yCurLimit[1] - yCurLimit[0]) * (1 + factor)
    # print 'yNewLimit = %f, %f' % (yNewLimit[0], yNewLimit[1])

    return yNewLimit


def adjustXAxisLimits(axes, factor=0.05):
    """
    adjust the lower/upper limit of the x axis by factor and uses unit for the ticks

    Parameters:
        axes: the axes of the plot
        factor: expresses in percentages what to add at top/bottom of x axis

    Returns:
        xNewLimit: the new limits for the x axis
    """
    # range for axis
    xCurLimit = axes.get_xlim()
    # print 'xCurLimit = %f, %f' % (xCurLimit[0], xCurLimit[1])

    # new limit
    xNewLimit = (xCurLimit[0] + xCurLimit[1])/2 + np.array((-0.5, 0.5)) * (xCurLimit[1] - xCurLimit[0]) * (1 + factor)
    # print 'xNewLimit = %f, %f' % (xNewLimit[0], xNewLimit[1])

    return xNewLimit


def annotateText(annotateString, subPlot, xLoc=0, yLoc=0, ha='left', va='bottom'):
    """
    annotateText prints the date string DD/MM/YYYY at the location specified (axes values for from 0,0 to 1,1)

    Parameters:
        annotateString: string with date to print
        subPlot: number of the sub-plot
        xLoc: location on X-axis
        yLoc: location on Y-axis
        ha, va: what type of alignment to use
    """
    subPlot.text(xLoc, yLoc, annotateString, transform=subPlot.transAxes, fontsize=10, horizontalalignment=ha, verticalalignment=va, color='0.55')


def getSignalTypeColor(signalType):
    '''
    getSignalTypeColor gets the color for the signal type

    Parameters:
        signalType: signal type number

    Returns:
        color according to this signalType
    '''
    return rgbColors[signalType % len(rgbColors)]


def getSVIDColor(SVID):
    '''
    getSVIDColor gets the color for the satellite SVID

    Parameters:
        SVID: SV PRN number SSN convention

    Returns:
        color according to the SVID
    '''

    return rgbColors[SVID % len(rgbColors)]
