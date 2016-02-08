#!/usr/bin/env python

from GNSS import gnss

# define an instance of class GNSS
mGNSS = gnss.GNSS()

# GNSSSIgnals is dict for getting full name, freq, ...
GNSSSignals = {0: {'name': 'GPS_L1-CA', 'freq': str(mGNSS.fGPS_L1)},
               1: {'name': 'GPS_L1-P(Y)', 'freq': str(mGNSS.fGPS_L1)},
               2: {'name': 'GPS_L2-P(Y)', 'freq': str(mGNSS.fGPS_L2)},
               3: {'name': 'GPS_L2C', 'freq': str(mGNSS.fGPS_L2)},
               4: {'name': 'GPS_L5', 'freq': str(mGNSS.fGPS_L5)},
               8: {'name': 'GLO_L1-CA'},
               9: {'name': 'GLO_L1-P'},
               10: {'name': 'GLO_L2-P'},
               11: {'name': 'GLO_L2-CA'},
               16: {'name': 'GAL_L1A', 'freq': str(mGNSS.fGAL_E1A)},
               17: {'name': 'GAL_L1BC', 'freq': str(mGNSS.fGAL_E1BC)},
               18: {'name': 'GAL_E6A', 'freq': str(mGNSS.fGAL_E6A)},
               19: {'name': 'GAL_E6BC', 'freq': str(mGNSS.fGAL_E6BC)},
               20: {'name': 'GAL_E5a', 'freq': str(mGNSS.fGAL_E5A)},
               21: {'name': 'GAL_E5b', 'freq': str(mGNSS.fGAL_E5B)},
               22: {'name': 'GAL_E5', 'freq': str(mGNSS.fGAL_E5)}
               }

# names and format for MeasEpoch_2
colNamesMeasEpoch = ('MEAS_WNC', 'MEAS_TOW', 'MEAS_CHANNEL', 'MEAS_SVID', 'MEAS_FREQNR', 'MEAS_ANTENNA', 'MEAS_SIGNALTYPE', 'MEAS_CODE', 'MEAS_CARRIER', 'MEAS_DOPPLER', 'MEAS_CN0', 'MEAS_LOCKTIME', 'MEAS_HALFCYCLEAMBIGUITY', 'MEAS_SMOOTHING')
colFmtMeasEpoch = 'u2,f8,u1,u1,u1,u1,u1,f8,f8,f8,f4,u4,u1,u1'

# names and format for MeasExtra
colNamesMeasExtra = ('EXTRA_WNC', 'EXTRA_TOW', 'EXTRA_CHANNEL', 'EXTRA_ANTENNA', 'EXTRA_SIGNALTYPE', 'EXTRA_LOCKTIME', 'EXTRA_CODEVARIANCE', 'EXTRA_CARRIERVARIANCE', 'EXTRA_DOPPLERVARIANCE', 'EXTRA_MPCORR', 'EXTRA_SMOOTHINGCORR', 'EXTRA_CUMMLOSSCONT')
colFmtMeasExtra = 'u2,f8,u1,u1,u1,u2,f4,f4,f4,i2,i2,u1'

# names and format for SatVisibility_1
colNamesSatVisibility = ('VISIBILITY_WNC', 'VISIBILITY_TOW', 'VISIBILITY_SVID', 'VISIBILITY_FREQNR', 'VISIBILITY_SOURCE', 'VISIBILITY_AZIMUTH', 'VISIBILITY_ELEVATION', 'VISIBILITY_RISESET',)
colFmtSatVisibility = 'u2,f8,u1,u1,u1,u2,i2,u1'

# names and format for DOP
colNamesDOP = ('DOP_WNC', 'DOP_TOW', 'DOP_NrSV', 'DOP_PDOP', 'DOP_VDOP', 'DOP_HDOP', 'DOP_TDOP', 'DOP_HPL', 'DOP_VPL')
colFmtDOP = 'u2,f8,u1,f4,f4,f4,f4,f4,f4'

# names and format for PosGeod
colNamesPosGeod = ('GEOD_WNC', 'GEOD_TOW', 'GEOD_MODE', 'GEOD_2D/3D', 'GEOD_Error', 'GEOD_NrSV', 'GEOD_Latitude', 'GEOD_Longitude', 'GEOD_Height', 'GEOD_Vn', 'GEOD_Ve', 'GEOD_Vu', 'GEOD_ClockBias', 'GEOD_ClockDrift', 'GEOD_ReferenceID', 'GEOD_MeanCorrAge', 'GEOD_NrBases', 'GEOD_Undulation', 'GEOD_COG', 'GEOD_Datum', 'GEOD_TimeSystem', 'GEOD_SignalInfo', 'GEOD_WACorrInfo', 'GEOD_AlertFlag', 'GEOD_AutoBase')
colFmtPosGeod = 'u2,f8,u1,u1,u1,u1,f8,f8,f8,f8,f8,f8,f8,f8,u2,u2,u2,f4,f4,u1,u1,u4,u1,u1,u1'

# names and format for ChannelStatus
colNamesChannelStatus = ('CHST_WNC','CHST_TOW','CHST_RxChannel','CHST_SVID','CHST_FreqNr','CHST_HealthStatus','CHST_Azimuth','CHST_Elevation','CHST_RiseSet','CHST_Antenna','CHST_TrackingStatus','CHST_PVTStatus','CHST_PVTInfo')
colFmtChannelStatus = 'u2,f8,u1,u1,u1,u2,u2,i1,u1,u1,u2,u2,u2'


def svPRN(prnSSN):
    """
    svPRN calculates the official PRN number of a SV based on the prn assigned by SSN

    Parameters:
        prnSSN: prn number used by SSN
                1 - 37 : PRN number of a GPS satellite
                38 - 61 : slot number of a GLONASS satellite with an offset of 37
                71 - 102 : PRN number of a GALILEO satellite with an offset of 70
                120 - 138 : PRN number of an SBAS satellite

    Returns:
        gnssSystem: the system the SV belongs to
        gnssSystemShort: abbreviation of GNSS system satellite belongs to
        gnssPRN: is the official used prn
    """
    if prnSSN in range(1, 38):
        return ('GPS', 'G', prnSSN)
    elif prnSSN in range(38, 62):
        return ('GLO', 'R', prnSSN-37)
    elif prnSSN in range(71, 103):
        return ('GAL', 'E', prnSSN-70)
    elif prnSSN in range(120, 139):
        return ('SBAS', 'S', prnSSN)
    else:
        return ('None', 'N', '0')

    # for testing out
    # for gnssSignal in ssnConstants.GNSSSignals:
    #     print 'GNSSSignals = %s' % ssnConstants.GNSSSignals[gnssSignal]

    # for prn in range(9, 100, 10):
    #     gnssSyst, gnssPRN = ssnConstants.svPRN(prn)
    #     print 'prn = %d: System %s - PRN %d' % (prn, gnssSyst, gnssPRN)
    # sys.exit(6)
