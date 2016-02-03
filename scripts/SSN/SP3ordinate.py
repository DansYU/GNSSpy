#!/usr/bin/env python

import sys
import os
import SP3get
import datetime
import numpy as np
import matplotlib.pyplot as plt


def getlagrange(nrSV, WEEK, DAY):

    # nrSV = 'E11'
    print nrSV
    if DAY == 0:
        DIR0 = SP3get.getSP3(WEEK-1, str(WEEK) + '6')
        DIR1 = SP3get.getSP3(WEEK, str(WEEK) + str(DAY))
        DIR2 = SP3get.getSP3(WEEK, str(WEEK) + str(DAY+1))
    elif DAY == 6:
        DIR0 = SP3get.getSP3(WEEK, str(WEEK) + str(DAY-1))
        DIR1 = SP3get.getSP3(WEEK, str(WEEK) + str(DAY))
        DIR2 = SP3get.getSP3(WEEK+1, 0)
    else:
        DIR0 = SP3get.getSP3(WEEK, str(WEEK) + str(DAY-1))
        DIR1 = SP3get.getSP3(WEEK, str(WEEK) + str(DAY))
        DIR2 = SP3get.getSP3(WEEK, str(WEEK) + str(DAY+1))

    # DIR0 = SP3get.getSP3(1841, 18410)
    # DIR1 = SP3get.getSP3(1841, 18411)
    # DIR2 = SP3get.getSP3(1841, 18412)

    # Extract Time and Ordinate information
    time = []
    sat = []

    with open(DIR0, 'rb') as f:
        for line in f:
            if line.startswith('*  '):
                time.append(line.split())
            if line.startswith('P' + nrSV):
                sat.append(line.split())
    count1 = 1
    count2 = 1

    with open(DIR1, 'rb') as f:
        for line in f:
            if line.startswith('*  '):
                time.append(line.split())
                if count1 == 1:
                    time.pop()
                count1 += 1
            if line.startswith('P' + nrSV):
                sat.append(line.split())
                if count2 == 1:
                    sat.pop()
                count2 += 1
    count1 = 1
    count2 = 1

    with open(DIR2, 'rb') as f:
        for line in f:
            if line.startswith('*  '):
                time.append(line.split())
                if count1 == 1:
                    time.pop()
                count1 += 1
            if line.startswith('P' + nrSV):
                sat.append(line.split())
                if count2 == 1:
                    sat.pop()
                count2 += 1

    if not len(time) == len(sat):
        print 'SP3 importation error'
        exit()

    # print time[0][1], time[1]
    TIME = []
    for count in range(0, len(time)):
        TIME.append(datetime.datetime(int(time[count][1]), int(time[count][2]),
                                      int(time[count][3]), int(time[count][4]),
                                      int(time[count][5]), int(float(time[count][6]))))

    # a = np.matrix([[1, (-4), (-4)**2, (-4)**3, (-4)**4, (-4)**5, (-4)**6, (-4)**7, (-4)**8], [1, (-3), (-3)**2, (-3)**3, (-3)**4, (-3)**5, (-3)**6, (-3)**7, (-3)**8], [1, (-2), (-2)**2, (-2)**3, (-2)**4, (-2)**5, (-2)**6, (-2)**7, (-2)**8], [1, (-1), (-1)**2, (-1)**3, (-1)**4, (-1)**5, (-1)**6, (-1)**7, (-1)**8], [1, 0, 0**2, 0**3, 0**4, 0**5, 0**6, 0**7, 0**8], [1, 1, 1**2, 1**3, 1**4, 1**5, 1**6, 1**7, 1**8], [1, 2, 2**2, 2**3, 2**4, 2**5, 2**6, 2**7, 2**8], [1, 3, 3**2, 3**3, 3**4, 3**5, 3**6, 3**7, 3**8], [1, 4, 4**2, 4**3, 4**4, 4**5, 4**6, 4**7, 4**8]])

    T = np.matrix([[-2.22044605e-16, 1.77635684e-15, 0.00000000e+00,
                    1.42108547e-14, 1.00000000e+00, -3.55271368e-15,
                    0.00000000e+00, 0.00000000e+00, 0.00000000e+00],
                   [3.57142857e-03, -3.80952381e-02, 2.00000000e-01,
                    -8.00000000e-01, 3.51306286e-16, 8.00000000e-01,
                    -2.00000000e-01, 3.80952381e-02, -3.57142857e-03],
                   [-8.92857143e-04, 1.26984127e-02, -1.00000000e-01,
                    8.00000000e-01, -1.42361111e+00, 8.00000000e-01,
                    -1.00000000e-01, 1.26984127e-02, -8.92857143e-04],
                   [-4.86111111e-03, 5.00000000e-02, -2.34722222e-01,
                    3.38888889e-01, -1.48029737e-16, -3.38888889e-01,
                    2.34722222e-01, -5.00000000e-02, 4.86111111e-03],
                   [1.21527778e-03, -1.66666667e-02, 1.17361111e-01,
                    -3.38888889e-01, 4.73958333e-01, -3.38888889e-01,
                    1.17361111e-01, -1.66666667e-02, 1.21527778e-03],
                   [1.38888889e-03, -1.25000000e-02, 3.61111111e-02,
                    -4.02777778e-02, -6.09218364e-18, 4.02777778e-02,
                    -3.61111111e-02, 1.25000000e-02, -1.38888889e-03],
                   [-3.47222222e-04, 4.16666667e-03, -1.80555556e-02,
                    4.02777778e-02, -5.20833333e-02, 4.02777778e-02,
                    -1.80555556e-02, 4.16666667e-03, -3.47222222e-04],
                   [-9.92063492e-05, 5.95238095e-04, -1.38888889e-03,
                    1.38888889e-03, 8.73234500e-19, -1.38888889e-03,
                    1.38888889e-03, -5.95238095e-04, 9.92063492e-05],
                   [2.48015873e-05, -1.98412698e-04, 6.94444444e-04,
                    -1.38888889e-03, 1.73611111e-03, -1.38888889e-03,
                    6.94444444e-04, -1.98412698e-04, 2.48015873e-05]])

    satAR = np.array(sat)
    X = np.array(satAR[:, 1], dtype=np.float32)
    Y = np.array(satAR[:, 2], dtype=np.float32)
    Z = np.array(satAR[:, 3], dtype=np.float32)
    COEF = []
    # print np.shape(np.asmatrix(np.transpose([X[0:9], Y[0:9], Z[0:9]])))
    for count in range(0, len(X)-9):
        C = np.asmatrix(np.transpose([X[count:count+9], Y[count:count+9], Z[count:count+9]]))
        COEF.append(np.dot(T, C))

    return COEF, sat, TIME
    # return COEF, sat, TIME
    # print type(T)
    # print type(C)
    # print len(COEF)
    # print COEF[0][:, 0]

    # test of interpolation
    # OUT = []
    # # COEF = np.dot(T, C)
    # for count in range(0, 9):
    #     t = count-4
    #     OUT.append(COEF[0][0, 0]*t**0 + COEF[0][1, 0]*t**1 + COEF[0][2, 0]*t**2 + COEF[0][3, 0]*t**3
    #                + COEF[0][4, 0]*t**4 + COEF[0][5, 0]*t**5 + COEF[0][6, 0]*t**6 + COEF[0][7, 0]*t**7
    #                + COEF[0][8, 0]*t**8)
    # print len(OUT)
    # plt.plot([-4, -3, -2, -1, 0, 1, 2, 3, 4], X[0:9])
    # plt.plot([-4, -3, -2, -1, 0, 1, 2, 3, 4], OUT)
    # plt.show()
