#!/usr/bin/env python

import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib
# from pyproj import Proj

from GNSS import gpstime


def plotGEOD(dataGEODPos, dataDOP):
    plt.style.use('BEGPIOS')
    # plt.style.use('ggplot')
    # verbose = 1
    # print "datameas 0 ", dataMeasSVID[0]['MEAS_CN0']
    # print "datameas 1 ", dataMeasSVID[1]['MEAS_CN0']
    plt.figure(1)
    # f, axes = plt.subplots(2, 1)
    plt.suptitle('UTM Position', fontsize=20)

    # print "type", type(dataGEODPos)
    # print "data:", dataGEODPos[0:5]
    # print "data2:", dataGEODPos['MEAS_WNC'][0:5]
    utc = []
    # index = sbf2stf.findNanValues(dataGEODPos['Latitude'])
    # print "index: ", index[0][:]
    # if len(index) < 0:
    #     print "NO POSITION CALCULATED"
    # else:
    #     dataGEODPOSValid = dataGEODPos[index]
    # dataDOPValid = dataDOP[index]
    # print "DATA %s" % dataGEODPos
    # print "DATA %s" % dataGEODPOSValid
    for count in range(0, len(dataGEODPos)):
        utc.append(gpstime.UTCFromWT(float(dataGEODPos['GEOD_WNC'][count]), float(dataGEODPos['GEOD_TOW'][count])))

    # myProj = Proj("+proj=utm +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    # east, north = myProj(rad2deg(dataGEODPOSValid['Longitude']), rad2deg(dataGEODPOSValid['Latitude']))
    # print "EAST", east[0]
    # print "NORTH", north[0]
    # print "len data", len(dataGEODPos)
    plt.subplot(4, 1, 1)
    ax = plt.gca()
    xfmt = md.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    # EAST IS PUT IN LONGITUDE COLUMN
    plt.plot(utc, dataGEODPos['GEOD_Longitude'], label="Easting (m)", marker='.', linestyle='', markersize=1.5)
    plt.legend(shadow=True)

    plt.subplot(4, 1, 2)
    ax = plt.gca()
    xfmt = md.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
    ax.yaxis.set_major_formatter(y_formatter)
    # NORTH IS PUT IN LATITUDE COLUMN
    plt.plot(utc, dataGEODPos['GEOD_Latitude'], label="Northing (m)", marker='.', linestyle='', markersize=1.5)
    plt.legend(shadow=True)

    plt.subplot(4, 1, 3)
    ax = plt.gca()
    xfmt = md.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(utc, dataGEODPos['GEOD_Height'], label="Height (m)", marker='.', linestyle='', markersize=1.5)
    plt.legend(shadow=True)

    plt.subplot(4, 1, 4)
    ax = plt.gca()
    ax2 = ax.twinx()
    xfmt = md.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    ax.legend(shadow=True, loc=1)
    # ax2.plot(utc, dataDOPValid['PDOP']/100)
    ax.fill_between(utc, 0, dataDOP['DOP_PDOP'], label="PDOP", zorder=1)
    ax.set_ylim([0, 20])
    ax.set_ylabel('PDOP')
    ax2.plot(utc, dataGEODPos['GEOD_NrSV'], label="NrSV", marker='.', linestyle='', markersize=1.5, zorder=2)
    ax2.set_ylim([2, max(dataGEODPos['GEOD_NrSV'])+1])
    ax2.grid(True)
    ax.grid(False)

    ax2.legend(shadow=True, loc=0)
    dateString = gpstime.UTCFromWT(float(dataGEODPos['GEOD_WNC'][0]), float(dataGEODPos['GEOD_TOW'][0])).strftime("%d/%m/%Y")
    plt.xlabel('Time [hh:mm:ss] of ' + dateString)
    plt.show()
