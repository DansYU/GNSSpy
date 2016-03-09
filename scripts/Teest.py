import numpy as np
import csv
import string

if __name__ == "__main__":
	# colNamesMeasEpoch = ('MEAS_WNC', 'MEAS_TOW', 'MEAS_CHANNEL', 'MEAS_SVID', 'MEAS_FREQNR', 'MEAS_ANTENNA', 'MEAS_SIGNALTYPE', 'MEAS_CODE', 'MEAS_CARRIER', 'MEAS_DOPPLER', 'MEAS_CN0', 'MEAS_LOCKTIME', 'MEAS_HALFCYCLEAMBIGUITY', 'MEAS_SMOOTHING')
	# colFmtMeasEpoch = 'u2,f8,u1,u1,u1,u1,u1,f8,f8,f8,f4,u4,u1,u1'
	f = open('ASSN337Z.15__MeasEpoch_2Test.stf', 'r')
	filedata = f.read()
	f.close()
	newdata = filedata.replace('1.#IND', '').replace('-1.#INF', '')
	f = open('ASSN337Z.15__MeasEpoch_2Test.stf', 'w')
	f.write(newdata)
	f.close()
	# measData = np.genfromtxt('ASSN337Z.15__MeasEpoch_2Test.stf', delimiter=",", dtype=colFmtMeasEpoch, names=colNamesMeasEpoch, usecols=[0, 7, 8])