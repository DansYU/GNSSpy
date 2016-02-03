#!/usr/bin/env python
#
# variety.py -- Make a variety of plots in a single figure

from numpy import *
import matplotlib.pyplot as plt
import sys


def addSubPlot(figNr):
    plt.subplot(2, 2, figNr)
    x = linspace(0,10,101)
    y = exp(x)
    plt.semilogy(x,y,color='m',linewidth=2)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("y = exp(x)")


fg = plt.figure(figsize=(10,8))
adj = plt.subplots_adjust(hspace=0.4,wspace=0.4)

for i in range(1, 5):
    print ('i = %d' % i)
    addSubPlot(i)

plt.show()
sys.exit(0)

sp = plt.subplot(2,2,1)
x = linspace(0,10,101)
y = exp(x)
l1 = plt.semilogy(x,y,color='m',linewidth=2)
lx = plt.xlabel("x")
ly = plt.ylabel("y")
tl = plt.title("y = exp(x)")

sp = plt.subplot(2,2,2)
print x
y = x**-1.67
l1 = plt.loglog(x,y)
lx = plt.xlabel("x")
ly = plt.ylabel("y")
tl = plt.title("y = x$^{-5/3}$")

sp = plt.subplot(2,2,3)
x = arange(1001)
y = mod(x,2.87)
l1 = plt.hist(y, color='r', rwidth=0.8)
lx = plt.xlabel("y")
ly = plt.ylabel("num(y)")
tl = plt.title("y = mod(arange(1001),2.87)")

sp = plt.subplot(2,2,4)
l1 = plt.hist(y,bins=25,normed=True,cumulative=True,orientation='horizontal')
lx = plt.xlabel("num(y)")
ly = plt.ylabel("y")
tl = plt.title("cumulative normed y")

plt.show()
