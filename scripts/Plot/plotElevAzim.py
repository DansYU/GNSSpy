#!/usr/bin/env python

from matplotlib.pyplot import rc, grid, figure, rcParams, show, text
# from matplotlib import style
import matplotlib as plt
import numpy as np
from math import radians

from GNSS import gpstime
from SSN import ssnConstants as mSSN


def skyview(PRNs, azimuths, elevations, dateStr, hours, hoursAzims, hoursElevs):
    '''
    skyview creates the skyview plot for observed satellites
    Parameters:
        PRNs is list of PRNs of observed satellites
        azimuths is aziumuts with which these satellites were observed (in degrees)
        elevations is elevation angle with which these satellites were observed (in degrees)
        dateStr contains the current date
        hours contain the TOWs that correspond to a multiple of hours
        hoursAzims, hoursElevs contain the corersponding azimuth/elevation (in degrees)
    Returns:
        fig is reference to created plot
    '''
    plt.style.use('BEGPIOS')

    # rc('grid', color='#999999', linewidth=1, linestyle='-', alpha=[0].6)
    rc('xtick', labelsize='x-small')
    rc('ytick', labelsize='x-small')

    # force square figure and square axes looks better for polar, IMO
    width, height = rcParams['figure.figsize']
    size = min(width, height)

    # make a square figure
    fig = figure(figsize=(size, size))

    # set the axis (0 azimuth is North direction, azimuth indirect angle)
    ax = fig.add_axes([0.10, 0.15, 0.8, 0.8], projection=u'polar')  # , axisbg='#CCCCCC', alpha=0.6)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    # Define the xticks
    ax.set_xticks(np.linspace(0, 2 * np.pi, 13))
    xLabel = ['N', '30', '60', 'E', '120', '150', 'S', '210', '240', 'W', '300', '330']
    ax.set_xticklabels(xLabel)

    # Define the yticks
    ax.set_yticks(np.linspace(0, 90, 7))
    yLabel = ['', '75', '60', '45', '30', '15', '']
    ax.set_yticklabels(yLabel)

    # annotate for copyright and put the currecnt date
    text(-0.1, 1, dateStr, horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes, fontsize='large')
    text(1.1, 1, r'$\copyright$ Alain Muls (alain.muls@rma.ac.be)', horizontalalignment='right', verticalalignment='bottom', transform=ax.transAxes, alpha=0.5, fontsize='x-small')

    # draw a grid
    grid(True)

    # treat the sky track of the satellites
    # for (PRN, E, Az) in sat_positions:
    #     ax.annotate(str(PRN),
    #                 xy=(radians(Az), 90-E),  # theta, radius
    #                 bbox=dict(boxstyle="round", fc='green', alpha=0.5),
    #                 horizontalalignment='center',
    #                 verticalalignment='center')

    # plot the skytracks for each PRN
    colors = iter(plt.cm.rainbow(np.linspace(0, 1, len(PRNs))))
    satLabel = []
    for i, prn in enumerate(PRNs):
        gnssSyst, gnssSystShort, gnssPRN = mSSN.svPRN(prn)

        satLabel.append('%s%d (%d)' % (gnssSystShort, gnssPRN, prn))
        azims = [radians(az) for az in azimuths[i]]
        elevs = [(90 - el) for el in elevations[i]]
        # print('PRN = %d' % prn)
        # print('elev = %s' % elevs)
        # print('azim = %s' % azims)
        # ax.plot(azims, elevs, color=next(colors), linewidth=0.35, alpha=0.85, label=satLabel[-1])
        ax.plot(azims, elevs, color=next(colors), marker='.', markersize=1, linestyle='None', alpha=0.85, label=satLabel[-1])

        # annotate with the hour labels
        hrAzims = [radians(az + 2) for az in hoursAzims[i]]
        hrElevs = [(90 - el) for el in hoursElevs[i]]
        for j, hr in enumerate(hours[i]):
            hrAz = hrAzims[j]
            hrEl = hrElevs[j]
            # print('hr = %s' % hr)
            hr = int((np.fmod(hr, gpstime.secsInDay)) / 3600.)
            # print('hr = %s' % hr)
            # print('hrAz = %d' % hrAz)
            # print('hrEl = %d' % hrEl)
            text(hrAz, hrEl, hr, fontsize='x-small')

    # adjust the legend location
    mLeg = ax.legend(bbox_to_anchor=(0.5, -0.15), loc='lower center', ncol=np.size(satLabel), fontsize='small', markerscale=4)
    for legobj in mLeg.legendHandles:
        legobj.set_linewidth(5.0)

    # needed for having radial axis span from 0 => 90 degrees and y-labels along north axis
    ax.set_rmax(90)
    ax.set_rmin(0)
    ax.set_rlabel_position(0)

    return fig


# main starts here
if __name__ == '__main__':
    # sat_positions = [[1, 30, 0], [2, 60, 90], [3, 30, 180], [4, 50, 270]]

    svPRN = []
    prnElev = []
    prnAzim = []
    azimRad = []
    prnHour = []
    prnHourElev = []
    prnHourAzim = []

    svPRN.append(18)
    svPRN.append(20)

    elev = [20, 21, 23, 25, 20, 15, 6]
    azim = [300, 302, 305, 308, 312, 316, 322]
    prnElev.append(elev)
    prnAzim.append(azim)
    prnHour.append([194400., 208800.])
    prnHourElev.append([52, 4])
    prnHourAzim.append([211, 15])

    azimRad = []
    elev = [40, 41, 43, 45, 40, 15, 6]
    azim = [150, 154, 155, 158, 162, 166, 170]
    prnElev.append(elev)
    prnAzim.append(azim)
    prnHour.append([230400., 172800.])
    prnHourElev.append([52, 4])
    prnHourAzim.append([227, 12])

    for i, prn in enumerate(svPRN):
        print('PRN = %d' % prn)
        print('elev = %s' % prnElev[i])
        print('azim = %s' % prnAzim[i])
        print('prnHour = %s' % prnHour)
        print('prnHourAzim = %s' % prnHourAzim)
        print('prnHourElev = %s' % prnHourElev)

    fig = skyview(svPRN, prnAzim, prnElev, '21/3/2015', prnHour, prnHourAzim, prnHourElev)
    # fig = skyview(sat_positions)
    fig.savefig('plotElevAzim.png')
    # show the plot
    show()
