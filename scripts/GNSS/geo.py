#!/usr/bin/env python

# See https://github.com/GAVLab/fhwa2_viz/blob/master/fhwa2_gui/src/util.py
"""
Container for general Geographic functions
Functions:
    deg2rad
    rad2deg
    euclideanDistance
    gpsWeekCheck
    keplerE
"""

# Import required packages
from math import sqrt, pi, sin


def deg2rad(deg):
    """
    Converts degrees to radians
    """
    return deg * pi / 180


def rad2deg(rad):
    """
    Converts radians to degrees
    """
    return rad * 180 / pi


def isEven(num):
    """
    Boolean function returning true if num is even, false if not
    """
    return num % 2 == 0


def euclideanDistance(data, dataRef=None):
    """
    Calculates the Euclidian distance between the given data and zero.
    This works out to be equivalent to the distance between two points if their
    difference is given as the input
    """
    total = 0
    for index in range(len(data)):
        if dataRef is None:
            total += data[index]**2
        else:
            total += (data[index] - dataRef[index])**2
    return sqrt(total)


def gpsWeekCheck(t):
    """
    Makes sure the time is in the interval [-302400 302400] seconds, which
    corresponds to number of seconds in the GPS week
    """
    if t > 302400.:
        t = t - 604800.
    elif t < -302400.:
        t = t + 604800.
    return t


def keplerE(M_k, ecc, tolerance=1e-12):
    """
    Iteratively calculates E_k using Kepler's equation:
    E_k = M_k + ecc * sin(E_k)
    """
    E_k = M_k
    E_0 = E_k + tolerance * 10.
    while abs(E_k - E_0) > tolerance:
        E_0 = E_k
        E_k = M_k + ecc * sin(E_k)
    return E_k
